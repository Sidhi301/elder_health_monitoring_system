"""
This file loads environment settings from the .env file.
Keeping configuration here makes the rest of the project easier to read.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


# Load values from backend/.env based on this file's location.
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)


# Read settings with simple default values for safety.
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "elder_health_system")
SECRET_KEY = os.getenv("SECRET_KEY", "change_this_secret_in_production")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
CARE_MANAGER_SECRET = os.getenv("CARE_MANAGER_SECRET", "giet")
