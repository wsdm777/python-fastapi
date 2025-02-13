import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
SUPER_USER_EMAIL = os.environ.get("SUPER_USER_EMAIL")
SUPER_USER_PASSWORD = os.environ.get("SUPERUSER_PASSWORD")
TEST_URL = os.environ.get("TEST_URL")
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")
