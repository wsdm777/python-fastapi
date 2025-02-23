import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = "db"
DB_PORT = "5432"
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
SUPERUSER_EMAIL = os.environ.get("SUPERUSER_EMAIL")
SUPERUSER_PASSWORD = os.environ.get("SUPERUSER_PASSWORD")
TEST_URL = os.environ.get("TEST_URL")
REDIS_HOST = "redis"
REDIS_PORT = "6379"
