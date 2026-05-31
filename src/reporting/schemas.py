from pydantic import BaseModel, Field


class ComplianceFinding(BaseModel):
    clause: str
    source_type: str = "EU AI Act"
    finding: str
    risk_level: str = Field(pattern="^(High|Medium|Low)$")
    evidence: str
    recommendation: str
    source_excerpt: str
    source_url: str | None = None
    retrieval_score: float | None = None


class ComplianceReport(BaseModel):
    summary: str
    findings: list[ComplianceFinding]
