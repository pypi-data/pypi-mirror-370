import os
import re

def parse_dotenv(filepath):
    """
    Parses a .env file and returns key-value pairs.
    """
    if not os.path.exists(filepath):
        return {}

    env_vars = {}
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip().strip('"').strip("'")
    return env_vars

def parse_python_config(filepath):
    """
    Parses settings.py or config.py and extracts key assignments.
    """
    if not os.path.exists(filepath):
        return {}

    config_vars = {}
    pattern = re.compile(r'^(\w+)\s*=\s*[\'"]?(.*?)[\'"]?$')

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            match = pattern.match(line.strip())
            if match:
                key, value = match.groups()
                config_vars[key.strip()] = value.strip()
    return config_vars

def extract_env_variables(project_path):
    """
    Checks common config files for environment variables and returns all found.

    Returns:
        dict: Merged environment variables from .env and config files.
    """
    env = {}

    # 1. .env file
    dotenv_path = os.path.join(project_path, ".env")
    env.update(parse_dotenv(dotenv_path))

    # 2. settings.py (Django)
    for root, _, files in os.walk(project_path):
        for name in files:
            if name in ["settings.py", "config.py"]:
                config_path = os.path.join(root, name)
                env.update(parse_python_config(config_path))

    return env
