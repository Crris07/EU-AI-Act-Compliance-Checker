from src.retrieval.hybrid_search import tokenize


def test_tokenize_keeps_legal_numbers():
    assert tokenize("Article 6(2), Annex III, high-risk") == [
        "article",
        "6",
        "2",
        "annex",
        "iii",
        "high",
        "risk",
    ]
