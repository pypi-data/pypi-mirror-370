import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Retrieve the Bitwarden folder name from environment variables
BITWARDEN_FOLDER_NAME = os.getenv("BITWARDEN_FOLDER_NAME", "AI_KEYS")
