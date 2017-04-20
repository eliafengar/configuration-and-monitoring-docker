from abc import ABCMeta, abstractmethod


class VirtualizationClient(metaclass=ABCMeta):

    def __init__(self):
        pass

    @abstractmethod
    def check_application_status(self, app_name):
        pass

    @abstractmethod
    def start(self, object_type, object_file_path, force=False):
        pass

    @abstractmethod
    def stop(self, object_type, name):
        pass
