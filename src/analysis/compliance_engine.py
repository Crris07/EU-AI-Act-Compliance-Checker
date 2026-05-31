from src.analysis.llm_client import analyze_with_llm
from src.analysis.risk_classifier import normalize_risk_level
from src.analysis.rule_guardrails import deterministic_findings
from src.reporting.schemas import ComplianceFinding, ComplianceReport
from src.retrieval.retriever import retrieve_clauses


def get_clause_label(metadata: dict) -> str:
    return metadata.get("section_number") or metadata.get("article_number") or "EU AI Act"


def normalize_clause(value: str) -> str:
    return " ".join(value.lower().split())


def resolve_source(clause: str, source_lookup: dict[str, object]):
    normalized = normalize_clause(clause)
    for label, source in source_lookup.items():
        source_label = normalize_clause(label)
        if normalized == source_label or source_label in normalized or normalized in source_label:
            return source
    return None


def build_retrieval_fallback(description: str, retrieved, summary: str) -> ComplianceReport:
    findings = [
        ComplianceFinding(
            clause=get_clause_label(node.metadata),
            source_type=node.metadata.get("section_type", "EU AI Act"),
            finding="Potentially relevant EU AI Act obligation retrieved for review.",
            risk_level="Medium",
            evidence=description[:500],
            recommendation="Review the cited clause and add controls, documentation, or human oversight where required.",
            source_excerpt=node.get_content()[:1000],
            source_url=node.metadata.get("source_url"),
            retrieval_score=node.score,
        )
        for node in retrieved
    ]
    return ComplianceReport(summary=summary, findings=findings)


def analyze_ai_system(description: str) -> ComplianceReport:
    if not description.strip():
        return ComplianceReport(summary="No description provided.", findings=[])

    retrieved = retrieve_clauses(description)
    guardrail_findings = deterministic_findings(description, retrieved)

    try:
        llm_report = analyze_with_llm(description, retrieved)
    except Exception as exc:
        fallback = build_retrieval_fallback(
            description,
            retrieved,
            f"Retrieved relevant EU AI Act clauses. LLM analysis was unavailable: {exc}",
        )
        fallback.findings = merge_findings(guardrail_findings, fallback.findings)
        return fallback

    source_lookup = {
        get_clause_label(node.metadata): node
        for node in retrieved
    }
    llm_findings = []

    for item in llm_report.get("findings", []):
        source = resolve_source(item.get("clause", ""), source_lookup)
        if source is None:
            continue

        llm_findings.append(
            ComplianceFinding(
                clause=get_clause_label(source.metadata),
                source_type=source.metadata.get("section_type", "EU AI Act"),
                finding=item.get("finding", ""),
                risk_level=normalize_risk_level(item.get("risk_level", "Medium")),
                evidence=item.get("evidence", ""),
                recommendation=item.get("recommendation", ""),
                source_excerpt=source.get_content()[:1000],
                source_url=source.metadata.get("source_url"),
                retrieval_score=source.score,
            )
        )

    return ComplianceReport(
        summary=llm_report.get("summary", "Compliance analysis generated from retrieved EU AI Act context."),
        findings=merge_findings(guardrail_findings, llm_findings),
    )


def merge_findings(primary: list[ComplianceFinding], secondary: list[ComplianceFinding]) -> list[ComplianceFinding]:
    merged: list[ComplianceFinding] = []
    seen: set[tuple[str, str]] = set()
    high_risk_guardrail_clauses = {
        finding.clause
        for finding in primary
        if finding.risk_level == "High"
    }

    for finding in primary:
        key = (finding.clause, finding.finding.lower())
        if key in seen:
            continue
        seen.add(key)
        merged.append(finding)

    for finding in secondary:
        if should_skip_secondary_finding(finding):
            continue
        if finding.clause in high_risk_guardrail_clauses:
            continue
        key = (finding.clause, finding.finding.lower())
        if key in seen:
            continue
        seen.add(key)
        merged.append(finding)

    return merged[:6]


def should_skip_secondary_finding(finding: ComplianceFinding) -> bool:
    finding_text = f"{finding.finding} {finding.recommendation}".lower()
    if finding.clause == "Article 3":
        return True
    if "no remediation needed" in finding_text:
        return True
    if "not necessarily" in finding_text:
        return True
    return False
