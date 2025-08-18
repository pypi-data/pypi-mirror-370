import os
import json

def detect_python_entry(project_path):
    for name in ["app.py", "main.py"]:
        if os.path.exists(os.path.join(project_path, name)):
            return f"python {name}"
    
    for root, _, files in os.walk(project_path):
        for file in files:
            if file == "manage.py":
                return "python manage.py runserver"
            if file == "wsgi.py":
                return "gunicorn app:app"

    return None

def detect_node_entry(project_path):
    package_path = os.path.join(project_path, "package.json")
    if not os.path.exists(package_path):
        return None

    try:
        with open(package_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "scripts" in data:
            if "start" in data["scripts"]:
                return "npm start"
            elif "dev" in data["scripts"]:
                return "npm run dev"

        # fallback: look for server.js or app.js
        for entry in ["server.js", "app.js"]:
            if os.path.exists(os.path.join(project_path, entry)):
                return f"node {entry}"

    except Exception:
        return None

    return None

def generate_usage_instruction(project_path, environment="generic"):
    """
    Returns a suggested way to run the project (CLI).

    Args:
        project_path (str): Path to project
        environment (str): Detected environment (django, flask, react, etc.)

    Returns:
        str: A usage command or instructions
    """
    if environment in ["flask", "django"]:
        cmd = detect_python_entry(project_path)
        if cmd:
            return cmd

    if environment in ["node", "react"]:
        cmd = detect_node_entry(project_path)
        if cmd:
            return cmd

    # Try both methods as fallback
    return detect_python_entry(project_path) or detect_node_entry(project_path) or "Check documentation or main file."
