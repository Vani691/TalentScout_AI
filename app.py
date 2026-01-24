import streamlit as st
import PyPDF2
import docx
from sentence_transformers import SentenceTransformer, util
import re


st.set_page_config(
    page_title="TalentScout AI",
    page_icon="🧠",
    layout="wide"
)



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
    
    
    skills_db = [
        "python", "java", "c++", "javascript", "typescript", "ruby", "swift", "go", "php",
        "react", "angular", "vue", "django", "flask", "fastapi", "spring boot", "laravel",
        "aws", "azure", "google cloud", "docker", "kubernetes", "jenkins", "terraform",
        "sql", "mysql", "postgresql", "mongodb", "redis", "firebase",
        "machine learning", "deep learning", "nlp", "tensorflow", "pytorch", "scikit-learn",
        "pandas", "numpy", "matplotlib", "html", "css", "git", "linux", "jira"
    ]
    
 
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
    
  
    for skill in skills_db:
        # Use regex to find whole words only (prevents finding "java" in "javascript")
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            found_skills.add(skill)
    
   
    for skill in list(found_skills):
        if skill in inference_map:
            implied_skill = inference_map[skill]
            found_skills.add(implied_skill)

    return found_skills


@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()


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


if st.button("🚀 Analyze Candidate", type="primary", use_container_width=True):
    if not job_description or not resume_text:
        st.warning("⚠️ Please provide both a Job Description and a Resume to proceed.")
    else:
        with st.spinner("🔍 Reading Resume... Extracting Skills... Calculating Match..."):
            
           
            emb1 = model.encode(job_description, convert_to_tensor=True)
            emb2 = model.encode(resume_text, convert_to_tensor=True)
            semantic_score = util.cos_sim(emb1, emb2).item() * 100

           
            jd_skills = extract_skills(job_description)
            resume_skills = extract_skills(resume_text)
            
        
            missing_skills = jd_skills - resume_skills
            matching_skills = jd_skills.intersection(resume_skills)
            
           
            if len(jd_skills) > 0:
                skill_match_score = (len(matching_skills) / len(jd_skills)) * 100
                # 60% Semantic + 40% Hard Skills
                final_score = (semantic_score * 0.3) + (skill_match_score * 0.7)
            else:
                # If no skills detected in JD, rely 100% on semantic context
                final_score = semantic_score

      
        st.markdown("---")
        
       
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Final Match Score", f"{final_score:.1f}%")
        with m2:
            st.metric("Semantic Similarity", f"{semantic_score:.1f}%")
        with m3:
            if len(jd_skills) > 0:
                st.metric("Skill Match", f"{len(matching_skills)}/{len(jd_skills)}")
            else:
                st.metric("Skill Match", "N/A")

      
        st.progress(int(final_score))
        
        if final_score >= 75:
            st.success("🌟 **High Match:** This candidate is a strong fit!")
        elif final_score >= 50:
            st.warning("⚠️ **Moderate Match:** Good potential, but missing some key requirements.")
        else:
            st.error("❌ **Low Match:** Significant skills gap detected.")

       
        st.markdown("### 🧩 Skill Gap Analysis")
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("#### ✅ Matched Skills (Detected & Inferred)")
            if matching_skills:
                # Display tags
                st.write(", ".join([f"`{s}`" for s in matching_skills]))
            else:
                st.write("No direct skill matches found.")

        with c2:
            st.markdown("#### ⚠️ Missing Skills")
            if missing_skills:
                for skill in missing_skills:
                    st.markdown(f"- 🔴 **{skill.title()}**")
                st.caption("Tip: Use these keywords to upskill or update the resume.")
            else:
                if len(jd_skills) > 0:
                    st.success("🎉 No missing skills! Perfect technical match.")
                else:
                    st.write("No specific skills found in JD to check against.")
