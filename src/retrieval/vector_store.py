import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore

from src.config import settings


def get_chroma_client():
    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(settings.chroma_dir))


def get_chroma_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(settings.chroma_collection)


def reset_chroma_collection():
    client = get_chroma_client()
    existing_names = [collection.name for collection in client.list_collections()]
    if settings.chroma_collection in existing_names:
        client.delete_collection(settings.chroma_collection)
    return client.get_or_create_collection(settings.chroma_collection)


def get_chroma_vector_store() -> ChromaVectorStore:
    return ChromaVectorStore(chroma_collection=get_chroma_collection())


def get_fresh_chroma_vector_store() -> ChromaVectorStore:
    return ChromaVectorStore(chroma_collection=reset_chroma_collection())
