
from flask import Flask, render_template, request
import PyPDF2
import spacy
latest_data = {}

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")

# 🔹 Skills List
SKILLS = [
    "Python", "Java", "HTML", "CSS", "JavaScript",
    "GitHub", "Web Design", "Responsive Design",
    "Photography", "Communication", "Teamwork", "SQL"
]

# 🔹 Extract Text
def extract_text(file):
    pdf = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text() or ""
    return text

# 🔹 Extract Skills
def extract_skills(text):
    found_skills = []
    for skill in SKILLS:
        if skill.lower() in text.lower():
            found_skills.append(skill)
    return found_skills

# 🔹 Suggestions
def get_suggestions(skills):
    suggestions = []

    if "Python" not in skills:
        suggestions.append("❗ Add Python skill (high demand)")

    if "SQL" not in skills:
        suggestions.append("❗ Add SQL for backend/data roles")

    if len(skills) < 5:
        suggestions.append("⚠ Add more technical skills to improve ATS score")

    if "Communication" not in skills:
        suggestions.append("💬 Add communication skills")

    return suggestions
# 🔹 Job Matching
import re

def clean_text(text):
    return re.findall(r'\b\w+\b', text.lower())

import re

import re

STOPWORDS = {"the", "and", "for", "with", "looking", "developer"}

def clean_text(text):
    words = re.findall(r'\b\w+\b', text.lower())
    return [w for w in words if w not in STOPWORDS]
def match_job_description(resume_text, job_desc):
    resume_words = set(clean_text(resume_text))
    jd_words = set(clean_text(job_desc))

    common = resume_words & jd_words

    if len(jd_words) == 0:
        return 0, []

    match_percent = int((len(common) / len(jd_words)) * 100)
    missing = list(jd_words - resume_words)

    return match_percent, missing[:10]
def highlight_missing(text, missing_keywords):
    for word in missing_keywords:
        text = text.replace(word, f"<span style='color:red;'>{word}</span>")
        text = text.replace(word.capitalize(), f"<span style='color:red;'>{word.capitalize()}</span>")
    return text

def ai_suggestions(resume_text, job_desc):
    feedback = []

    text = resume_text.lower()

    if "python" not in text:
        feedback.append("💡 Add Python skill (high demand in industry)")

    if "sql" not in text:
        feedback.append("💡 Include SQL for database-related roles")

    if "project" not in text:
        feedback.append("📁 Add projects section to strengthen your resume")

    if "communication" not in text:
        feedback.append("💬 Mention communication skills")

    if len(text.split()) < 100:
        feedback.append("⚠ Resume content is too short, add more details")

    if not feedback:
        feedback.append("✅ Your resume looks strong and well-optimized!")

    return "\n".join(feedback)

# ✅ ADD HERE 👇
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(skills, score, match_percent, suggestions, ai_feedback):
    doc = SimpleDocTemplate("report.pdf")
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("AI Resume Analysis Report", styles['Title']))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"Skills: {', '.join(skills)}", styles['Normal']))
    content.append(Paragraph(f"ATS Score: {score}%", styles['Normal']))
    content.append(Paragraph(f"Job Match: {match_percent}%", styles['Normal']))

    content.append(Spacer(1, 10))
    content.append(Paragraph("Suggestions:", styles['Heading2']))

    for s in suggestions:
        content.append(Paragraph(f"- {s}", styles['Normal']))

    content.append(Spacer(1, 10))
    content.append(Paragraph("AI Feedback:", styles['Heading2']))
    content.append(Paragraph(ai_feedback, styles['Normal']))

    doc.build(content)

# 🔹 Main Route
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        file = request.files['resume']
        job_desc = request.form.get('job_desc')

        if file:
            text = extract_text(file)
            skills = extract_skills(text)
            score = len(skills) * 10
            suggestions = get_suggestions(skills)
            
            # Resume Strength Logic
            strength = "Weak ❌"
            if score >= 70:
                strength = "Strong 💪"
            elif score >= 40:
                strength = "Average ⚠"
            
            ai_feedback = ""
            if job_desc:
                ai_feedback = ai_suggestions(text, job_desc)
            match_percent = 0
            missing_keywords = []

            if job_desc:
                match_percent, missing_keywords = match_job_description(text, job_desc)

            # Highlight logic
            highlighted_text = text
            if missing_keywords:
                highlighted_text = highlight_missing(text, missing_keywords)
                
            global latest_data
            latest_data = {
                "skills": skills,
                "score": score,
                "match_percent": match_percent,
                "suggestions": suggestions,
                "ai_feedback": ai_feedback
}

            return render_template(
             'index.html',
              resume_text=highlighted_text,
              skills=skills,
              score=score,
              strength=strength,
              suggestions=suggestions,
              match_percent=match_percent,
              missing_keywords=missing_keywords,
              ai_feedback=ai_feedback
)
            
from flask import send_file

@app.route('/download')
def download():
    generate_pdf(
        skills=latest_data.get("skills", []),
        score=latest_data.get("score", 0),
        match_percent=latest_data.get("match_percent", 0),
        suggestions=latest_data.get("suggestions", []),
        ai_feedback=latest_data.get("ai_feedback", "")
    )
    return send_file("report.pdf", as_attachment=True)

    return render_template('index.html')
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)