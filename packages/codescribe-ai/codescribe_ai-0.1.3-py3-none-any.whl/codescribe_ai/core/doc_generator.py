# core/doc_generator.py
from jinja2 import Environment, FileSystemLoader
import os

def generate_section(file_path, summary):  # Formats a file-level summary block in markdown
    """
    Formats a markdown section for a single file's summary.

    Args:
        file_path (str): The file name or relative path.
        summary (str): The text summary from the LLM.

    Returns:
        str: A markdown-formatted section block.
    """
    return f"### `{file_path}`\n\n{summary.strip()}\n\n---\n"


from core.env_var_descriptions import ENV_VAR_DESCRIPTIONS

def generate_readme(summary_dict, dependencies=None, env_vars=None, usage=None, environment="generic", project_name="Codebase"):
    """
    Generates README.md content using Jinja2 templating.

    Args:
        summary_dict (dict): File-wise summaries
        dependencies (dict): Lang-wise dependency lists
        env_vars (dict): Environment variables with descriptions
        usage (str): Command or steps to run the project
        environment (str): Detected tech stack/environment
        project_name (str): Name of the project

    Returns:
        str: Final rendered Markdown string
    """
    template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("readme_template.md")

    content = template.render(
        project_name=project_name,
        overview="This project was auto-documented using CodeScribe AI.",
        summary_dict=summary_dict,
        dependencies=dependencies or {},
        env_vars=env_vars or {},
        usage=usage or "python main.py",
        environment=environment,
        year="2025"
    )

    return content

