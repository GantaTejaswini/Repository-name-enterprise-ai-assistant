from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.dependencies import get_db
from app.core.elasticsearch import es_client
from app.core.rbac import require_role
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import (
    DocumentListResponse,
    DocumentResponse,
)
from app.services.audit_service import AuditService
from app.services.document_service import DocumentService


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

INDEX_NAME = "document_chunks"

MAX_FILE_SIZE = 10 * 1024 * 1024


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"],
)

document_service = DocumentService()


def get_embedding_model(request: Request):
    embedding_model = getattr(
        request.app.state,
        "embedding_model",
        None,
    )

    if embedding_model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Embedding model is not ready",
        )

    return embedding_model


def build_document_response(
    document,
) -> DocumentResponse:

    return DocumentResponse(
        id=document.id,
        tenant_id=document.tenant_id,
        filename=document.filename,
        status=document.status,
        created_at=document.created_at.isoformat(),
    )


@router.get(
    "/",
    response_model=DocumentListResponse,
)
async def list_documents(
    current_user: dict = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):

    repository = DocumentRepository(db)

    documents = await repository.get_all(
        tenant_id=current_user["tenant_id"]
    )

    document_responses = [
        build_document_response(document)
        for document in documents
    ]

    return DocumentListResponse(
        documents=document_responses,
        total=len(document_responses),
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
async def get_document(
    document_id: str,
    current_user: dict = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):

    repository = DocumentRepository(db)

    document = await repository.get_by_id(
        document_id=document_id,
        tenant_id=current_user["tenant_id"],
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return build_document_response(document)


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_document(
    document_id: str,
    current_user: dict = Depends(
        require_role("admin")
    ),
    db: AsyncSession = Depends(get_db),
):

    repository = DocumentRepository(db)

    document = await repository.get_by_id(
        document_id=document_id,
        tenant_id=current_user["tenant_id"],
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    filename = document.filename

    try:
        await es_client.delete_by_query(
            index=INDEX_NAME,
            query={
                "bool": {
                    "must": [
                        {
                            "term": {
                                "document_id": document.id
                            }
                        },
                        {
                            "term": {
                                "tenant_id": current_user[
                                    "tenant_id"
                                ]
                            }
                        },
                    ]
                }
            },
            conflicts="proceed",
            refresh=True,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Failed to delete document "
                "from Elasticsearch"
            ),
        ) from exc

    deleted_document = await repository.delete(
        document_id=document.id,
        tenant_id=current_user["tenant_id"],
    )

    if deleted_document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    await AuditService.log(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"],
        action="document_deleted",
        resource_type="document",
        resource_id=document.id,
        details=(
            f"Document '{filename}' "
            "deleted successfully."
        ),
    )

    return None


@router.post(
    "/upload",
    response_model=DocumentResponse,
)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    current_user: dict = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    safe_filename = Path(
        file.filename
    ).name

    if not safe_filename.lower().endswith(
        ".pdf"
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported",
        )

    if file.content_type not in {
        "application/pdf",
        "application/octet-stream",
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid PDF content type",
        )

    file_content = await file.read()

    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=(
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            ),
            detail=(
                "PDF file exceeds the maximum "
                "allowed size of 10 MB"
            ),
        )

    if not file_content.startswith(
        b"%PDF-"
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Uploaded file does not contain "
                "a valid PDF signature"
            ),
        )

    document_id = str(uuid4())

    stored_filename = (
        f"{document_id}_{safe_filename}"
    )

    file_path = UPLOAD_DIR / stored_filename

    file_path.write_bytes(file_content)

    repository = DocumentRepository(db)

    document = await repository.create(
        tenant_id=current_user["tenant_id"],
        filename=safe_filename,
    )

    try:

        pages = document_service.extract_text(
            str(file_path)
        )

        chunks = document_service.chunk_text(
            pages
        )

        if not chunks:

            await repository.update_status(
                document_id=document.id,
                tenant_id=current_user[
                    "tenant_id"
                ],
                status="failed",
            )

            await AuditService.log(
                db=db,
                tenant_id=current_user[
                    "tenant_id"
                ],
                user_id=current_user["user_id"],
                action="document_ingestion_failed",
                resource_type="document",
                resource_id=document.id,
                details=(
                    f"Document '{safe_filename}' "
                    "contains no extractable text."
                ),
            )

            raise HTTPException(
                status_code=(
                    status.HTTP_422_UNPROCESSABLE_ENTITY
                ),
                detail=(
                    "No extractable text found "
                    "in the PDF"
                ),
            )

        print(
            f"Extracted {len(pages)} pages "
            f"and created {len(chunks)} chunks."
        )

        document_chunks = (
            await repository.create_chunks(
                document_id=document.id,
                chunks=chunks,
            )
        )

        print(
            f"Stored {len(document_chunks)} "
            "chunks in PostgreSQL."
        )

        model = get_embedding_model(
            request
        )

        print(
            "Generating embeddings and "
            "indexing into Elasticsearch..."
        )

        for index, document_chunk in enumerate(
            document_chunks,
            start=1,
        ):

            print(
                f"Embedding chunk "
                f"{index}/{len(document_chunks)}..."
            )

            embedding = model.encode(
                document_chunk.content,
                normalize_embeddings=False,
            )

            document_body = {
                "document_id": document.id,
                "tenant_id": document.tenant_id,
                "filename": document.filename,
                "page_number": (
                    document_chunk.page_number
                ),
                "chunk_id": (
                    document_chunk.chunk_id
                ),
                "content": (
                    document_chunk.content
                ),
                "embedding": embedding.tolist(),
                "metadata": {
                    "source": "uploaded_pdf",
                    "document_type": "pdf",
                },
            }

            await es_client.index(
                index=INDEX_NAME,
                id=document_chunk.id,
                document=document_body,
            )

        await es_client.indices.refresh(
            index=INDEX_NAME
        )

        print(
            f"Indexed {len(document_chunks)} "
            "chunks into Elasticsearch."
        )

        await repository.update_status(
            document_id=document.id,
            tenant_id=current_user[
                "tenant_id"
            ],
            status="processed",
        )

        await AuditService.log(
            db=db,
            tenant_id=current_user[
                "tenant_id"
            ],
            user_id=current_user["user_id"],
            action="document_ingested",
            resource_type="document",
            resource_id=document.id,
            details=(
                f"Document '{safe_filename}' "
                f"processed successfully with "
                f"{len(document_chunks)} chunks."
            ),
        )

        print(
            "DOCUMENT INGESTION COMPLETE"
        )

    except HTTPException:
        raise

    except Exception as exc:

        print(
            "Document ingestion failed. "
            "Starting cleanup..."
        )

        # Remove any Elasticsearch chunks that
        # may have been indexed before the failure.
        try:

            await es_client.delete_by_query(
                index=INDEX_NAME,
                query={
                    "bool": {
                        "must": [
                            {
                                "term": {
                                    "document_id": (
                                        document.id
                                    )
                                }
                            },
                            {
                                "term": {
                                    "tenant_id": (
                                        current_user[
                                            "tenant_id"
                                        ]
                                    )
                                }
                            },
                        ]
                    }
                },
                conflicts="proceed",
                refresh=True,
            )

            print(
                "Elasticsearch cleanup complete."
            )

        except Exception as cleanup_exc:

            print(
                "Elasticsearch cleanup failed: "
                f"{cleanup_exc}"
            )

        # Remove the PostgreSQL document and
        # all associated PostgreSQL chunks.
        try:

            await repository.delete(
                document_id=document.id,
                tenant_id=current_user[
                    "tenant_id"
                ],
            )

            print(
                "PostgreSQL cleanup complete."
            )

        except Exception as cleanup_exc:

            print(
                "PostgreSQL cleanup failed: "
                f"{cleanup_exc}"
            )

        try:

            await AuditService.log(
                db=db,
                tenant_id=current_user[
                    "tenant_id"
                ],
                user_id=current_user["user_id"],
                action="document_ingestion_failed",
                resource_type="document",
                resource_id=document.id,
                details=(
                    f"Document '{safe_filename}' "
                    f"ingestion failed and cleanup "
                    f"was attempted. Error: {exc}"
                ),
            )

        except Exception:
            pass

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Document processing failed.",
        ) from exc

    finally:

        try:

            if file_path.exists():
                file_path.unlink()

        except Exception as cleanup_exc:

            print(
                "Uploaded file cleanup failed: "
                f"{cleanup_exc}"
            )

    return DocumentResponse(
        id=document.id,
        tenant_id=document.tenant_id,
        filename=document.filename,
        status=document.status,
        created_at=document.created_at.isoformat(),
    )