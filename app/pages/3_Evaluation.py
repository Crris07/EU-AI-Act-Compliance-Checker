import streamlit as st

from src.evaluation.test_cases import load_eval_cases
from src.config import ROOT_DIR

st.title("Evaluation")
st.write("Track whether retrieval finds the expected EU AI Act topics and whether reports stay grounded in retrieved clauses.")

eval_path = ROOT_DIR / "data" / "eval" / "compliance_test_cases.json"
cases = load_eval_cases(eval_path)

st.metric("Evaluation cases", len(cases))

for case in cases:
    with st.expander(case["id"]):
        st.write(case["description"])
        st.write("Expected topics:")
        st.write(", ".join(case["expected_topics"]))
