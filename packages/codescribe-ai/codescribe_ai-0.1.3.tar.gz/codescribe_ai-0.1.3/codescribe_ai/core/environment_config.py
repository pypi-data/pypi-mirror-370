import os
import json

# core/environment_config.py

def detect_environment(project_path):
    indicators = {
        "django": ["manage.py", "settings.py"],
        "flask": ["app.py", "requirements.txt"],
        "react": ["package.json", "src/index.js"],
        "nextjs": ["next.config.js", "pages/index.js"],
        "node": ["server.js", "app.js"],
        "express": ["package.json", "express"],
        "spring": ["pom.xml", "src/main/java"],
        "laravel": ["artisan", "composer.json"],
    }

    found_files = []
    for root, _, files in os.walk(project_path):
        for file in files:
            found_files.append(file.lower())

    for env, keywords in indicators.items():
        if all(any(key.lower() in f for f in found_files) for key in keywords):
            return env

    return "generic"
