from pathlib import Path
import os
from dotenv import load_dotenv

# Define BASE_DIR as the parent directory of the current file's parent.
BASE_DIR = Path(__file__).resolve().parent.parent

# Build the path to the .env file.
dotenv_path = BASE_DIR / ".env"
# Load environment variables from the .env file.
load_dotenv(dotenv_path=dotenv_path)

# Retrieve configuration variables from environment.
API_V1_PREFIX = os.getenv("API_V1_PREFIX")
DB_URL = os.getenv("DB_URL")
DB_ECHO = os.getenv("DB_ECHO")
