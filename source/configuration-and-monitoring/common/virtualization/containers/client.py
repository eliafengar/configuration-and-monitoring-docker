import os
import logging
import json
import shutil
from pykube import HTTPClient, KubeConfig, Pod, Service, ReplicationController
from common.virtualization.enums import KubernetesObjects
from common.virtualization.interfaces import VirtualizationClient


class KubernetesClient(VirtualizationClient):
    def __init__(self):
        logging.info('Getting Kubernetes HTTPClient')
        try:
            #if not os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'):
            #    logging.debug('Stat Kube Config from /serviceaccount')
            #    shutil.copytree('/var/run/secrets/kubernetes.io/serviceaccount', '/serviceaccount')
            #    shutil.copyfile('/ca.crt', '/serviceaccount/ca.crt')
            #    self.api = HTTPClient(KubeConfig.from_service_account('/serviceaccount'))
            #else:
            #    logging.debug('Staty Kube Config from /var/run/secrets/kubernetes.io/serviceaccount')
            self.api = HTTPClient(KubeConfig.from_service_account())
        except Exception as ex:
            logging.exception('Error Getting Kubernetes HTTPClient using ServiceAccount')

            logging.info('Trying with URL')
            kube_host = os.getenv('KUBERNETES_PROXY_API_HOST', '127.0.0.1')
            kube_port = os.getenv('KUBERNETES_PROXY_API_PORT', '8080')
            logging.info('Kubernetes Host: {}, Kubernetes Port: {}'.format(kube_host, kube_port))
            try:
                self.api = HTTPClient(KubeConfig.from_url('http://{}:{}'.format(kube_host, kube_port)))
            except Exception as ex:
                logging.exception('Error Getting Kubernetes HTTPClient using URL')
                self.api = None

        self.kube_objects = {}

    def start(self, object_type, object_file_path, force=False):

        if not self.api:
            logging.info('API Client does not exist')
            return

        with open(object_file_path) as json_data:
            json_file = json.load(json_data)

        if object_type is KubernetesObjects.POD:

            pod = Pod(self.api, json_file)
            self._recreate_object(pod, force)
            self._add_object_to_kube_objects_dict('pods', pod)

        elif object_type is KubernetesObjects.SERVICE:

            service = Service(self.api, json_file)
            self._recreate_object(service, force)
            self._add_object_to_kube_objects_dict('services', service)

        elif object_type is KubernetesObjects.REPLICATION_CONTROLLER:

            rc = ReplicationController(self.api, json_file)
            self._recreate_object(rc, force)
            self._add_object_to_kube_objects_dict('rcs', rc)

    def _recreate_object(self, obj, force=False):
        if force:
            if obj.exists():
                obj.delete()
            # Wait till the object terminated successfully
            while obj.exists():
                pass
            obj.create()
        else:
            if not obj.exists():
                obj.create()

    def _add_object_to_kube_objects_dict(self, key, value):
        if key not in self.kube_objects:
            self.kube_objects[key] = []
        self.kube_objects[key].append(value)

    def stop(self, object_type, name=None):

        if not self.api:
            logging.info('API Client does not exist')
            return

        if object_type is KubernetesObjects.POD:
            kube_obj_list = self.kube_objects['pods'] if 'pods' in self.kube_objects else []
        elif object_type is KubernetesObjects.SERVICE:
            kube_obj_list = self.kube_objects['services'] if 'services' in self.kube_objects else []
        elif object_type is KubernetesObjects.REPLICATION_CONTROLLER:
            kube_obj_list = self.kube_objects['rcs'] if 'rcs' in self.kube_objects else []

        for obj in kube_obj_list:
            if obj.name == name or not name:
                obj.delete()

    def check_application_status(self, app_name):
        pass
