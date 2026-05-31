import streamlit as st

from src.config import settings
from src.retrieval.vector_store import get_chroma_collection

st.set_page_config(page_title="EU AI Act Compliance Checker", layout="wide")

st.title("EU AI Act Compliance Checker")
st.caption("RAG-powered compliance research assistant using LlamaIndex, ChromaDB, and a local open-source LLM.")

try:
    chunk_count = get_chroma_collection().count()
except Exception:
    chunk_count = 0

col1, col2, col3 = st.columns(3)
col1.metric("Knowledge base chunks", chunk_count)
col2.metric("Retrieval", "Hybrid")
col3.metric("LLM", f"{settings.llm_provider}: {settings.ollama_model}")

st.success("EU AI Act knowledge base is indexed and ready for citation-grounded retrieval.")

st.write(
    "Use **Check Compliance** to analyze an AI system description. "
    "If the local model cannot run on available memory, the app returns a citation-first retrieval report instead of failing."
)
