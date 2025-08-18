from codescribe_ai.scripts.run_pipeline import run_codescribe_pipeline
from flask import Flask, render_template, request, redirect, url_for, send_file
import os, zipfile, uuid, shutil
from git import Repo
from markdown import markdown

app = Flask(__name__)

# 🔹 Configurable base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS = os.path.join(BASE_DIR, "uploads")
OUTPUTS = os.environ.get("OUTPUT_DIR", os.path.join(BASE_DIR, "generated"))

# Ensure folders exist
os.makedirs(UPLOADS, exist_ok=True)
os.makedirs(OUTPUTS, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        project_id = str(uuid.uuid4())
        extract_path = os.path.join(UPLOADS, project_id)

        zip_file = request.files.get("code_zip")
        github_url = request.form.get("github_url")
        output_ext = request.form.get("format", "md")
        output_file = os.path.join(OUTPUTS, f"{project_id}_README.{output_ext}")

        # Handle ZIP upload
        if zip_file and zip_file.filename.endswith(".zip"):
            zip_path = os.path.join(UPLOADS, f"{project_id}.zip")
            zip_file.save(zip_path)
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_path)

        # Handle GitHub repo
        elif github_url:
            try:
                Repo.clone_from(github_url.strip(), extract_path)
            except Exception as e:
                return f"❌ GitHub error: {e}"

        else:
            return "❌ Provide a ZIP or GitHub URL."

        # Run Codescribe pipeline
        run_codescribe_pipeline(extract_path, output_file)

        # Cleanup
        shutil.rmtree(extract_path, ignore_errors=True)

        return redirect(url_for("preview", filename=os.path.basename(output_file)))

    return render_template("index.html")

@app.route("/preview/<filename>")
def preview(filename):
    filepath = os.path.join(OUTPUTS, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        html = markdown(f.read(), extensions=["fenced_code", "tables"])
    return render_template(
        "preview.html",
        html_content=html,
        download_link=url_for("download", filename=filename),
    )

@app.route("/download/<filename>")
def download(filename):
    return send_file(os.path.join(OUTPUTS, filename), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
