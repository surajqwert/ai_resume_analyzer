from openai import OpenAI
from dotenv import load_dotenv
from pypdf import PdfReader
import os

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Read resume PDF
reader = PdfReader("resume.pdf")
resume_text = "".join([page.extract_text() for page in reader.pages])

# Read Job Description
with open("job_description.txt", "r") as f:
    jd_text = f.read()

# Prompt AI to compare resume vs JD
prompt = f"""
You are an HR expert.
Compare the following resume with the job description.
1. Give a match percentage (0-100%)  
2. List missing skills or qualifications  
3. Suggest ways to improve the resume

Resume:
{resume_text}

Job Description:
{jd_text}
"""

# Call AI
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=400
)

print("===== RESUME MATCH ANALYSIS =====")
print(response.choices[0].message.content)
