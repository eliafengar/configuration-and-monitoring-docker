from abc import ABCMeta, abstractmethod


class AdapterMeta(ABCMeta):
    def __init__(cls, name, bases, namespace):
        super(ABCMeta, cls).__init__(name, bases, namespace)
        if not hasattr(cls, 'adapters'):
            cls.adapters = []
        else:
            cls.adapters.append(cls)


class Adapter(metaclass=AdapterMeta):
    """
    An Interface for the Adapters
    """

    def __init__(self, app_name=None):
        self._virtualization_client = None
        self._store_client = None
        self._application_name = app_name
        self._application_status = None

    @property
    def application_name(self):
        return self._application_name

    @property
    def virtualization_client(self):
        return self._virtualization_client

    @property
    def store_client(self):
        return self._store_client

    @property
    def application_status(self):
        """
        Gets the application status
        :return: ApplicationStatus Enum
        """
        return self._application_status

    @abstractmethod
    def start_application(self):
        """
        Starting an application in Container or Virtual Machine
        Either directly to Docker engine or by using Kubernetes
        :return:
        """

    @abstractmethod
    def configure_application(self):
        """
        Configuring the Application
        Either by calling a REST/SOAP API or Pass Files by FTP or by Kubernetes Persistence volume
        :return:
        """

    @abstractmethod
    def stop_application(self):
        """
        Stopping the application
        :return:
        """

    @abstractmethod
    def fetch_application_stats(self):
        """
        Fetching the monitoring data
        :return: Dictionary (JSON)
        """

    @abstractmethod
    def update_application_stats_in_store(self, stats):
        """
        Update the returned monitoring data in the database store
        :return:
        """
