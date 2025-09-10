import os
from dotenv import load_dotenv

def load_environment():
    """
    Load environment variable otomatis berdasarkan APP_ENV.
    Default = development.
    """
    APP_ENV = os.getenv("APP_ENV", "development")

    if APP_ENV == "production":
        env_file = ".env.prod"
    else:
        env_file = ".env.dev"

    load_dotenv(env_file, override=True)
    print(f"Loaded environment: {APP_ENV} ({env_file})")
