from adapters.containers.adapters import KubernetesAdapter


class TigerAdapter(KubernetesAdapter):

    def __init__(self):
        super().__init__('tiger')
