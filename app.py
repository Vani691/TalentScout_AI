import streamlit as st

st.set_page_config(
    page_title="TalentScout AI",
    page_icon="🧠",
    layout="wide"
)

st.markdown("# 🧠 TalentScout AI")
st.markdown("### Smart Resume Screening using Semantic AI")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Job Description")
    job_description = st.text_area(
        "Paste job requirements here",
        height=250
    )

with col2:
    st.subheader("📄 Candidate Resume")
    resume_text = st.text_area(
        "Paste resume content here",
        height=250
    )

st.markdown("---")

if st.button("🔍 Analyze Match"):
    st.info("AI analysis will be added in the next step.")
