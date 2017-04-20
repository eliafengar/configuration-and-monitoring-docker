import os
import logging
from common.database.nosql.mongodb import ProductDAO
from common.virtualization.containers.client import KubernetesClient
from common.virtualization.enums import KubernetesObjects, ApplicationStatus
from adapters.interfaces import Adapter


class KubernetesAdapter(Adapter):

    def __init__(self, app_name=None):
        super().__init__(app_name)
        self._virtualization_client = KubernetesClient()
        self._store_client = ProductDAO(self._application_name)
        self._application_status = ApplicationStatus.SHUT_DOWN

        self._metadata_path = None

        logging.info('Start listening to events')
        self._store_client.add_app_config_change_listener(self._configuration_event_handler)
        self._store_client.add_app_action_change_listener(self._actions_event_handler)

        self._store_client.enable_events()

    def _configuration_event_handler(self, config):
        if config:
            self._parse_and_configure(config)
            self._store_client.set_app_actions({'status': 'restart'})

    def _actions_event_handler(self, actions):
        if actions:
            status = actions['status'] if 'status' in actions else 'stop'
            # Either start or restart will start the application
            if status.endswith('start'):
                self._inner_start_application(actions)
            elif status == 'stop':
                self.stop_application()

    def start_application(self, path='/etc/virtualization/metadata'):
        self._metadata_path = path
        actions = self._store_client.get_app_actions()
        self._inner_start_application(actions)

    def _inner_start_application(self, actions):

        if actions:
            status = actions['status'] if 'status' in actions else 'stop'
            # Either start or restart will start the application
            if not status.endswith('start'):
                logging.info('Application status is {}, will not start application'.format(status))
                return

            if self.application_status is ApplicationStatus.CONFIGURED or self._application_status is ApplicationStatus.RECONFIGURED:

                if not os.path.exists(self._metadata_path):
                    logging.warning('Missing metadata folder')
                    return

                logging.info('Starting Services')
                self._start_application_object(KubernetesObjects.SERVICE,
                                               os.path.join(self._metadata_path, 'services'))

                logging.info('Starting Replication Controller')
                self._start_application_object(KubernetesObjects.REPLICATION_CONTROLLER,
                                               os.path.join(self._metadata_path, 'replication-controllers'))

                logging.info('Starting Pods')
                self._start_application_object(KubernetesObjects.POD,
                                               os.path.join(self._metadata_path, 'pods'))

                self._application_status = ApplicationStatus.RUNNING

                logging.info('Application started successfully')

    def _start_application_object(self, object_type, obj_path):

        if os.path.exists(obj_path):
            files = os.listdir(obj_path)
            for file in files:
                if file.endswith('.json'):
                    self.virtualization_client.start(object_type, os.path.join(obj_path, file), True)

    def configure_application(self):
        logging.info('Fetching current config')
        current_config = self._store_client.get_app_config()
        self._parse_and_configure(current_config)

    def _parse_and_configure(self, config):
        if not config:
            logging.info('Config is empty, skip configuring application')
            return

        # Pass configuration either by call API or by using Kubernetes Persistence Volume
        logging.debug('Configuring application with {}'.format(config))
        if self._application_status is ApplicationStatus.SHUT_DOWN:
            self._application_status = ApplicationStatus.CONFIGURED
        else:
            self._application_status = ApplicationStatus.RECONFIGURED

        logging.info('Application configured successfully')

    def stop_application(self):

        if self._application_status is ApplicationStatus.SHUT_DOWN:
            return

        logging.info('Stopping Replication Controllers')
        self.virtualization_client.stop(KubernetesObjects.REPLICATION_CONTROLLER)

        logging.info('Stopping Pods')
        self.virtualization_client.stop(KubernetesObjects.POD)

        logging.info('Stopping Services')
        self.virtualization_client.stop(KubernetesObjects.SERVICE)

        self._application_status = ApplicationStatus.SHUT_DOWN

        logging.info('Application stopped successfully')

    def fetch_application_stats(self):
        if self._application_status is ApplicationStatus.RUNNING:
            return {'Data': 'Eli Afengar'}

        # Return empty result in case not running
        return {}

    def update_application_stats_in_store(self, stats):
        if stats:
            self._store_client.set_app_stats(stats)
