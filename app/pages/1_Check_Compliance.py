import streamlit as st

from src.analysis.compliance_engine import analyze_ai_system

st.title("Check Compliance")

description = st.text_area(
    "AI system or policy description",
    height=220,
    placeholder="Describe the AI system, target users, decisions it supports, input data, and deployment context.",
)

uploaded_file = st.file_uploader("Optional document upload", type=["pdf", "docx", "txt", "md"])

if st.button("Run EU AI Act Check", type="primary"):
    if not description and uploaded_file is None:
        st.warning("Add a description or upload a document first.")
    else:
        with st.spinner("Retrieving EU AI Act clauses and drafting findings..."):
            report = analyze_ai_system(description=description)
        st.subheader("Summary")
        st.write(report.summary)

        st.subheader("Findings")
        if not report.findings:
            st.info("No findings were generated from the retrieved EU AI Act context.")

        for index, finding in enumerate(report.findings, start=1):
            with st.expander(f"{index}. {finding.clause} | {finding.risk_level}", expanded=index == 1):
                st.write(f"**Source type:** {finding.source_type}")
                st.write(f"**Finding:** {finding.finding}")
                st.write(f"**Evidence:** {finding.evidence}")
                st.write(f"**Recommendation:** {finding.recommendation}")
                if finding.retrieval_score is not None:
                    st.write(f"**Retrieval score:** {finding.retrieval_score:.3f}")
                if finding.source_url:
                    st.link_button("Open official source", finding.source_url)
                st.text_area(
                    "Retrieved EU AI Act excerpt",
                    value=finding.source_excerpt,
                    height=220,
                    key=f"source_excerpt_{index}",
                )

        with st.expander("Raw JSON"):
            st.json(report.model_dump())
