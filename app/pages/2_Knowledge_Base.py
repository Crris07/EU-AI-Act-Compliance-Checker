import streamlit as st

from scripts.ingest_eu_ai_act import DEFAULT_EU_AI_ACT_URL
from src.ingestion.build_index import ingest_eu_ai_act_url

st.title("Knowledge Base")

st.write("Ingest the official EUR-Lex HTML version of Regulation (EU) 2024/1689.")

url = st.text_input("EU AI Act HTML URL", value=DEFAULT_EU_AI_ACT_URL)
output = st.text_input("Raw HTML output path", value="data/raw/eu_ai_act.html")

if st.button("Build EU AI Act Index", type="primary"):
    with st.spinner("Downloading, chunking, embedding, and indexing the EU AI Act..."):
        chunk_count = ingest_eu_ai_act_url(url=url, raw_output_path=output)
    st.success(f"Indexed {chunk_count} EU AI Act chunks.")
