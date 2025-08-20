from types import SimpleNamespace

import fsspec
from .webdav_client import WebDAVClient

class StorageManager:
    def __init__(self, storage_path, fs_type="file", fs_options=None, debug=False):
        """
        Initializes the StorageManager with the base storage path and file system settings.
        :param storage_path: Base path for the storage (e.g., "s3://my-bucket").
        :param fs_type: File system type (e.g., "file", "s3").
        :param fs_options: Dictionary of options for fsspec file system (e.g., credentials).
        """
        self.debug = debug
        # Ensure the storage_path ends with a slash for consistency
        self.storage_path = storage_path.rstrip("/")
        self.fs_type = fs_type
        self.fs_options = fs_options or {}
        if fs_type == "webdav":
            self._initialize_webdav()
        else:
            self.fs = fsspec.filesystem(fs_type, **self.fs_options)

        self.depot_paths = {}
        self.depot_name = None

    def _initialize_webdav(self):
        """
        Initialize WebDAV filesystem using the WebDAVClient.
        """
        base_url = self.fs_options.get("base_url", "")
        username = self.fs_options.get("username", "")
        password = self.fs_options.get("password", "")
        token = self.fs_options.get("token", "")
        # Convert string 'false' to boolean False
        verify = self.fs_options.get("verify", True)
        if isinstance(verify, str) and verify.lower() == 'false':
            verify = False

        # Create WebDAV client
        self.webdav_client = WebDAVClient(
            base_url=base_url,
            username=username,
            password=password,
            token=token,
            verify=verify
        )

        # Use the fsspec-compatible filesystem
        self.fs = self.webdav_client.get_fs()
    @staticmethod
    def join_paths(*parts):
        """
        Joins paths using '/' as a separator, compatible with remote file systems.
        """
        return "/".join(part.strip("/") for part in parts)

    def setup_directories(self, base_path, dirs_to_create, clear_existing=False):
        """
        Creates directories using fsspec given a base path and a list of subdirectories.
        Optionally clears existing directories with safeguards.
        :param base_path: The base path where directories are created.
        :param dirs_to_create: List of subdirectories to create.
        :param clear_existing: Whether to clear existing directories.
        """
        if self.debug:
            print(f"Setting up directories under: {base_path}")
        if clear_existing:
            if self.debug:
                print(f"Warning: All existing contents in {base_path} will be removed.")
            if self.fs.exists(base_path):
                self.fs.rm(base_path, recursive=True)

        # Create the base path
        self.fs.mkdirs(base_path, exist_ok=True)

        # Create subdirectories
        for sub_directory in dirs_to_create:
            sub_path = self.join_paths(base_path, sub_directory)
            if self.debug:
                print(f"Creating directory: {sub_path}")
            if clear_existing and self.fs.exists(sub_path):
                self.fs.rm(sub_path, recursive=True)
            self.fs.mkdirs(sub_path, exist_ok=True)

    def rebuild_depot_paths(self, depots, clear_existing=False, write_mode="full-access"):
        """
        Rebuilds depot_paths (dictionary) and depot_name (SimpleNamespace).
        Handles clear_existing scenario by resetting directories when required.
        :param depots: Dictionary where keys are depot names and values are subdirectory lists.
        :param clear_existing: Whether to clear existing directories.
        :return: Tuple of depot_paths (dictionary) and depot_name (SimpleNamespace).
        """
        # Ensure directories exist (optionally clear existing ones)
        for depot, sub_directories in depots.items():
            depot_path = self.join_paths(self.storage_path, depot)
            if self.debug:
                print(f"Rebuilding depot at: {depot_path}")
            if write_mode == "full-access":
                self.setup_directories(depot_path, sub_directories, clear_existing=clear_existing)

        # Generate depot_paths dictionary
        self.depot_paths = {
            depot: {sub: self.join_paths(self.storage_path, depot, sub) for sub in sub_directories}
            for depot, sub_directories in depots.items()
        }

        # Convert depot_paths to a nested SimpleNamespace
        self.depot_name = SimpleNamespace(
            **{
                depot: SimpleNamespace(**sub_dirs)
                for depot, sub_dirs in self.depot_paths.items()
            }
        )

        return self.depot_paths, self.depot_name

    def rebuild(self, depots, clear_existing=False):
        """
        Public method to clear and rebuild the depot structure.
        Calls rebuild_depot_paths internally and resets depot paths and names.
        :param depots: Dictionary where keys are depot names and values are subdirectory lists.
        :param clear_existing: Whether to clear existing directories.
        """
        if self.debug:
            print("Rebuilding depot structure...")
        self.rebuild_depot_paths(depots, clear_existing=clear_existing)
        if self.debug:
            print("Rebuild complete.")

    def get_fs_instance(self):
        """
        Returns the filesystem instance.
        """
        if self.fs_type == "webdav":
            return self.fs
        else:
            return fsspec.filesystem(self.fs_type, **self.fs_options)

    def upload_file(self, local_path, remote_path):
        """
        Upload a file to the storage.

        :param local_path: Local file path
        :param remote_path: Remote file path
        """
        if self.fs_type == "webdav":
            # Use the WebDAV client's upload method for WebDAV
            self.webdav_client.upload_file(local_path, remote_path)
        else:
            # Use fsspec's put method for other filesystems
            self.fs.put(local_path, remote_path)

    def download_file(self, remote_path, local_path):
        """
        Download a file from the storage.

        :param remote_path: Remote file path
        :param local_path: Local file path
        """
        if self.fs_type == "webdav":
            # Use the WebDAV client's download method for WebDAV
            self.webdav_client.download_file(remote_path, local_path)
        else:
            # Use fsspec's get method for other filesystems
            self.fs.get(remote_path, local_path)
