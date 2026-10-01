from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from sqlalchemy import text
from transformers import AutoModelForCausalLM, AutoTokenizer

from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.database_test import router as database_test_router
from app.api.diagnostics import router as diagnostics_router
from app.api.document import router as document_router
from app.api.models import router as models_router
from app.api.retrieval import router as retrieval_router
from app.api.tenant import router as tenant_router
from app.api.user import router as user_router
from app.core.config import get_cors_origins, settings
from app.core.database import engine
from app.core.elasticsearch import es_client
from app.core.exception_handlers import global_exception_handler
from app.core.logging_config import configure_logging
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService


EMBEDDING_MODEL_NAME = (
    "nvidia/llama-nemotron-embed-1b-v2"
)

LLM_MODEL_NAME = (
    "ibm-granite/granite-3.3-8b-instruct"
)


configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("=" * 80)
    print("STARTING ENTERPRISE AI ASSISTANT")
    print("=" * 80)
    print()

    llm_provider = (
        settings.llm_provider
        .lower()
        .strip()
    )

    print(
        f"Configured LLM provider: {llm_provider}"
    )
    print()

    print(
        "Loading Nemotron embedding model..."
    )

    embedding_model = SentenceTransformer(
        EMBEDDING_MODEL_NAME,
        trust_remote_code=True,
    )

    app.state.embedding_model = embedding_model

    print(
        "Nemotron embedding model loaded!"
    )
    print()

    tokenizer = None
    llm_model = None

    if llm_provider == "granite":

        print(
            "Loading Granite tokenizer..."
        )

        tokenizer = AutoTokenizer.from_pretrained(
            LLM_MODEL_NAME
        )

        print(
            "Granite tokenizer loaded!"
        )
        print()

        print(
            "Loading Granite LLM..."
        )

        llm_model = AutoModelForCausalLM.from_pretrained(
            LLM_MODEL_NAME,
            torch_dtype="auto",
        )

        print(
            "Granite LLM loaded!"
        )
        print()

    elif llm_provider == "extractive":

        print(
            "Using CPU-friendly extractive "
            "development provider."
        )

        print(
            "Granite will not be loaded."
        )

        print()

    else:

        raise RuntimeError(
            "Unsupported LLM_PROVIDER: "
            f"{llm_provider}"
        )

    llm_service = LLMService(
        provider=llm_provider,
        tokenizer=tokenizer,
        model=llm_model,
    )

    app.state.llm_service = llm_service

    print(
        "Creating RAG service..."
    )

    app.state.rag_service = RAGService(
        llm_service=llm_service,
        embedding_model=embedding_model,
    )

    print()
    print(
        "RAG service ready!"
    )

    print(
        "Enterprise AI Assistant started."
    )

    yield

    print()
    print(
        "Shutting down Enterprise AI Assistant..."
    )

    await es_client.close()
    await engine.dispose()

    print(
        "Shutdown complete."
    )


app = FastAPI(
    title="Enterprise AI Assistant",
    version="0.1.0",
    lifespan=lifespan,
)


app.add_exception_handler(
    Exception,
    global_exception_handler,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(
    SecurityHeadersMiddleware
)

app.add_middleware(
    RequestIDMiddleware
)

app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=60,
)


app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(database_test_router)
app.include_router(diagnostics_router)
app.include_router(document_router)
app.include_router(models_router)
app.include_router(retrieval_router)
app.include_router(tenant_router)
app.include_router(user_router)


@app.get("/")
async def root():

    return {
        "message": (
            "Enterprise AI Assistant API is running"
        )
    }


@app.get("/health")
async def health():

    postgres_status = "healthy"
    elasticsearch_status = "healthy"

    try:

        async with engine.connect() as conn:

            await conn.execute(
                text("SELECT 1")
            )

    except Exception:

        postgres_status = "unhealthy"

    try:

        await es_client.info()

    except Exception:

        elasticsearch_status = "unhealthy"

    overall_status = (
        "healthy"
        if (
            postgres_status == "healthy"
            and elasticsearch_status == "healthy"
        )
        else "unhealthy"
    )

    return {
        "status": overall_status,
        "postgresql": postgres_status,
        "elasticsearch": elasticsearch_status,
    }