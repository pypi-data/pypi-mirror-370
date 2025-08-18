# core/prompt_builder.py

import os
from core.lang_detector import detect_language_from_extension

def build_prompt(code_chunk, file_path=None, environment="generic", language="python"):
    """
    Builds a prompt to summarize code with contextual awareness.

    Args:
        code_chunk (str): The code snippet or chunk.
        file_path (str): Optional file path to include in the prompt.
        environment (str): Detected environment/framework (e.g., 'flask', 'react').
        language (str): Language of the file (e.g., 'python', 'javascript').

    Returns:
        str: Formatted prompt string.
    """

    header = "You are an intelligent AI that helps developers understand code easily."

    # Language-aware code block (for formatting)
    language = language.lower()
    code_lang_tag = {
        "python": "python",
        "javascript": "javascript",
        "typescript": "typescript",
        "java": "java",
        "go": "go",
        "c": "c",
        "cpp": "cpp",
        "csharp": "csharp",
        "ruby": "ruby",
        "php": "php",
        "html": "html",
        "css": "css",
        "bash": "bash",
        "json": "json",
        "yaml": "yaml",
        "rust": "rust",
    }.get(language, "")  # fallback to empty if unknown

    # Environment-specific note
    env_note = ""
    match environment.lower():
        case "django":
            env_note = "This is a Django backend project. Look for models, views, URLs, and app configuration.\n"
        case "flask":
            env_note = "This is a Flask backend project. Focus on routes, decorators, and app factory structure.\n"
        case "react":
            env_note = "This is a React frontend project. Explain components, props, hooks, and JSX structure.\n"
        case "node":
            env_note = "This is a Node.js project (likely using Express). Explain API routes, middleware, and logic.\n"
        case "spring":
            env_note = "This is a Java Spring Boot project. Explain services, controllers, and configurations.\n"
        case _:
            env_note = ""  # Generic fallback

    # Prompt instructions
    instructions = (
        f"{env_note}"
        "Summarize the following code clearly for a developer audience:\n"
        "- Explain the main purpose of the file\n"
        "- Describe functions, classes, and key logic\n"
        "- Use simple but technical language\n"
        "- Keep the summary concise and readable"
    )

    # Add file context if available
    context = f"File: {file_path}\n\n" if file_path else ""

    # Format code with correct markdown tag
    code_block = f"```{code_lang_tag}\n{code_chunk.strip()}\n```"

    return f"{header}\n\n{instructions}\n\n{context}{code_block}"
