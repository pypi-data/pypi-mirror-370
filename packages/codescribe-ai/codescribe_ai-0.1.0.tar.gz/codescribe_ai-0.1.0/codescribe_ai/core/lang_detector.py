# core/lang_detector.py

def detect_language_from_extension(file_path):
    """
    Detect programming language from file extension.
    Supports Python, JavaScript, TypeScript, Java, Go, HTML, CSS, etc.
    """
    ext = file_path.split(".")[-1].lower()
    mapping = {
        "py": "python",
        "js": "javascript",
        "ts": "typescript",
        "jsx": "react",
        "tsx": "react",
        "java": "java",
        "go": "go",
        "html": "html",
        "css": "css",
        "rb": "ruby",
        "php": "php",
        "cpp": "cpp",
        "c": "c",
        "cs": "csharp",
        "rs": "rust",
        "sh": "shell",
        "yml": "yaml",
        "yaml": "yaml",
        "json": "json",
        "md": "markdown",
    }
    return mapping.get(ext, "unknown")
