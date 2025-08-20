from threading import RLock
from typing import Dict, Callable, Any

from sibi_dst.utils import Logger
from .storage_manager import StorageManager
from .credentials import ConfigManager

class StorageConfig:
    def __init__(self, config:ConfigManager, depots:dict=None, clear_existing=False, write_mode="full-access"):
        self.conf = config
        self.depots = depots
        self._initialize_storage()
        self.storage_manager = StorageManager(self.base_storage, self.filesystem_type, self.filesystem_options)
        if self.depots is not None:
            self.depot_paths, self.depot_names = self.storage_manager.rebuild_depot_paths(depots, clear_existing=clear_existing, write_mode=write_mode)
        else:
            self.depot_paths = None
            self.depot_names = None

    def _initialize_storage(self):
        self.filesystem_type = self.conf.get('fs_type','file')
        self.base_storage = self.conf.get('fs_path', "local_storage/")
        if self.filesystem_type == "file":
            self.filesystem_options ={}
        elif self.filesystem_type == "s3":
            self.filesystem_options = {
                "key": self.conf.get('fs_key',''),
                "secret": self.conf.get('fs_secret'),
                "token": self.conf.get('fs_token'),
                "skip_instance_cache":True,
                "use_listings_cache": False,
                "client_kwargs": {
                    "endpoint_url": self.conf.get('fs_endpoint')
                },
                "config_kwargs" :{
                    "signature_version": "s3v4",
                    's3': {
                      'addressing_style': 'path'
                    }
                }
            }
        elif self.filesystem_type == "webdav":
            verify_ssl = self.conf.get('fs_verify_ssl', True)
            # Convert string 'false' to boolean False
            if isinstance(verify_ssl, str) and verify_ssl.lower() == 'false':
                verify_ssl = False
            self.filesystem_options = {
                "base_url": self.conf.get('fs_endpoint', ''),
                "username": self.conf.get('fs_key', ''),
                "password": self.conf.get('fs_secret', ''),
                "token": self.conf.get('fs_token', ''),
                "verify": verify_ssl
            }
        else:
            # unsupported filesystem type
            # defaulting to local filesystem
            self.filesystem_type = 'file'
            self.filesystem_options = {}
        self.filesystem_options = {k: v for k, v in self.filesystem_options.items() if v}

class FsRegistry:
    def __init__(self, debug: bool = False, logger: Logger = None):
        self._storage_registry: Dict[str, Callable[[], Any]]={}
        self._fs_instance_cache: Dict[str, object] = {}
        self._lock = RLock()
        self.debug = debug

        if logger:
            self.logger = logger
        else:
            self.logger = Logger.default_logger(logger_name="FsRegistry")
            self.logger.set_level(Logger.DEBUG if self.debug else Logger.INFO)

    def register(self, name:str, manager: Any):
        """
        Registers a filesystem manager instance with a name.
        :param name: Name of the filesystem instance.
        :param manager: Filesystem manager instance to register.
        """
        if not hasattr(manager, 'get_fs_instance'):
            raise TypeError("Manager must have a 'get_fs_instance' method.")
        self._storage_registry[name] = lambda: manager


    def get_fs_instance(self, name: str='source') -> object:
        """
        Retrieve a filesystem instance from a registered storage manager.
        Caches instances per name.
        """
        if name in self._fs_instance_cache:
            return self._fs_instance_cache[name]

        if name not in self._storage_registry:
            raise ValueError(f"Storage '{name}' has not been registered.")

        manager = self._storage_registry[name]()
        fs = manager.get_fs_instance()
        self._fs_instance_cache[name] = fs
        return fs

    def unregister_fs(self, name: str):
        """
        Unregister a storage and clear its cached fs instance.
        """
        self._storage_registry.pop(name, None)
        self._fs_instance_cache.pop(name, None)


    def clear_fs_cache(self):
        """
        Clear all cached fs instances.
        """
        self._fs_instance_cache.clear()