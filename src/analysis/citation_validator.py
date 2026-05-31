def has_citation(text: str) -> bool:
    markers = ["Article", "Annex", "Regulation (EU) 2024/1689"]
    return any(marker in text for marker in markers)

