import logging
from datetime import date

level = logging.DEBUG
name = "Logger"
today_date = date.today()
log_file = f"app_{today_date}.log"

handler = logging.FileHandler(log_file)
handler.setLevel(level)

dateformat = "%Y-%m-%d %H:%M:%S"

formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] --- %(message)s (%(filename)s:%(lineno)s)",
    datefmt=dateformat,
)
handler.setFormatter(formatter)

logger = logging.getLogger(name)
logger.setLevel(level)
logger.addHandler(handler)
