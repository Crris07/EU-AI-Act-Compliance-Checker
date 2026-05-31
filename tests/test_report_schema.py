from src.reporting.schemas import ComplianceFinding, ComplianceReport


def test_compliance_report_schema():
    finding = ComplianceFinding(
        clause="Article 9",
        source_type="Article",
        finding="Missing risk management description.",
        risk_level="High",
        evidence="No lifecycle risk process is described.",
        recommendation="Add a documented risk management process.",
        source_excerpt="Article 9...",
    )
    report = ComplianceReport(summary="One issue found.", findings=[finding])

    assert report.findings[0].clause == "Article 9"
