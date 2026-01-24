import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import PyPDF2
import docx
import re


st.set_page_config(
    page_title="TalentScout AI | Enterprise Edition",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
    <style>
    .big-font { font-size: 24px !important; font-weight: bold; }
    
    /* This fixes the 'White Box' issue by making metrics transparent/native */
    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05); /* Subtle transparency */
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
    }
    
   
    .header-logo {
        vertical-align: middle;
        margin-right: 15px;
    }
    </style>
    """, unsafe_allow_html=True)


if 'job_list' not in st.session_state:
    st.session_state['job_list'] = []


@st.cache_resource
def load_transformer_model():
    
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_transformer_model()


def parse_file(file):
    """Extracts text from PDF or DOCX files safely."""
    text = ""
    try:
        if file.name.endswith(".pdf"):
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
        elif file.name.endswith(".docx"):
            doc = docx.Document(file)
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            text = str(file.read(), "utf-8")
    except Exception as e:
        st.error(f"Error reading file: {e}")
    return text

def analyze_skills(text):
    """
    Hybrid Skill Extraction:
    1. Direct keyword matching from a predefined database.
    2. Inference logic (e.g., 'Django' implies 'Python').
    """
    
    tech_stack = [
        "python", "java", "c++", "javascript", "typescript", "ruby", "swift", "go", "php",
        "react", "angular", "vue", "django", "flask", "fastapi", "spring boot", "laravel",
        "aws", "azure", "google cloud", "docker", "kubernetes", "jenkins", "terraform",
        "sql", "mysql", "postgresql", "mongodb", "redis", "firebase",
        "machine learning", "deep learning", "nlp", "tensorflow", "pytorch", "scikit-learn",
        "pandas", "numpy", "matplotlib", "html", "css", "git", "linux", "jira"
    ]
    
    
    inference_engine = {
        "django": "python", "flask": "python", "fastapi": "python", 
        "pandas": "python", "numpy": "python", "scikit-learn": "python",
        "react": "javascript", "angular": "javascript", "vue": "javascript",
        "spring boot": "java", "laravel": "php",
        "tensorflow": "python", "pytorch": "python",
        "aws": "cloud computing", "azure": "cloud computing", "gcp": "cloud computing"
    }

    text_lower = text.lower()
    detected_skills = set()
    
   
    for tech in tech_stack:
       
        if re.search(r'\b' + re.escape(tech) + r'\b', text_lower):
            detected_skills.add(tech)
    
    
    for skill in list(detected_skills):
        if skill in inference_engine:
            detected_skills.add(inference_engine[skill])

    return detected_skills

def compute_match_score(job_desc, resume_text):
    """
    Calculates a weighted score based on:
    - Semantic Similarity (Context)
    - Hard Skill Overlap (Keywords)
    """
   
    embedding_jd = model.encode(job_desc, convert_to_tensor=True)
    embedding_resume = model.encode(resume_text, convert_to_tensor=True)
    semantic_score = util.cos_sim(embedding_jd, embedding_resume).item() * 100

    
    jd_skills = analyze_skills(job_desc)
    resume_skills = analyze_skills(resume_text)
    
    if jd_skills:
        intersection = jd_skills.intersection(resume_skills)
        skill_match = (len(intersection) / len(jd_skills)) * 100
        final_score = (semantic_score * 0.6) + (skill_match * 0.4)
    else:
       
        final_score = semantic_score
        
    return round(final_score, 1), jd_skills, resume_skills



LOGO_URL = "https://cdn-icons-png.flaticon.com/512/2083/2083213.png"

with st.sidebar:
    st.image(LOGO_URL, width=60)
    st.title("TalentScout AI")
    st.caption("v2.1 Enterprise Edition")
    st.markdown("---")
    
    st.markdown("### ⚙️ Controls")
    if st.button("🗑️ Clear Job Database", width='stretch'):
        st.session_state['job_list'] = []
        st.rerun()

    st.markdown("---")
    st.info(
        "**💡 AI Insight:**\n"
        "This system uses 'Inferred Competence'. "
        "Example: If a candidate knows *Django*, we automatically credit them for *Python*."
    )


col_logo, col_title, col_metric = st.columns([1, 6, 2])

with col_logo:
    st.image(LOGO_URL, width=70)

with col_title:
    st.markdown("# TalentScout AI")
    st.caption("Intelligent Resume Screening & Skill Gap Analysis")

with col_metric:
    st.metric(label="Active Positions", value=len(st.session_state['job_list']))

st.divider()


st.subheader("1️  Job Database Management")

with st.expander("➕ Add a New Position", expanded=not st.session_state['job_list']):
    c1, c2 = st.columns([1, 2])
    with c1:
        new_role_title = st.text_input("Job Title", placeholder="e.g. Full Stack Engineer")
    with c2:
        new_role_desc = st.text_area("Job Description", placeholder="Paste the full job description here...", height=100)
    
    if st.button("Save Position to Database", type="primary"):
        if new_role_title and new_role_desc:
            st.session_state['job_list'].append({
                "title": new_role_title, 
                "desc": new_role_desc,
                "date": pd.Timestamp.now().strftime("%Y-%m-%d")
            })
            st.success(f"✅ Position '{new_role_title}' added successfully!")
            st.rerun()
        else:
            st.warning("⚠️ Please provide both a Job Title and Description.")


if st.session_state['job_list']:
    st.caption("Current Openings in Database:")
    df_jobs = pd.DataFrame(st.session_state['job_list'])
    st.dataframe(df_jobs[["title", "date"]], width='stretch', hide_index=True)

st.divider()


st.subheader("2️ Candidate Evaluation")

uploaded_resume = st.file_uploader("Upload Candidate Resume (PDF/DOCX)", type=["pdf", "docx", "txt"])

if uploaded_resume and st.session_state['job_list']:
    
    resume_content = parse_file(uploaded_resume)
    
    if st.button(" Analyze Candidate Fit", type="primary", width='stretch'):
        
        with st.spinner(" AI is analyzing semantic context and extracting skills..."):
            analysis_results = []
            
            for job in st.session_state['job_list']:
                score, jd_skills, resume_skills = compute_match_score(job['desc'], resume_content)
                missing_skills = jd_skills - resume_skills
                
                analysis_results.append({
                    "Role": job['title'],
                    "Match Score": score,  
                    "Missing Critical Skills": ", ".join(list(missing_skills)[:3]) if missing_skills else "None",
                    "_full_missing": missing_skills 
                })
            
            df_results = pd.DataFrame(analysis_results).sort_values(by="Match Score", ascending=False)
            best_match = df_results.iloc[0]

            st.markdown("###  Analysis Report")
            
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Top Recommended Role", best_match['Role'])
            with m2:
                st.metric("Match Confidence", f"{best_match['Match Score']}%")
            with m3:
                st.metric("Technical Fit", "Strong" if best_match['Match Score'] > 75 else "Moderate" if best_match['Match Score'] > 50 else "Weak")

           
            st.info(f"**Skill Gap Analysis for '{best_match['Role']}':**")
            
            col_gap1, col_gap2 = st.columns(2)
            with col_gap1:
                if best_match['_full_missing']:
                    st.write("⚠️ **Missing Skills:**")
                    for skill in best_match['_full_missing']:
                        st.markdown(f"- 🔴 {skill.title()}")
                else:
                    st.success("✅ No critical skills missing!")
            
            with col_gap2:
                 st.write("💡 **Recommendation:**")
                 if best_match['Match Score'] > 80:
                     st.write("Candidate is a strong fit. Proceed to interview.")
                 elif best_match['Match Score'] > 50:
                     st.write("Candidate has potential but lacks specific tech stack experience.")
                 else:
                     st.write("Candidate profile does not align with current requirements.")

          
            st.markdown("####  Cross-Role Comparison")
            
          
            st.dataframe(
                df_results.drop(columns=["_full_missing"]),
                column_config={
                    "Match Score": st.column_config.ProgressColumn(
                        "Match Score",
                        help="AI Confidence Score",
                        format="%.1f%%",
                        min_value=0,
                        max_value=100,
                    ),
                },
                width='stretch',
                hide_index=True
            )

elif not st.session_state['job_list']:
    st.info("👆 Please add a job position above to start screening.")
