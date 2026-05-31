from pathlib import Path

import fitz
import requests
from bs4 import BeautifulSoup


REQUEST_TIMEOUT_SECONDS = 60


def load_pdf_text(path: Path) -> str:
    doc = fitz.open(path)
    pages = [page.get_text("text") for page in doc]
    return "\n\n".join(pages)


def load_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    main = soup.find("div", id="TexteOnly") or soup.find("body") or soup
    lines = [
        line.strip()
        for line in main.get_text("\n").splitlines()
        if line.strip()
    ]
    return "\n".join(lines)


def fetch_html(url: str) -> str:
    response = requests.get(
        url,
        timeout=REQUEST_TIMEOUT_SECONDS,
        headers={"User-Agent": "ai-compliance-checker/0.1"},
    )
    response.raise_for_status()
    return response.text


def save_url_html(url: str, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(fetch_html(url), encoding="utf-8")
    return output_path


def load_source_document(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return load_pdf_text(path)
    if suffix in {".html", ".htm"}:
        return html_to_text(path.read_text(encoding="utf-8"))
    if suffix in {".txt", ".md"}:
        return load_text_file(path)
    raise ValueError(f"Unsupported source format: {suffix}")
