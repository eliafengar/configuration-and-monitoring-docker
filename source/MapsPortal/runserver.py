import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from app import app


def run():
    # Initialize Logger
    logger = logging.getLogger()
    formatter = logging.Formatter('[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')
    handler = RotatingFileHandler('maps-portal.log', maxBytes=10000, backupCount=10)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    std_handler = logging.StreamHandler(sys.stdout)
    std_handler.setLevel(logging.DEBUG)
    std_handler.setFormatter(formatter)
    logger.addHandler(std_handler)

    server_port = int(os.getenv('SERVER_PORT', '9000'))

    app.run(host='0.0.0.0', port=server_port, debug=True)


if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))
    run()