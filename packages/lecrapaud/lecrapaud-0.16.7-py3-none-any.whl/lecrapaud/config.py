import os
from dotenv import load_dotenv

load_dotenv(override=False)

PYTHON_ENV = os.getenv("PYTHON_ENV")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
EXPERIMENT_ID = os.getenv("EXPERIMENT_ID")
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")

DB_USER = (
    os.getenv("TEST_DB_USER") if PYTHON_ENV == "Test" else os.getenv("DB_USER", None)
)
DB_PASSWORD = (
    os.getenv("TEST_DB_PASSWORD", "")
    if PYTHON_ENV == "Test"
    else os.getenv("DB_PASSWORD", "")
)
DB_HOST = (
    os.getenv("TEST_DB_HOST") if PYTHON_ENV == "Test" else os.getenv("DB_HOST", None)
)
DB_PORT = (
    os.getenv("TEST_DB_PORT") if PYTHON_ENV == "Test" else os.getenv("DB_PORT", None)
)
DB_NAME = (
    os.getenv("TEST_DB_NAME") if PYTHON_ENV == "Test" else os.getenv("DB_NAME", None)
)
DB_URI: str = (
    os.getenv("TEST_DB_URI", None)
    if PYTHON_ENV == "Test"
    else os.getenv("DB_URI", None)
)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LECRAPAUD_LOGFILE = os.getenv("LECRAPAUD_LOGFILE")
LECRAPAUD_LOCAL = os.getenv("LECRAPAUD_LOCAL", False)
LECRAPAUD_TABLE_PREFIX = os.getenv("LECRAPAUD_TABLE_PREFIX", "lecrapaud")
