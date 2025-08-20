"""
WebDAV client implementation for storage manager.
"""
from __future__ import annotations

from pathlib import PurePosixPath
from typing import Optional, Tuple, Union, Iterable

from webdav4.client import Client, ResourceNotFound
from webdav4.fsspec import WebdavFileSystem


def _normalize_base_url(url: str) -> str:
    # webdav4 accepts trailing slash; normalize to one
    url = url.strip()
    return url if url.endswith("/") else url + "/"


def _normpath(path: str) -> str:
    # Ensure POSIX path semantics (WebDAV paths are POSIX-like)
    # Remove duplicate slashes but keep leading slash if present
    p = str(PurePosixPath("/" + path.strip("/")))
    return p[1:] if not path.startswith("/") else p


class WebDAVClient:
    """
    WebDAV client wrapper for interacting with WebDAV servers (e.g., Nextcloud).

    - Uses webdav4.Client for high-level ops and WebdavFileSystem (fsspec) for path utilities.
    - Provides fsspec-compatible aliases: ls, rm, mkdir, makedirs.
    - Prefer fs methods for filesystem ops (exists, makedirs, copy, open).
    """

    def __init__(
        self,
        base_url: str,
        *,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        verify: Union[bool, str] = True,
        timeout: Optional[float] = None,
    ) -> None:
        """
        :param base_url: e.g. "https://host/remote.php/dav/files/user/"
        :param username: Basic auth username (ignored if token is provided)
        :param password: Basic auth password
        :param token: Bearer/token auth (passed as `auth=token`)
        :param verify: bool or path to CA bundle; "false" (str) treated as False
        :param timeout: Optional default timeout (seconds) for client requests
        """
        self.base_url = _normalize_base_url(base_url)

        # verify may arrive as 'false' string
        if isinstance(verify, str) and verify.lower() == "false":
            verify = False
        self.verify = verify

        # auth precedence: token -> (username, password) -> None
        if token:
            self.auth: Union[str, Tuple[str, str], None] = token
        elif username and password:
            self.auth = (username, password)
        else:
            self.auth = None

        # Core clients
        self.client = Client(self.base_url, auth=self.auth, verify=self.verify, timeout=timeout)
        self.fs = WebdavFileSystem(self.base_url, auth=self.auth, verify=self.verify, timeout=timeout)

    # ---------- convenience ----------

    def _p(self, path: str) -> str:
        """Normalize a relative/absolute path to WebDAV format."""
        return _normpath(path)

    # ---------- existence / listing ----------

    def exists(self, path: str) -> bool:
        """Return True if the resource exists."""
        try:
            return bool(self.fs.exists(self._p(path)))
        except Exception:
            return False

    def list_directory(self, path: str = "", detail: bool = False):
        """
        List contents of a directory. Returns [] (or {}) if not found.
        """
        p = self._p(path)
        try:
            return self.fs.ls(p, detail=detail)
        except FileNotFoundError:
            return [] if not detail else {}
        except ResourceNotFound:
            return [] if not detail else {}

    # ---------- directory creation ----------

    def ensure_directory_exists(self, path: str) -> None:
        """
        Create a directory and parents if needed (idempotent).
        """
        p = self._p(path)
        # WebdavFileSystem implements makedirs(exist_ok=True)
        self.fs.makedirs(p, exist_ok=True)

    def create_directory(self, path: str) -> None:
        self.ensure_directory_exists(path)

    # ---------- file transfer ----------

    def upload_file(self, local_path: str, remote_path: str) -> None:
        parent = PurePosixPath(self._p(remote_path)).parent.as_posix()
        if parent and parent not in (".", "/"):
            self.ensure_directory_exists(parent)
        # client supports upload_file(local, remote)
        self.client.upload_file(local_path, self._p(remote_path))

    def download_file(self, remote_path: str, local_path: str) -> None:
        self.client.download_file(self._p(remote_path), local_path)

    # ---------- deletion ----------

    def delete(self, path: str, recursive: bool = False) -> None:
        p = self._p(path)
        try:
            # fs.rm handles both files and directories
            self.fs.rm(p, recursive=recursive)
        except FileNotFoundError:
            pass
        except ResourceNotFound:
            pass

    # ---------- fsspec-like aliases ----------

    def get_fs(self) -> WebdavFileSystem:
        return self.fs

    def mkdir(self, path: str, create_parents: bool = True) -> None:
        if create_parents:
            self.ensure_directory_exists(path)
        else:
            # fsspec's mkdir usually creates a single level
            self.fs.mkdir(self._p(path))

    def ls(self, path: str = "", detail: bool = False):
        return self.list_directory(path, detail=detail)

    def rm(self, path: str, recursive: bool = False) -> None:
        self.delete(path, recursive=recursive)

    def makedirs(self, path: str, exist_ok: bool = True) -> None:
        p = self._p(path)
        self.fs.makedirs(p, exist_ok=exist_ok)

    # ---------- context manager ----------

    def __enter__(self) -> "WebDAVClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        # webdav4 clients don’t require explicit close, but fsspec may hold pools
        try:
            close = getattr(self.fs, "close", None)
            if callable(close):
                close()
        except Exception:
            pass