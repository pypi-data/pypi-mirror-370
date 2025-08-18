import os
import ast
from collections import defaultdict

def extract_imports_from_file(filepath):
    """Parses Python file and extracts its import statements."""
    with open(filepath, "r", encoding="utf-8",errors="ignore") as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except SyntaxError:
            return []

    imports = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])

    return list(imports)

def build_import_graph(project_path):
    """
    Builds a mapping of each file to its internal imports (by filename base).
    
    Returns:
        dict[str, list[str]]: { 'main.py': ['utils', 'auth'], ... }
    """
    graph = defaultdict(list)
    file_map = {}

    # Build map of module name → full path
    for root, _, files in os.walk(project_path):
        for f in files:
            if f.endswith(".py"):
                module_name = f[:-3]  # remove .py
                file_map[module_name] = os.path.join(root, f)

    # Now parse each file for imports
    for module, path in file_map.items():
        imports = extract_imports_from_file(path)
        # Only keep internal project imports (in file_map)
        internal = [imp for imp in imports if imp in file_map]
        graph[module] = internal

    return dict(graph)
