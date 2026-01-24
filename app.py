import streamlit as st
import PyPDF2
import docx
from sentence_transformers import SentenceTransformer, util
import re

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

def extract_skills(text):
    # Simple skill extraction using regex (expand as needed)
    skills = set()
    skill_keywords = [
        'python', 'java', 'javascript', 'sql', 'machine learning', 'ai', 'data analysis',
        'react', 'node.js', 'docker', 'aws', 'git', 'agile', 'scrum'
    ]
    text_lower = text.lower()
    for skill in skill_keywords:
        if skill in text_lower:
            skills.add(skill.title())
    return skills

model = load_model()
st.set_page_config(
    page_title="TalentScout AI",
    page_icon="🧠",
    layout="wide"
)

# -------------------------------
# 2. HELPER FUNCTIONS
# -------------------------------

def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def extract_text_from_docx(file):
    try:
        doc = docx.Document(file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading DOCX: {e}")
        return ""

def extract_skills(text):
    """
    Extracts skills using a hybrid approach:
    1. Direct Keyword Matching
    2. Inference Matching (e.g., Django -> Python)
    """
    
    # --- Database of Skills ---
    skills_db = [
        "python", "java", "c++", "javascript", "typescript", "ruby", "swift", "go", "php",
        "react", "angular", "vue", "django", "flask", "fastapi", "spring boot", "laravel",
        "aws", "azure", "google cloud", "docker", "kubernetes", "jenkins", "terraform",
        "sql", "mysql", "postgresql", "mongodb", "redis", "firebase",
        "machine learning", "deep learning", "nlp", "tensorflow", "pytorch", "scikit-learn",
        "pandas", "numpy", "matplotlib", "html", "css", "git", "linux", "jira"
    ]
    
    # --- Inference Map (The "Smart" Logic) ---
    # This teaches the AI that specific frameworks imply knowledge of the parent language.
    inference_map = {
        "django": "python",
        "flask": "python",
        "fastapi": "python",
        "pandas": "python",
        "numpy": "python",
        "scikit-learn": "python",
        "react": "javascript",
        "angular": "javascript",
        "vue": "javascript",
        "typescript": "javascript",
        "spring boot": "java",
        "laravel": "php",
        "tensorflow": "python",
        "pytorch": "python",
        "aws": "cloud computing",
        "azure": "cloud computing",
        "gcp": "cloud computing"
    }

    text_lower = text.lower()
    found_skills = set()
    
    # A. Direct Keyword Matching
    for skill in skills_db:
        # Use regex to find whole words only (prevents finding "java" in "javascript")
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            found_skills.add(skill)
    
    # B. Inference Matching
    # If a framework is found, automatically add the parent language
    for skill in list(found_skills):
        if skill in inference_map:
            implied_skill = inference_map[skill]
            found_skills.add(implied_skill)

    return found_skills

# -------------------------------
# 3. LOAD AI MODEL
# -------------------------------
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()

# -------------------------------
# 4. SIDEBAR & UI LAYOUT
# -------------------------------
with st.sidebar:
    st.title("🧠 TalentScout AI")
    st.markdown("### Smart Resume Screening")
    st.info(
        "**Unfair Advantage:**\n"
        "Traditional ATS rejects resumes that miss keywords.\n\n"
        "**TalentScout AI** uses 'Inferred Competence'. If you list *Django*, we know you know *Python*."
    )
    st.markdown("---")
    st.write("Created for Hackathon 2026")

# Main Header
st.markdown(
    """
    <h1 style='text-align: center; color: #4F8BF9;'>TalentScout AI</h1>
    <p style='text-align: center; font-size: 1.2em;'>
    The ATS that thinks like a human recruiter.
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

# Input Section
col1, col2 = st.columns(2)

with col1:
    st.subheader("1️⃣ Job Description (JD)")
    job_description = st.text_area(
        "Paste Job Requirements",
        height=300,
        placeholder="e.g. Looking for a Python Developer with experience in SQL and Cloud Computing..."
    )

with col2:
    st.subheader("2️⃣ Candidate Resume")
    input_method = st.radio("Choose input method:", ("Upload File", "Paste Text"))
    
    resume_text = ""
    if input_method == "Upload File":
        uploaded_file = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"])
        if uploaded_file is not None:
            if uploaded_file.name.endswith(".pdf"):
                resume_text = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.name.endswith(".docx"):
                resume_text = extract_text_from_docx(uploaded_file)
            st.success("✅ Resume Loaded Successfully")
    else:
        resume_text = st.text_area("Paste Resume Text", height=200)

# -------------------------------
# 5. ANALYSIS LOGIC
# -------------------------------
if st.button("🚀 Analyze Candidate", type="primary", use_container_width=True):
    if not job_description or not resume_text:
        st.warning("⚠️ Please provide both a Job Description and a Resume to proceed.")
    else:
        with st.spinner("🔍 Reading Resume... Extracting Skills... Calculating Match..."):
            
            # --- STEP 1: Semantic Match (The Context) ---
            # This captures the "vibe" and general meaning
            emb1 = model.encode(job_description, convert_to_tensor=True)
            emb2 = model.encode(resume_text, convert_to_tensor=True)
            semantic_score = util.cos_sim(emb1, emb2).item() * 100

            # --- STEP 2: Smart Skill Extraction ---
            jd_skills = extract_skills(job_description)
            resume_skills = extract_skills(resume_text)
            
            # Set Operations
            missing_skills = jd_skills - resume_skills
            matching_skills = jd_skills.intersection(resume_skills)
            
            # Calculate final score as average of semantic and skill match
            skill_match_pct = (len(matching_skills) / max(1, len(jd_skills))) * 100
            final_score = (semantic_score + skill_match_pct) / 2
        

        # -------------------------------
        # 6. RESULTS DISPLAY
        # -------------------------------
        st.markdown("---")
        
        # Top Metrics
        st.metric("Final Match Score", f"{final_score:.1f}%")
