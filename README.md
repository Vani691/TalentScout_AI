# 🧠 TalentScout AI  
### Smart Resume Screening Platform (AI/ML)

**TalentScout AI** is an intelligent resume screening system that analyzes resumes and maps candidate skills to job requirements using **AI-powered semantic understanding** instead of simple keyword matching.

Traditional ATS systems reject strong candidates due to missing keywords. TalentScout AI overcomes this by understanding **context, inferred skills, and semantic meaning**, making resume evaluation fairer and more human-like.

---

## 🚀 Features

- 📄 Resume input via **PDF, DOCX, or text**
- 🧠 **Semantic similarity analysis** using transformer embeddings
- 🛠️ Smart **skill extraction with inference**
  - Example: *Django → Python*, *React → JavaScript*
- 📊 **Weighted match scoring** (skills + context)
- 🔍 Clear **skill gap analysis**
- 🎯 Actionable improvement suggestions
- 🖥️ Clean, professional **Streamlit UI**

---

## 🧠 How It Works

### 1️⃣ Input
- Job Description (JD)
- Candidate Resume (Upload or Paste)

### 2️⃣ Semantic Understanding
- Both texts are converted into embeddings using a **pre-trained Sentence Transformer**
- **Cosine similarity** measures contextual alignment

### 3️⃣ Smart Skill Mapping
- Extracts skills using:
  - Keyword matching
  - Skill inference (framework → core skill)
- Identifies:
  - Matched skills
  - Missing skills

### 4️⃣ Scoring Logic
Final score is calculated using:
- **Skill Match (Primary Weight)**
- **Semantic Similarity (Context Weight)**

### 5️⃣ Output
- Final Match Percentage
- Skill Match Ratio
- Missing Skills List
- Verdict:
  - ✅ High Match
  - ⚠️ Moderate Match
  - ❌ Low Match

---

## 📊 Why TalentScout AI is Different

| Traditional ATS | TalentScout AI |
|-----------------|---------------|
| Keyword-based | Meaning-based |
| Rejects resumes blindly | Explains skill gaps |
| No inference | Framework → skill inference |
| Black-box decisions | Transparent evaluation |

---

## 🛠️ Tech Stack

- **Python**
- **Sentence Transformers (MiniLM)**
- **Cosine Similarity**
- **Regex-based Skill Extraction**
- **Streamlit**
- **PyPDF2**
- **python-docx**

---

## ▶️ How to Run Locally

```bash
# Create virtual environment
python -m venv venv

# Activate venv (Windows)
venv\Scripts\activate

# Install dependencies
pip install streamlit sentence-transformers torch PyPDF2 python-docx

# Run the application
streamlit run app.py

---

## 🎯 Target Users
- HR Teams
- Recruiters
- Startups
- Placement Cells
- Hiring Managers

---

## 📌 Hackathon Note
This project was developed **during the hackathon window** as a working MVP.  
We used open-source AI models and implemented original application logic, UI flow, and skill inference mechanisms.

---

## 👥 Team – Code Alchemists
- Shravani Mane (Team Lead)
- Shubham
- Sanika
- Sunaina

Multiverse of Tech Hackathon 2026  
Smt. Indira Gandhi College of Engineering
