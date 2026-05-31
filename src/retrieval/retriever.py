from llama_index.core import VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from src.config import settings
from src.retrieval.vector_store import get_chroma_vector_store


def get_retriever(top_k: int | None = None):
    embed_model = HuggingFaceEmbedding(model_name=settings.embed_model)
    index = VectorStoreIndex.from_vector_store(
        vector_store=get_chroma_vector_store(),
        embed_model=embed_model,
    )
    return index.as_retriever(similarity_top_k=top_k or settings.top_k)


def semantic_retrieve(query: str, top_k: int | None = None):
    return get_retriever(top_k=top_k).retrieve(query)


def retrieve_clauses(query: str):
    from src.retrieval.hybrid_search import hybrid_search

    return hybrid_search(query)
