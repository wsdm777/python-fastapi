import logging
from datetime import date
import os


log_dir = "/app/logs"
os.makedirs(log_dir, exist_ok=True)
today_date = date.today()
log_file = os.path.join(log_dir, f"app_{today_date}.log")
level = logging.DEBUG
name = "Logger"

handler = logging.FileHandler(log_file)
handler.setLevel(level)

dateformat = "%Y-%m-%d %H:%M:%S"


class CustomFormatter(logging.Formatter):
    def format(self, record):
        parent_folder = os.path.basename(os.path.dirname(record.pathname))
        record.file_with_folder = f"{parent_folder}/{os.path.basename(record.pathname)}"
        return super().format(record)


formatter = CustomFormatter(
    "[%(asctime)s] [%(levelname)s] --- %(message)s (%(file_with_folder)s:%(lineno)s)",
    datefmt=dateformat,
)
handler.setFormatter(formatter)

logger = logging.getLogger(name)
logger.setLevel(level)
logger.addHandler(handler)
