from src.reporting.schemas import ComplianceReport


def report_to_markdown(report: ComplianceReport) -> str:
    lines = [f"# Compliance Report\n\n{report.summary}\n"]
    for finding in report.findings:
        lines.extend(
            [
                f"## {finding.clause}",
                f"- Finding: {finding.finding}",
                f"- Risk level: {finding.risk_level}",
                f"- Evidence: {finding.evidence}",
                f"- Recommendation: {finding.recommendation}",
                f"- Source excerpt: {finding.source_excerpt}",
                "",
            ]
        )
    return "\n".join(lines)

