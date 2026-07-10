"""
===========================================
 AI Candidate Evaluation System
 Main Application - Flask UI
===========================================
"""

from flask import Flask, request, render_template_string
import os
from cv_parser import read_pdf
from cv_extractor import extract_all
from job_matcher import calculate_skill_score, calculate_experience_score, calculate_education_score

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Candidate Evaluator</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; background: #f5f5f5; }
        h1 { color: #2c3e50; }
        .form-group { margin-bottom: 15px; }
        label { font-weight: bold; display: block; margin-bottom: 5px; }
        input[type=text], input[type=number], textarea {
            width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;
        }
        button { background: #2c3e50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #34495e; }
        .card { background: white; padding: 20px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .score { font-size: 24px; font-weight: bold; }
        .green { color: #27ae60; }
        .yellow { color: #f39c12; }
        .red { color: #e74c3c; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #2c3e50; color: white; }
    </style>
</head>
<body>
    <h1>🤖 AI Candidate Evaluation System</h1>

    <div class="card">
        <form method="POST" enctype="multipart/form-data">
            <div class="form-group">
                <label>Job Title:</label>
                <input type="text" name="job_title" placeholder="e.g. AI Engineer" required>
            </div>
            <div class="form-group">
                <label>Required Skills (comma separated):</label>
                <textarea name="required_skills" rows="2" placeholder="e.g. python, machine learning, sql" required></textarea>
            </div>
            <div class="form-group">
                <label>Preferred Skills (comma separated):</label>
                <textarea name="preferred_skills" rows="2" placeholder="e.g. docker, git, aws"></textarea>
            </div>
            <div class="form-group">
                <label>Minimum Years of Experience:</label>
                <input type="number" name="min_experience" value="2" min="0" max="20">
            </div>
            <div class="form-group">
                <label>Upload CV Files (PDF):</label>
                <input type="file" name="cvs" multiple accept=".pdf" required>
            </div>
            <button type="submit">🚀 Evaluate Candidates</button>
        </form>
    </div>

    {% if results %}
    <h2>🏆 Ranking Results</h2>
    <div class="card">
        <table>
            <tr>
                <th>Rank</th>
                <th>Name</th>
                <th>Email</th>
                <th>Experience</th>
                <th>Final Score</th>
                <th>Suitability</th>
            </tr>
            {% for r in results %}
            <tr>
                <td>#{{ loop.index }}</td>
                <td>{{ r.name }}</td>
                <td>{{ r.email }}</td>
                <td>{{ r.experience }} years</td>
                <td class="score {% if r.score >= 75 %}green{% elif r.score >= 50 %}yellow{% else %}red{% endif %}">
                    {{ r.score }}%
                </td>
                <td>{{ r.suitability }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>

    {% for r in results %}
    <div class="card">
        <h3>#{{ loop.index }} - {{ r.name }} ({{ r.score }}%)</h3>
        <p>✅ <b>Matched Skills:</b> {{ r.matched }}</p>
        <p>❌ <b>Missing Skills:</b> {{ r.missing }}</p>
        <p>🎓 <b>Education:</b> {{ r.education }}</p>
    </div>
    {% endfor %}
    {% endif %}

</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    results = []

    if request.method == "POST":
        job_title       = request.form.get("job_title")
        required_skills = [s.strip().lower() for s in request.form.get("required_skills", "").split(",") if s.strip()]
        preferred_skills = [s.strip().lower() for s in request.form.get("preferred_skills", "").split(",") if s.strip()]
        min_experience  = int(request.form.get("min_experience", 2))
        education_required = ["Bachelor's", "Master's", "PhD"]

        files = request.files.getlist("cvs")

        for file in files:
            if file.filename.endswith(".pdf"):
                path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(path)

                cv_text = read_pdf(path)
                if cv_text:
                    candidate = extract_all(cv_text)

                    skill_score, matched_required, _ = calculate_skill_score(
                        candidate["skills"], required_skills, preferred_skills
                    )
                    experience_score = calculate_experience_score(candidate["experience_years"], min_experience)
                    education_score  = calculate_education_score(candidate["education"], education_required)

                    final_score = round((skill_score * 0.60) + (experience_score * 0.30) + (education_score * 0.10), 2)

                    if final_score >= 75:
                        suitability = "🟢 Highly Suitable"
                    elif final_score >= 50:
                        suitability = "🟡 Moderately Suitable"
                    else:
                        suitability = "🔴 Not Suitable"

                    missing = [s for s in required_skills if s not in candidate["skills"]]

                    results.append({
                        "name":       candidate["name"] or file.filename,
                        "email":      candidate["email"] or "N/A",
                        "experience": candidate["experience_years"],
                        "education":  candidate["education"],
                        "score":      final_score,
                        "suitability": suitability,
                        "matched":    ", ".join(matched_required) or "None",
                        "missing":    ", ".join(missing) or "None",
                    })

                os.remove(path)

        results = sorted(results, key=lambda x: x["score"], reverse=True)

    return render_template_string(HTML_TEMPLATE, results=results)


if __name__ == "__main__":
    print("=" * 50)
    print("  AI Candidate Evaluator is running!")
    print("  Open: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)