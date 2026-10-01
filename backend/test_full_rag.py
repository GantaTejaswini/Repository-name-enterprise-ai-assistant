import asyncio

from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer

from app.core.elasticsearch import es_client
from app.services.rag_service import RAGService


EMBEDDING_MODEL_NAME = (
    "nvidia/llama-nemotron-embed-1b-v2"
)

LLM_MODEL_NAME = (
    "ibm-granite/granite-3.3-8b-instruct"
)

TENANT_ID = (
    "9984bc36-f841-44bd-899a-2a62c755f5ec"
)

QUESTION = "What is Python?"


async def main():

    print("=" * 80)
    print("FULL RAG PIPELINE TEST")
    print("=" * 80)

    try:

        print()
        print("STEP 1: Loading Nemotron embedding model...")

        embedding_model = SentenceTransformer(
            EMBEDDING_MODEL_NAME,
            trust_remote_code=True,
        )

        print(
            "Nemotron embedding model loaded."
        )

        print()
        print("STEP 2: Loading Granite tokenizer...")

        tokenizer = AutoTokenizer.from_pretrained(
            LLM_MODEL_NAME
        )

        print(
            "Granite tokenizer loaded."
        )

        print()
        print("STEP 3: Loading Granite LLM...")

        llm_model = AutoModelForCausalLM.from_pretrained(
            LLM_MODEL_NAME,
            torch_dtype="auto",
        )

        print(
            "Granite LLM loaded."
        )

        print()
        print("STEP 4: Creating RAG service...")

        rag_service = RAGService(
            tokenizer=tokenizer,
            model=llm_model,
            embedding_model=embedding_model,
        )

        print(
            "RAG service created."
        )

        print()
        print("=" * 80)
        print("STEP 5: RUNNING RAG")
        print("=" * 80)

        print()
        print(
            f"Question: {QUESTION}"
        )

        result = await rag_service.ask(
            question=QUESTION,
            tenant_id=TENANT_ID,
            top_k=2,
        )

        print()
        print("=" * 80)
        print("RAG ANSWER")
        print("=" * 80)

        print()
        print(
            result["answer"]
        )

        print()
        print("=" * 80)
        print("SOURCES")
        print("=" * 80)

        for index, source in enumerate(
            result["sources"],
            start=1,
        ):

            print()
            print(
                f"SOURCE {index}"
            )

            print("-" * 80)

            print(
                f"Document : "
                f"{source['document']}"
            )

            print(
                f"Page     : "
                f"{source['page']}"
            )

            print(
                f"Chunk ID  : "
                f"{source['chunk_id']}"
            )

            print(
                f"RRF      : "
                f"{source['rrf_score']}"
            )

            print()
            print(
                "Content preview:"
            )

            print(
                source["content"][:500]
            )

        print()
        print("=" * 80)
        print(
            "FULL RAG PIPELINE TEST COMPLETE"
        )
        print("=" * 80)

    finally:

        await es_client.close()


if __name__ == "__main__":
    asyncio.run(main())