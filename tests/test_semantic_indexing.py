from llama_index.core import Document
from llama_index.core.embeddings import MockEmbedding

from src.ingestion.build_index import build_semantic_nodes


def test_build_semantic_nodes_preserves_parent_metadata():
    documents = [
        Document(
            text="Article 9\nRisk management system.\nProviders shall establish controls.",
            metadata={
                "section_number": "Article 9",
                "section_type": "Article",
                "source_url": "https://example.com",
            },
        )
    ]

    nodes = build_semantic_nodes(documents, MockEmbedding(embed_dim=8))

    assert nodes
    assert nodes[0].metadata["section_number"] == "Article 9"
    assert nodes[0].metadata["parent_section_number"] == "Article 9"
    assert nodes[0].metadata["chunking_strategy"] == "article_annex_semantic"
