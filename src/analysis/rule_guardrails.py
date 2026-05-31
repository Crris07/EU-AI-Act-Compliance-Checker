from src.reporting.schemas import ComplianceFinding


BIOMETRIC_TERMS = {"biometric", "face", "facial", "identification", "cctv", "watchlist"}
PUBLIC_SPACE_TERMS = {"shopping mall", "mall", "public", "publicly accessible", "cctv"}
RECRUITMENT_TERMS = {"job", "candidate", "recruit", "interview", "cv", "employment", "worker", "shortlist"}


def text_has_any(text: str, terms: set[str]) -> bool:
    normalized = text.lower()
    return any(term in normalized for term in terms)


def source_for_clause(retrieved, clause: str):
    normalized_clause = clause.lower()
    for node in retrieved:
        label = (node.metadata.get("section_number") or node.metadata.get("article_number") or "").lower()
        if normalized_clause == label:
            return node
    return None


def build_finding(source, finding: str, risk_level: str, evidence: str, recommendation: str) -> ComplianceFinding:
    return ComplianceFinding(
        clause=source.metadata.get("section_number") or source.metadata.get("article_number") or "EU AI Act",
        source_type=source.metadata.get("section_type", "EU AI Act"),
        finding=finding,
        risk_level=risk_level,
        evidence=evidence,
        recommendation=recommendation,
        source_excerpt=source.get_content()[:1000],
        source_url=source.metadata.get("source_url"),
        retrieval_score=source.score,
    )


def deterministic_findings(description: str, retrieved) -> list[ComplianceFinding]:
    findings: list[ComplianceFinding] = []

    article_5 = source_for_clause(retrieved, "Article 5")
    annex_iii = source_for_clause(retrieved, "ANNEX III")

    if article_5 and text_has_any(description, BIOMETRIC_TERMS) and text_has_any(description, PUBLIC_SPACE_TERMS):
        findings.append(
            build_finding(
                source=article_5,
                finding="Possible prohibited or tightly restricted real-time biometric identification in a publicly accessible space.",
                risk_level="High",
                evidence=description[:180],
                recommendation="Pause deployment and assess whether any Article 5 exception applies before use.",
            )
        )

    if annex_iii and text_has_any(description, BIOMETRIC_TERMS):
        findings.append(
            build_finding(
                source=annex_iii,
                finding="The system may fall within high-risk biometric identification use cases listed in Annex III.",
                risk_level="High",
                evidence=description[:180],
                recommendation="Treat as high-risk unless legal review confirms an exclusion applies.",
            )
        )

    if annex_iii and text_has_any(description, RECRUITMENT_TERMS):
        findings.append(
            build_finding(
                source=annex_iii,
                finding="Recruitment or candidate-screening AI is likely a high-risk use case under Annex III.",
                risk_level="High",
                evidence=description[:180],
                recommendation="Apply high-risk AI controls before deployment, including oversight, documentation, and monitoring.",
            )
        )

    return findings
