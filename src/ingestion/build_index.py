from pathlib import Path

from llama_index.core import Document, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from src.config import settings
from src.ingestion.chunk_regulations import chunk_eu_ai_act
from src.ingestion.load_documents import load_source_document, save_url_html
from src.retrieval.vector_store import get_fresh_chroma_vector_store


def build_semantic_nodes(documents: list[Document], embed_model: HuggingFaceEmbedding):
    splitter = SemanticSplitterNodeParser(
        embed_model=embed_model,
        breakpoint_percentile_threshold=95,
        buffer_size=1,
    )
    nodes = splitter.get_nodes_from_documents(documents)

    section_counts: dict[str, int] = {}
    for node in nodes:
        section_number = node.metadata.get("section_number", "Unknown")
        section_counts[section_number] = section_counts.get(section_number, 0) + 1
        node.metadata["parent_section_number"] = section_number
        node.metadata["semantic_chunk_index"] = section_counts[section_number]
        node.metadata["chunking_strategy"] = "article_annex_semantic"

    return nodes


def build_eu_ai_act_index(source_path: Path) -> int:
    text = load_source_document(source_path)
    chunks = chunk_eu_ai_act(text)
    documents = [
        Document(text=chunk.text, metadata=chunk.metadata)
        for chunk in chunks
    ]

    embed_model = HuggingFaceEmbedding(model_name=settings.embed_model)
    nodes = build_semantic_nodes(documents, embed_model)
    vector_store = get_fresh_chroma_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex(
        nodes,
        storage_context=storage_context,
        embed_model=embed_model,
    )
    return len(nodes)


def ingest_eu_ai_act_url(url: str, raw_output_path: Path | str) -> int:
    saved_path = save_url_html(url, Path(raw_output_path))
    return build_eu_ai_act_index(saved_path)
