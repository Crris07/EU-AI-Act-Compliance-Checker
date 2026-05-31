# Scripts

## Ingest EU AI Act

```powershell
python scripts/ingest_eu_ai_act.py
```

This downloads the official EUR-Lex HTML source, saves it to `data/raw/eu_ai_act.html`,
chunks the text by Article, and stores embeddings in the local ChromaDB collection.
