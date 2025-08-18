# core/env_var_descriptions.py

ENV_VAR_DESCRIPTIONS = {
    "DEBUG": "Enables debug mode for development.",
    "SECRET_KEY": "Used for cryptographic signing in Flask or Django apps.",
    "DATABASE_URL": "Specifies the database connection string.",
    "PORT": "Port on which the app runs.",
    "API_KEY": "Key used to authenticate with external APIs.",
    "ALLOWED_HOSTS": "List of allowed domains/IPs for the app (Django).",
    "ENV": "Specifies the environment type (development/production).",
    "LOG_LEVEL": "Defines the logging level (INFO, DEBUG, ERROR).",
    "JWT_SECRET": "Secret used for signing JWT tokens.",
    "EMAIL_HOST": "SMTP server for sending emails.",
    "EMAIL_PORT": "Port number for the email service.",
    "EMAIL_HOST_USER": "Username for the email server.",
    "EMAIL_HOST_PASSWORD": "Password for the email server."
}
