import os
import sys
import argparse
import logging
import time
import importlib
from logging.handlers import RotatingFileHandler
from adapters.interfaces import Adapter
from common.virtualization.enums import ApplicationStatus


def _init_logging():
    # Initialize Logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')
    handler = RotatingFileHandler('AnimalsAdapter.log', maxBytes=10000, backupCount=10)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    std_handler = logging.StreamHandler(sys.stdout)
    std_handler.setLevel(logging.DEBUG)
    std_handler.setFormatter(formatter)
    logger.addHandler(std_handler)


def parse_arguments():
    """
    Parsing the Command line arguments
    :return: result object with stored parameters
    """
    parser = argparse.ArgumentParser(prog='AdapterRunner', description='Adapter Runner Application')
    parser.add_argument('-a', '--application', action='store', dest='app_name', help='Application Name',
                        metavar='<application_name>')
    parser.add_argument('-fi', '--fetch_interval', action='store', dest='fetch_stats_interval', help='Fetch Stats Interval',
                        metavar='<fetch_interval in seconds>')
    return parser.parse_args()


def load_adapters(plugin_folders):
    for plugin_folder in plugin_folders:
        for root, dirs, files in os.walk(plugin_folder):
            candidates = [fname for fname in files if fname.endswith('.py') and not fname.startswith('__')]
            if candidates:
                for c in candidates:
                    modname = os.path.splitext(c)[0]
                    try:
                        fqn = '{}.{}'.format(root.replace('\\', '.'), modname)
                        module = importlib.import_module(fqn)
                    except (ImportError, NotImplementedError) as e:
                        print(e)


def start(app_name, fetch_interval):

    if not app_name:
        logging.error('App Name is Missing, Exiting')
        return

    adapter = None
    fi = int(fetch_interval)
    try:
        adapter = get_adapter_by_app_name(app_name)
        if not adapter:
            logging.error('Missing Adapter')
            return

        logging.info("Configuring Adapter's Application")
        adapter.configure_application()

        logging.info("Stating Adapter's Application")
        adapter.start_application()

        while True:

            if adapter.application_status is ApplicationStatus.RUNNING:
                logging.info("Fetching Adapter's Application Stats")
                stats = adapter.fetch_application_stats()

                logging.info("Update Adapter's Application Stats in Store")
                adapter.update_application_stats_in_store(stats)

            logging.debug('Sleeping for {}'.format(fi))
            time.sleep(fi)

    except KeyboardInterrupt:
        # This is for the Ctrl+C to end the program
        logging.info('Exiting Application')

    except Exception as ex:
        logging.exception(ex)

    if adapter:
        adapter.stop_application()

    logging.info('Adapter Finished Working')


def get_adapter_by_app_name(app_name):
    for adapter in Adapter.adapters:
        adapter_instance = adapter()
        if adapter_instance.application_name == app_name:
            return adapter_instance
    return None

if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))

    _init_logging()
    result = parse_arguments()

    load_adapters(['adapters'])

    name = result.app_name if result.app_name else os.getenv('ADAPTER_APPLICATION_NAME', None)
    interval = result.fetch_stats_interval if result.fetch_stats_interval else os.getenv('ADAPTER_FETCH_STATS_INTERVAL',
                                                                                         '30')
    start(name, interval)

