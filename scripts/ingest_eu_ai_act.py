import argparse
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.ingestion.build_index import ingest_eu_ai_act_url  # noqa: E402


DEFAULT_EU_AI_ACT_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202401689&qid=1780180102086"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest the official EU AI Act HTML into ChromaDB.")
    parser.add_argument("--url", default=DEFAULT_EU_AI_ACT_URL)
    parser.add_argument("--output", default="data/raw/eu_ai_act.html")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    count = ingest_eu_ai_act_url(args.url, Path(args.output))
    print(f"Ingested {count} EU AI Act chunks into ChromaDB.")


if __name__ == "__main__":
    main()
