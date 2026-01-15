import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_int_env(key, default=None):
    """Helper to get an environment variable and cast it to int."""
    value = os.getenv(key)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError:
        print(f"Warning: Environment variable {key} is not a valid integer. Using default: {default}")
        return default

# Telegram Configuration
TELEGRAM_API_ID = get_int_env("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME", "telegram_session")

# Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Target Configuration
# TARGET_GROUP_ID can be an integer (mostly negative for groups)
TARGET_GROUP_ID = get_int_env("TARGET_GROUP_ID")
# TARGET_TOPIC_ID is typically an integer
TARGET_TOPIC_ID = get_int_env("TARGET_TOPIC_ID")

def validate_config():
    """Validates that all necessary configuration variables are set."""
    required_vars = [
        ("TELEGRAM_API_ID", TELEGRAM_API_ID),
        ("TELEGRAM_API_HASH", TELEGRAM_API_HASH),
        ("GEMINI_API_KEY", GEMINI_API_KEY)
    ]

    missing = [name for name, value in required_vars if not value]

    if missing:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

    return True

if __name__ == "__main__":
    try:
        validate_config()
        print("Configuration is valid.")
    except EnvironmentError as e:
        print(f"Configuration error: {e}")
