import datetime as _dt
from typing import Tuple, List, Optional, Dict, Any

import fsspec

from .log_utils import Logger


class FileAgeChecker:
    """
    Check file/directory "age" (minutes since last modification) using fsspec.

    Backward compatible methods:
      - is_file_older_than(file_path, max_age_minutes, fs=None, ignore_missing=False, verbose=False) -> bool
      - get_file_or_dir_age_minutes(file_path, fs=None) -> float

    Enhancements:
      - dir_policy: 'oldest' | 'newest' | 'mean' when evaluating directories
      - recursive: recurse into subdirectories using fs.find()
      - robust mtime extraction for local/S3/FTP-like backends
      - grace_minutes: optional slack for threshold comparisons
    """

    _UTC = _dt.timezone.utc

    def __init__(
            self,
            debug: bool = False,
            logger: Optional[Logger] = None,
            *,
            dir_policy: str = "oldest",  # 'oldest' (legacy), 'newest', or 'mean'
            recursive_default: bool = False,
    ):
        self.logger = logger or Logger.default_logger(logger_name=self.__class__.__name__)
        self.logger.set_level(Logger.DEBUG if debug else Logger.INFO)

        if dir_policy not in {"oldest", "newest", "mean"}:
            raise ValueError("dir_policy must be one of: 'oldest', 'newest', 'mean'")
        self.dir_policy = dir_policy
        self.recursive_default = recursive_default

    # ---------------- Public API ----------------

    def is_file_older_than(
            self,
            file_path: str,
            max_age_minutes: float,
            fs: Optional[fsspec.AbstractFileSystem] = None,
            ignore_missing: bool = False,
            verbose: bool = False,
            *,
            recursive: Optional[bool] = None,
            dir_policy: Optional[str] = None,
            grace_minutes: float = 0.0,
    ) -> bool:
        """
        Return True if file/dir age (in minutes) is greater than the threshold.

        :param file_path: Path to the file or directory.
        :param max_age_minutes: Maximum allowed "age" in minutes.
        :param fs: Filesystem object (defaults to local 'file' fs).
        :param ignore_missing: If True, missing paths are treated as NOT old.
        :param verbose: Log extra details.
        :param recursive: Recurse into subdirectories (defaults to instance setting).
        :param dir_policy: 'oldest' | 'newest' | 'mean' (defaults to instance policy).
        :param grace_minutes: Threshold slack; if provided, we compare against
                              (max_age_minutes - grace_minutes), floored at 0.
        """
        fs = fs or fsspec.filesystem("file")
        use_recursive = self.recursive_default if recursive is None else bool(recursive)
        policy = dir_policy or self.dir_policy

        try:
            if not fs.exists(file_path):
                if verbose:
                    self.logger.debug(f"Path not found: {file_path}")
                return False if ignore_missing else True

            age = self.get_file_or_dir_age_minutes(
                file_path, fs=fs, recursive=use_recursive, dir_policy=policy, verbose=verbose
            )
            threshold = max(0.0, float(max_age_minutes) - float(grace_minutes))
            if verbose:
                self.logger.debug(
                    f"Age check for {file_path}: age={age:.2f} min, "
                    f"threshold={threshold:.2f} min (policy={policy}, recursive={use_recursive})"
                )
            return age > threshold

        except Exception as e:
            # On errors, be conservative and consider it old (legacy behavior)
            self.logger.warning(f"Error checking {file_path}: {e}")
            return True

    def get_file_or_dir_age_minutes(
            self,
            file_path: str,
            fs: Optional[fsspec.AbstractFileSystem] = None,
            *,
            recursive: Optional[bool] = None,
            dir_policy: Optional[str] = None,
            verbose: bool = False,
    ) -> float:
        """
        Compute the age (minutes since last modification timestamp) for a file or directory.

        For directories, applies `dir_policy`:
          - 'oldest' : age of the OLDEST file (max age)  [legacy default]
          - 'newest' : age since the MOST RECENT file update (min age)
          - 'mean'   : average age across files

        Returns float('inf') for missing paths, invalid path types, or on errors.
        """
        fs = fs or fsspec.filesystem("file")
        use_recursive = self.recursive_default if recursive is None else bool(recursive)
        policy = dir_policy or self.dir_policy

        try:
            if not fs.exists(file_path):
                if verbose:
                    self.logger.debug(f"Path not found: {file_path}")
                return float("inf")

            if fs.isdir(file_path):
                return self._get_directory_age_minutes(
                    file_path, fs, verbose=verbose, recursive=use_recursive, policy=policy
                )
            if fs.isfile(file_path):
                return self._get_file_age_minutes(file_path, fs, verbose=verbose)

            self.logger.warning(f"Invalid path type (neither file nor dir): {file_path}")
            return float("inf")

        except Exception as e:
            self.logger.warning(f"Error getting age for {file_path}: {e}")
            return float("inf")

    # ---------------- Internals ----------------

    def _now_utc(self) -> _dt.datetime:
        return _dt.datetime.now(self._UTC)

    def _get_directory_age_minutes(
            self,
            dir_path: str,
            fs: fsspec.AbstractFileSystem,
            *,
            verbose: bool,
            recursive: bool,
            policy: str,
    ) -> float:
        """Compute directory age using the chosen policy."""
        try:
            paths = self._list_files(dir_path, fs, recursive=recursive)
        except Exception as e:
            self.logger.warning(f"Error listing {dir_path}: {e}")
            return float("inf")

        if not paths:
            if verbose:
                self.logger.debug(f"Empty directory: {dir_path}")
            return float("inf")

        ages: List[float] = []
        for p in paths:
            try:
                info = fs.info(p)
                mt = self._extract_mtime_utc(info, p)
                if mt is None:
                    continue
                age_min = (self._now_utc() - mt).total_seconds() / 60.0
                ages.append(age_min)
            except Exception as e:
                # Skip problem files but continue
                self.logger.debug(f"Skipping {p}: {e}")

        if not ages:
            self.logger.warning(f"No valid files with mtime in {dir_path}")
            return float("inf")

        if policy == "oldest":
            chosen = max(ages)  # age of oldest file
        elif policy == "newest":
            chosen = min(ages)  # since most recent update
        elif policy == "mean":
            chosen = sum(ages) / len(ages)
        else:
            raise ValueError(f"Unknown dir_policy: {policy}")

        if verbose:
            self.logger.debug(
                f"Directory age ({policy}) for {dir_path}: {chosen:.2f} minutes "
                f"from {len(ages)} files (recursive={recursive})"
            )
        return chosen

    def _get_file_age_minutes(
            self,
            file_path: str,
            fs: fsspec.AbstractFileSystem,
            *,
            verbose: bool,
    ) -> float:
        """Age for a single file in minutes."""
        info = fs.info(file_path)
        mt = self._extract_mtime_utc(info, file_path)
        if mt is None:
            if verbose:
                self.logger.debug(f"Missing/invalid mtime for {file_path} (info: {info})")
            return float("inf")
        age = (self._now_utc() - mt).total_seconds() / 60.0
        if verbose:
            self.logger.debug(f"File age for {file_path}: {age:.2f} minutes")
        return age

    def _list_files(
            self,
            dir_path: str,
            fs: fsspec.AbstractFileSystem,
            *,
            recursive: bool,
    ) -> List[str]:
        """
        Return a list of file paths inside dir_path.
        Uses fs.find() if recursive else fs.ls(); filters out directories.
        """
        if recursive and hasattr(fs, "find"):
            found = fs.find(dir_path)
            # Some fs.find implementations return only files; still filter defensively
            return [p for p in (found or []) if self._is_file(fs, p)]
        else:
            items = fs.ls(dir_path)
            return [p for p in (items or []) if self._is_file(fs, p)]

    def _is_file(self, fs: fsspec.AbstractFileSystem, path: str) -> bool:
        try:
            return fs.isfile(path)
        except Exception:
            # Some backends: rely on info['type']
            try:
                info = fs.info(path)
                return info.get("type") == "file"
            except Exception:
                return False

    def _extract_mtime_utc(self, info: Dict[str, Any], path: str) -> Optional[_dt.datetime]:
        """
        Normalize an mtime from fsspec info to a timezone-aware UTC datetime.
        Supports common keys across local/S3/FTP-ish backends.
        """
        # 1) S3-like
        if "LastModified" in info:
            lm = info["LastModified"]
            if isinstance(lm, _dt.datetime):
                return lm if lm.tzinfo else lm.replace(tzinfo=self._UTC)
            if isinstance(lm, str):
                # Try ISO; honor trailing 'Z'
                s = lm.replace("Z", "+00:00") if lm.endswith("Z") else lm
                try:
                    dt = _dt.datetime.fromisoformat(s)
                    return dt if dt.tzinfo else dt.replace(tzinfo=self._UTC)
                except ValueError:
                    pass

        # 2) Local/posix fsspec
        if "mtime" in info:
            mt = info["mtime"]
            try:
                # fsspec local often returns float seconds
                ts = float(mt)
                return _dt.datetime.fromtimestamp(ts, tz=self._UTC)
            except (TypeError, ValueError):
                # Sometimes mtime is an ISO string
                if isinstance(mt, str):
                    s = mt.replace("Z", "+00:00") if mt.endswith("Z") else mt
                    try:
                        dt = _dt.datetime.fromisoformat(s)
                        return dt if dt.tzinfo else dt.replace(tzinfo=self._UTC)
                    except ValueError:
                        pass

        # 3) FTP/SSH style
        for k in ("modified", "last_modified", "updated"):
            if k in info and isinstance(info[k], str):
                val = info[k]
                # Try common "%Y-%m-%d %H:%M:%S" first, then ISO
                try:
                    dt = _dt.datetime.strptime(val, "%Y-%m-%d %H:%M:%S").replace(tzinfo=self._UTC)
                    return dt
                except ValueError:
                    s = val.replace("Z", "+00:00") if val.endswith("Z") else val
                    try:
                        dt = _dt.datetime.fromisoformat(s)
                        return dt if dt.tzinfo else dt.replace(tzinfo=self._UTC)
                    except ValueError:
                        continue

        # If nothing matched, log once at debug level
        self.logger.debug(f"No usable mtime in info for {path}: {info}")
        return None

