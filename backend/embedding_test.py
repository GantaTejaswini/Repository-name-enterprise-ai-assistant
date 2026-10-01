from sentence_transformers import SentenceTransformer


MODEL_NAME = "nvidia/llama-nemotron-embed-1b-v2"


print("Loading embedding model...")

model = SentenceTransformer(
    MODEL_NAME,
    trust_remote_code=True,
)

print("Model loaded successfully!")


text = (
    "Enterprise AI assistants use retrieval augmented generation "
    "to retrieve relevant information from documents."
)

print("Generating embedding...")

embedding = model.encode(
    text,
    normalize_embeddings=False,
)

print("Embedding generated successfully!")
print("Embedding type:", type(embedding))
print("Embedding shape:", embedding.shape)
print("Embedding dimensions:", len(embedding))
print("First 10 values:", embedding[:10])