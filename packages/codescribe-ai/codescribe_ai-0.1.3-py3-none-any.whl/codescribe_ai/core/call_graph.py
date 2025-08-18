import ast
import os
from collections import defaultdict

def extract_call_graph(filepath):
    """
    Extracts a call graph from a single Python file.
    Returns:
        - calls_from: dict[str, list[str]] - which functions call what
        - defined_funcs: list[str] - all defined functions in the file
    """
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return {}, []

    defined_funcs = []
    calls_from = defaultdict(list)

    class CallGraphVisitor(ast.NodeVisitor):
        def __init__(self):
            self.current_func = None

        def visit_FunctionDef(self, node):
            self.current_func = node.name
            defined_funcs.append(node.name)
            self.generic_visit(node)
            self.current_func = None

        def visit_Call(self, node):
            if self.current_func and isinstance(node.func, ast.Name):
                called = node.func.id
                calls_from[self.current_func].append(called)
            self.generic_visit(node)

    CallGraphVisitor().visit(tree)
    return dict(calls_from), defined_funcs

def build_project_call_graph(project_path):
    """
    Walks all .py files and builds a full project-wide call graph.
    Returns:
        call_graph: dict[file -> {func -> [calls]}]
    """
    call_graph = {}
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                calls, defs = extract_call_graph(full_path)
                if defs:
                    call_graph[file] = calls
    return call_graph
