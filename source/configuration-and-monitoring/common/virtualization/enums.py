from enum import Enum


class ApplicationStatus(Enum):
    SHUT_DOWN = 1,
    CONFIGURED = 2,
    RECONFIGURED = 3,
    RUNNING = 4


class KubernetesObjects(Enum):
    POD = 1,
    SERVICE = 2,
    REPLICATION_CONTROLLER = 3


class KVMObjects(Enum):
    DOMAIN = 1
