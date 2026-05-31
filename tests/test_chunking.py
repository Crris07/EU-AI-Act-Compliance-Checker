from src.ingestion.chunk_regulations import chunk_eu_ai_act


def test_chunk_eu_ai_act_articles():
    text = "Article 1\nSubject matter\nSome text.\nArticle 2\nDefinitions\nMore text."

    chunks = chunk_eu_ai_act(text)

    assert len(chunks) == 2
    assert chunks[0].metadata["article_number"] == "Article 1"
    assert "Subject matter" in chunks[0].text


def test_chunk_eu_ai_act_does_not_treat_article_reference_as_header():
    text = "Article 6\nClassification rules\nText.\nANNEX III\nHigh-risk AI systems referred to in Article 6(2)\nEmployment systems."

    chunks = chunk_eu_ai_act(text)

    assert len(chunks) == 2
    assert chunks[0].metadata["section_number"] == "Article 6"
    assert chunks[1].metadata["section_number"] == "ANNEX III"
    assert chunks[1].metadata["section_type"] == "Annex"
