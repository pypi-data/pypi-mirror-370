from devvio_util.lib_creds import Loader


class ConfigManager:
    """Manages configuration parameters"""

    _instance = None

    def __init__(self, *args, **kwargs):
        self._cm_map = {}

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def update(self, category, secret_name, kvs: Loader):
        self._cm_map.update({category: kvs.get_secrets(secret_name)})

    def get(self, category):
        return self._cm_map.get(category)
