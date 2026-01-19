from openai import OpenAI
from dotenv import load_dotenv
from pypdf import PdfReader
import os

# Load API key from .env
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Read resume PDF
reader = PdfReader("resume.pdf")
resume_text = ""
for page in reader.pages:
    resume_text += page.extract_text()

# AI prompt
prompt = f"""
You are an HR expert.
Analyze the following resume text and extract:
1. Key skills
2. Years of experience
3. Short professional summary

Resume:
{resume_text}
"""

# Call AI
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=300
)

print("===== AI ANALYSIS =====")
print(response.choices[0].message.content)
