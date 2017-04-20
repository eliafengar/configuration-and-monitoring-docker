from common.virtualization.enums import KVMObjects
from common.virtualization.interfaces import VirtualizationClient


class KVMClient(VirtualizationClient):

    def __init__(self):
        pass

    def check_application_status(self, app_name):
        pass

    def start(self, object_type, object_file_path, force=False):

        if object_type is KVMObjects.DOMAIN:
            pass

    def stop(self, object_type, name):
        pass
