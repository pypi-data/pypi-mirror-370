import os

def parse_repo_structure(repo_path):  # Parses the repo directory and returns a list of all file paths relative to root
    """
    Scans the provided repository path and returns a list of all source code file paths,
    relative to the root directory.

    Note:
        This function is called by the unit test `test_parse_structure()` in `tests/test_parser.py`.
    """
    file_list = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.go')):  # Extendable
                rel_path = os.path.relpath(os.path.join(root, file), repo_path)
                file_list.append(rel_path.replace("\\", "/"))  # Normalize path
    return file_list
