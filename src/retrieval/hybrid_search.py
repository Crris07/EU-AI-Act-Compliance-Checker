import re
from dataclasses import dataclass

from llama_index.core.schema import NodeWithScore, TextNode
from rank_bm25 import BM25Okapi

from src.config import settings
from src.retrieval.retriever import semantic_retrieve
from src.retrieval.vector_store import get_chroma_collection


TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9]+")


@dataclass(frozen=True)
class CorpusItem:
    id: str
    text: str
    metadata: dict


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def load_corpus() -> list[CorpusItem]:
    collection = get_chroma_collection()
    results = collection.get(include=["documents", "metadatas"])
    ids = results.get("ids", [])
    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])

    return [
        CorpusItem(id=item_id, text=document or "", metadata=metadata or {})
        for item_id, document, metadata in zip(ids, documents, metadatas)
        if document
    ]


def bm25_retrieve(query: str, top_k: int | None = None) -> list[NodeWithScore]:
    corpus = load_corpus()
    if not corpus:
        return []

    limit = top_k or settings.top_k
    tokenized_corpus = [tokenize(item.text) for item in corpus]
    bm25 = BM25Okapi(tokenized_corpus)
    scores = bm25.get_scores(tokenize(query))

    ranked = sorted(
        zip(corpus, scores),
        key=lambda item: item[1],
        reverse=True,
    )[:limit]

    return [
        NodeWithScore(
            node=TextNode(
                id_=item.id,
                text=item.text,
                metadata=item.metadata,
            ),
            score=float(score),
        )
        for item, score in ranked
        if score > 0
    ]


def hybrid_search(query: str, top_k: int | None = None) -> list[NodeWithScore]:
    """Fuse semantic and BM25 retrieval while preserving source metadata."""
    limit = top_k or settings.top_k
    semantic_results = semantic_retrieve(query, top_k=limit * 2)
    bm25_results = bm25_retrieve(query, top_k=limit * 2)

    fused: dict[str, NodeWithScore] = {}
    for rank, result in enumerate(semantic_results):
        node_id = result.node.node_id
        score = 1.0 / (rank + 1)
        fused[node_id] = NodeWithScore(node=result.node, score=score)

    for rank, result in enumerate(bm25_results):
        node_id = result.node.node_id
        score = (1.0 / (rank + 1)) + (fused[node_id].score if node_id in fused else 0.0)
        fused[node_id] = NodeWithScore(node=result.node, score=score)

    return sorted(fused.values(), key=lambda result: result.score or 0.0, reverse=True)[:limit]
