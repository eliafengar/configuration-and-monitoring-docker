import os
import logging
from common.database.nosql.mongodb import ProductDAO
from common.virtualization.virtual_machines.client import KVMClient
from common.virtualization.enums import ApplicationStatus, KVMObjects
from adapters.interfaces import Adapter


class KVMAdapter(Adapter):

    def __init__(self, app_name=None):
        super().__init__(app_name)
        self._virtualization_client = KVMClient()
        self._store_client = ProductDAO(self._application_name)
        self._application_status = ApplicationStatus.SHUT_DOWN

    def start_application(self, path='/etc/virtualization/metadata'):

        if not os.path.exists(path):
            logging.warning('Missing metadata folder')
            return

        self._virtualization_client.start(KVMObjects.DOMAIN, None)

        self._application_status = ApplicationStatus.STARTED

        logging.info('Application started successfully')

    def configure_application(self):
        logging.info('Fetching current config')
        self._parse_and_configure(self._store_client.get_app_config())

        logging.info('Start listening to config events')
        method = self.get_method_for_configuration_events()
        self._store_client.add_app_config_change_listener(method)
        self._store_client.enable_events()

    def get_method_for_configuration_events(self):
        return None

    def stop_application(self):

        if self._application_status is ApplicationStatus.SHUT_DOWN:
            return

        self._virtualization_client.stop(KVMObjects.DOMAIN, None)

        self._application_status = ApplicationStatus.SHUT_DOWN

        logging.info('Application stopped successfully')

    def fetch_application_stats(self):
        return {}

    def update_application_stats_in_store(self, stats):
        self._store_client.set_app_stats(stats)
