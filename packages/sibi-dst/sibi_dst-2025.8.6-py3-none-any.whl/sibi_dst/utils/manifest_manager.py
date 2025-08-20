import pandas as pd
import fsspec
import threading
import uuid
from typing import List, Optional, Set, Dict, Any

from sibi_dst.utils import Logger


class MissingManifestManager:
    """
    Thread-safe manager for a Parquet file manifest of missing partitions.

    - Atomic writes via temp → copy → remove
    - Cleans up orphan temp files (best-effort)
    - Stores a simple table with a single column: 'path'
    """

    def __init__(
        self,
        fs: fsspec.AbstractFileSystem,
        manifest_path: str,
        clear_existing: bool = False,
        **kwargs: Any,
    ):
        self.fs: fsspec.AbstractFileSystem = fs
        self.manifest_path: str = manifest_path.rstrip("/")
        self.clear_existing: bool = clear_existing
        self.clear_existing: bool = clear_existing
        self.ignore_missing: bool = kwargs.get("ignore_missing", False)
        if self.clear_existing:
            self.ignore_missing = False
        self.debug: bool = kwargs.get("debug", False)
        self.logger: Logger = kwargs.get(
            "logger",
            Logger.default_logger(logger_name="missing_manifest_manager"),
        )
        self.logger.set_level(Logger.DEBUG if self.debug else Logger.INFO)

        self._new_records: List[Dict[str, str]] = []
        self._loaded_paths: Optional[Set[str]] = None
        self._lock = threading.Lock()

        # Clean up any orphaned temp files from previous failed runs (best-effort)
        self._cleanup_orphaned_files()

    def _safe_exists(self, path: str) -> bool:
        """Safely check if a path exists, handling potential exceptions."""
        try:
            return self.fs.exists(path)
        except Exception as e:
            self.logger.warning(f"Error checking existence of '{path}': {e}")
            return False

    def load_existing(self) -> Set[str]:
        """
        Loads the set of paths from the existing manifest file into memory.
        Returns an empty set if not found or unreadable.
        """
        with self._lock:
            if self._loaded_paths is not None:
                return self._loaded_paths

            if not self._safe_exists(self.manifest_path):
                self._loaded_paths = set()
                return self._loaded_paths

            try:
                df = pd.read_parquet(self.manifest_path, filesystem=self.fs)
                paths = (
                    df.get("path", pd.Series(dtype=str))
                    .dropna().astype(str)
                    .loc[lambda s: s.str.strip().astype(bool)]
                )
                self._loaded_paths = set(paths.tolist())
            except Exception as e:
                self.logger.warning(
                    f"Failed to load manifest '{self.manifest_path}', "
                    f"treating as empty. Error: {e}"
                )
                self._loaded_paths = set()

            return self._loaded_paths

    def record(self, full_path: str) -> None:
        """
        Records a new path to be added to the manifest upon the next save.
        """
        if not full_path or not isinstance(full_path, str):
            return
        with self._lock:
            self._new_records.append({"path": full_path})

    def save(self) -> None:
        """
        Saves all new records to the manifest file atomically.
        """
        with self._lock:
            if not self._new_records and not self.clear_existing:
                self.logger.debug("Manifest Manager: No new records to save.")
                return

            new_df = pd.DataFrame(self._new_records)
            new_df = (
                new_df.get("path", pd.Series(dtype=str))
                .dropna().astype(str)
                .loc[lambda s: s.str.strip().astype(bool)]
                .to_frame(name="path")
            )

            # Determine the final DataFrame to be written
            should_overwrite = self.clear_existing or not self._safe_exists(self.manifest_path)
            if should_overwrite:
                out_df = new_df
            else:
                try:
                    old_df = pd.read_parquet(self.manifest_path, filesystem=self.fs)
                    out_df = pd.concat([old_df, new_df], ignore_index=True)
                except Exception as e:
                    self.logger.warning(f"Could not read existing manifest to merge, overwriting. Error: {e}")
                    out_df = new_df

            out_df = out_df.drop_duplicates(subset=["path"]).reset_index(drop=True)

            # Ensure parent directory exists
            parent = self.manifest_path.rsplit("/", 1)[0]
            try:
                self.fs.makedirs(parent, exist_ok=True)
            except TypeError:
                try:
                    self.fs.makedirs(parent)
                except FileExistsError:
                    pass

            # Perform an atomic write using a temporary file
            temp_path = f"{self.manifest_path}.tmp-{uuid.uuid4().hex}"
            try:
                out_df.to_parquet(temp_path, filesystem=self.fs, index=False)
                # some fs lack atomic rename; copy then remove
                if hasattr(self.fs, "rename"):
                    try:
                        self.fs.rename(temp_path, self.manifest_path)
                    except Exception:
                        self.fs.copy(temp_path, self.manifest_path)
                        self.fs.rm_file(temp_path)
                else:
                    self.fs.copy(temp_path, self.manifest_path)
                    self.fs.rm_file(temp_path)
                self.logger.info(f"Wrote manifest to {self.manifest_path}")
            except Exception as e:
                self.logger.error(f"Failed to write or move manifest: {e}")
                # not re-raising to avoid breaking the ETL run
            finally:
                # Always try to clean temp leftovers
                try:
                    if self._safe_exists(temp_path):
                        if hasattr(self.fs, "rm_file"):
                            self.fs.rm_file(temp_path)
                        else:
                            self.fs.rm(temp_path, recursive=False)
                except Exception:
                    pass

            # Reset internal state
            self._new_records.clear()
            try:
                self._loaded_paths = set(out_df["path"].tolist())
            except Exception:
                self._loaded_paths = None
            self.clear_existing = False

    def _cleanup_orphaned_files(self) -> None:
        """Best-effort removal of leftover temporary manifest files."""
        try:
            temp_file_pattern = f"{self.manifest_path}.tmp-*"
            orphaned_files = self.fs.glob(temp_file_pattern)
            if not orphaned_files:
                return

            for f_path in orphaned_files:
                try:
                    if hasattr(self.fs, "rm_file"):
                        self.fs.rm_file(f_path)
                    else:
                        self.fs.rm(f_path, recursive=False)
                    self.logger.info(f"Deleted orphaned file: {f_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to delete orphaned temp file '{f_path}': {e}")
        except Exception as e:
            # Non-critical
            self.logger.debug(f"Temp cleanup skipped: {e}")