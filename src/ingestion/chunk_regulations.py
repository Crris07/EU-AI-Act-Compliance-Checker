import re
from dataclasses import dataclass


EU_AI_ACT_SOURCE_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202401689"
SECTION_PATTERN = re.compile(
    r"(?m)^(?P<article>Article[\s\u00a0]+\d+[a-zA-Z]?)\s*$|^(?P<annex>ANNEX[\s\u00a0]+[IVXLCDM]+)\s*$"
)


@dataclass(frozen=True)
class RegulationChunk:
    text: str
    metadata: dict[str, str]


def chunk_eu_ai_act(text: str) -> list[RegulationChunk]:
    """Split the EU AI Act into Article and Annex chunks."""
    matches = list(SECTION_PATTERN.finditer(text))
    chunks: list[RegulationChunk] = []

    if not matches:
        return [
            RegulationChunk(
                text=text.strip(),
                metadata={
                    "regulation": "EU AI Act",
                    "regulation_id": "Regulation (EU) 2024/1689",
                    "jurisdiction": "EU",
                    "section_type": "FullText",
                    "section_number": "Unknown",
                    "source_url": EU_AI_ACT_SOURCE_URL,
                },
            )
        ] if text.strip() else []

    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section_number = normalize_legal_label(match.group("article") or match.group("annex") or "")
        section_type = "Article" if match.group("article") else "Annex"
        section_text = text[start:end].strip()

        if section_text:
            chunks.append(
                RegulationChunk(
                    text=section_text,
                    metadata={
                        "regulation": "EU AI Act",
                        "regulation_id": "Regulation (EU) 2024/1689",
                        "jurisdiction": "EU",
                        "section_type": section_type,
                        "section_number": section_number,
                        "article_number": section_number if section_type == "Article" else "",
                        "source_url": EU_AI_ACT_SOURCE_URL,
                    },
                )
            )

    return chunks


def normalize_legal_label(value: str) -> str:
    return re.sub(r"[\s\u00a0]+", " ", value).strip()
