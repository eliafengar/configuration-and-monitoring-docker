import logging
from logging.handlers import RotatingFileHandler
import sys
import os

sys.path.insert(0, '/var/www/configuration-and-monitor')
os.chdir('/var/www/configuration-and-monitor')

# Initialize Logger
logger = logging.getLogger()
formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
handler = RotatingFileHandler('Animals.log', maxBytes=10000, backupCount=10)
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger.addHandler(handler)

from server import app as application
