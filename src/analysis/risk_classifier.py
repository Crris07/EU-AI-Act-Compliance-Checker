def normalize_risk_level(value: str) -> str:
    normalized = value.strip().lower()
    if normalized in {"high", "medium", "low"}:
        return normalized.title()
    return "Medium"

