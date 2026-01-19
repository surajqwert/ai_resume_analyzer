# app.py
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from pypdf import PdfReader
import os
import time
from fpdf import FPDF
import re

# -------------------------
# Helper: Extract name from resume
# -------------------------
def extract_name_from_resume(text):
    lines = text.split("\n")
    for line in lines[:6]:  # name usually in top lines
        clean = line.strip()
        if 2 <= len(clean.split()) <= 3:
            return clean
    return "Candidate"

# -------------------------
# Helper: Extract sections from AI output
# -------------------------
def extract_section(title, text):
    pattern = rf"{title}:\s*(.*?)(?:\n\n|\Z)"
    match = re.search(pattern, text, re.S | re.I)
    if match:
        items = match.group(1).strip().split("\n")
        return [i.replace("-", "").strip() for i in items if i.strip()]
    return []

# -------------------------
# Load API Key
# -------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------
# Streamlit Page Config
# -------------------------
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🤖",
    layout="wide",
)

# -------------------------
# Custom CSS
# -------------------------
st.markdown("""
<style>
h1 {
    color: #1f77b4;
    text-align: center;
    font-size: 40px;
    font-weight: bold;
}
h2 {
    color: #ff7f0e;
}
.stButton>button {
    background-color: #1f77b4;
    color: white;
    font-size: 16px;
    padding: 10px 20px;
    border-radius: 10px;
}
.stDownloadButton>button {
    background-color: #2ca02c;
    color: white;
    font-size: 16px;
    padding: 10px 20px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🤖 AI Resume Analyzer & Job Matcher</h1>", unsafe_allow_html=True)

# -------------------------
# Upload Resume & JD
# -------------------------
col1, col2 = st.columns(2)

with col1:
    resume_file = st.file_uploader("📄 Upload Resume PDF", type=["pdf"])

with col2:
    jd_text = st.text_area("✏️ Paste Job Description Here", height=250)

# -------------------------
# Run AI Analysis
# -------------------------
if resume_file and jd_text:
    with st.spinner("Analyzing Resume... Please wait 🤓"):
        # Read resume PDF
        reader = PdfReader(resume_file)
        resume_text = ""
        for page in reader.pages:
            if page.extract_text():
                resume_text += page.extract_text()

        # AI Prompt
        prompt = f"""
You are an experienced HR professional and ATS system.

Respond STRICTLY in this format:

Name:
<name if visible>

Match Percentage:
<number>%

Matching Skills:
- skill 1
- skill 2

Missing Skills:
- missing skill 1
- missing skill 2

Suggestions:
- suggestion 1
- suggestion 2

Resume:
{resume_text}

Job Description:
{jd_text}
"""

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400
        )

        time.sleep(1)

        # ✅ IMPORTANT LINE (FIXED)
        ai_output = response.choices[0].message.content

    st.success("✅ Analysis Complete!")

    # -------------------------
    # Extract Name & Match %
    # -------------------------
    name_match = re.search(r"Name:\s*(.*)", ai_output)
    candidate_name = (
        name_match.group(1).strip()
        if name_match else extract_name_from_resume(resume_text)
    )

    match_match = re.search(r"(\d+)%", ai_output)
    match_percent = int(match_match.group(1)) if match_match else 0

    # -------------------------
    # Display Results
    # -------------------------
    st.markdown(f"## 👤 Candidate: **{candidate_name}**")
    st.markdown(f"### 🎯 Resume Match: **{match_percent}%**")
    st.progress(match_percent)

    matching_skills = extract_section("Matching Skills", ai_output)
    missing_skills = extract_section("Missing Skills", ai_output)
    suggestions = extract_section("Suggestions", ai_output)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### ✅ Matching Skills")
        for skill in matching_skills:
            st.markdown(f"- {skill}")

    with col2:
        st.markdown("### ❌ Missing Skills")
        for skill in missing_skills:
            st.markdown(f"- {skill}")

    with col3:
        st.markdown("### 💡 Suggestions")
        for s in suggestions:
            st.markdown(f"- {s}")

    # -------------------------
    # PDF Download
    # -------------------------
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", size=12)

    pdf.multi_cell(
        0,
        10,
        f"AI Resume Analysis Report\n\n"
        f"Candidate: {candidate_name}\n"
        f"Match Percentage: {match_percent}%\n\n"
        f"Matching Skills:\n" + "\n".join(matching_skills) +
        "\n\nMissing Skills:\n" + "\n".join(missing_skills) +
        "\n\nSuggestions:\n" + "\n".join(suggestions)
    )

    pdf.set_y(-20)
    pdf.set_font("DejaVu", size=8)
    pdf.cell(0, 10, "Created by Suraj R. Swain", align="C")

    pdf_file = f"{candidate_name.replace(' ', '_')}_Resume_Analysis.pdf"
    pdf.output(pdf_file)

    with open(pdf_file, "rb") as f:
        st.download_button(
            "📥 Download Analysis as PDF",
            f,
            file_name=pdf_file
        )
        st.markdown(
            """
            <hr style="margin-top:40px;">
            <p style="text-align:center; color:gray; font-size:14px;">
                Developed by <b>Suraj R. Swain</b>
            </p>
            """,
            unsafe_allow_html=True
        )
