# core/dependency_parser.py

import os
import json

def extract_python_dependencies(project_path):
    """
    Parses requirements.txt and returns a list of Python dependencies.
    """
    requirements_path = os.path.join(project_path, "requirements.txt")
    if not os.path.isfile(requirements_path):
        return []

    with open(requirements_path, "r", encoding="utf-8") as f:
        deps = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return deps

def extract_node_dependencies(project_path):
    """
    Parses package.json and returns a list of Node/React dependencies.
    """
    package_path = os.path.join(project_path, "package.json")
    if not os.path.isfile(package_path):
        return []

    try:
        with open(package_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            deps = list(data.get("dependencies", {}).keys())
            dev_deps = list(data.get("devDependencies", {}).keys())
            return deps + dev_deps
    except Exception:
        return []

def extract_all_dependencies(project_path):
    """
    Unified function that checks for both Python and Node dependencies.
    """
    return {
        "python": extract_python_dependencies(project_path),
        "node": extract_node_dependencies(project_path)
    }
