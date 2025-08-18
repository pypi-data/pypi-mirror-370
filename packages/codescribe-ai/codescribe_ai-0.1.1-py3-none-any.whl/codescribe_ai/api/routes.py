from flask import request, jsonify, send_file
import os, uuid, zipfile, shutil
from git import Repo
from scripts.run_pipeline import run_codescribe_pipeline
from markdown import markdown

from api import api

UPLOAD_DIR = "uploads"
GENERATED_DIR = "generated"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

@api.route("/api/upload_zip", methods=["POST"])
def upload_zip():
    zip_file = request.files.get("file")
    if not zip_file or not zip_file.filename.endswith(".zip"):
        return jsonify({"error": "Invalid zip file"}), 400

    doc_id = str(uuid.uuid4())
    extract_path = os.path.join(UPLOAD_DIR, doc_id)
    zip_path = os.path.join(UPLOAD_DIR, f"{doc_id}.zip")

    zip_file.save(zip_path)
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)

    output_file = os.path.join(GENERATED_DIR, f"{doc_id}_README.md")
    run_codescribe_pipeline(extract_path, output_file)

    shutil.rmtree(extract_path, ignore_errors=True)
    return jsonify({"doc_id": doc_id}), 200

@api.route("/api/upload_github", methods=["POST"])
def upload_github():
    data = request.get_json()
    url = data.get("repo_url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    doc_id = str(uuid.uuid4())
    clone_path = os.path.join(UPLOAD_DIR, doc_id)

    try:
        Repo.clone_from(url.strip(), clone_path)
    except Exception as e:
        return jsonify({"error": f"Git clone failed: {str(e)}"}), 500

    output_file = os.path.join(GENERATED_DIR, f"{doc_id}_README.md")
    run_codescribe_pipeline(clone_path, output_file)

    shutil.rmtree(clone_path, ignore_errors=True)
    return jsonify({"doc_id": doc_id}), 200

@api.route("/api/preview/<doc_id>", methods=["GET"])
def preview_doc(doc_id):
    filepath = os.path.join(GENERATED_DIR, f"{doc_id}_README.md")
    if not os.path.exists(filepath):
        return jsonify({"error": "Document not found"}), 404

    with open(filepath, "r", encoding="utf-8") as f:
        html = markdown(f.read(), extensions=["fenced_code", "tables"])
    return html

@api.route("/api/download/<doc_id>", methods=["GET"])
def download_doc(doc_id):
    filepath = os.path.join(GENERATED_DIR, f"{doc_id}_README.md")
    if not os.path.exists(filepath):
        return jsonify({"error": "Document not found"}), 404
    return send_file(filepath, as_attachment=True)
