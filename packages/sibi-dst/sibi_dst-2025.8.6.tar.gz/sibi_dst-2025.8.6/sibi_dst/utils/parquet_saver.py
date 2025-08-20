import warnings

import dask.dataframe as dd
import pyarrow as pa

from . import ManagedResource

warnings.filterwarnings("ignore", message="Passing 'overwrite=True' to to_parquet is deprecated")


class ParquetSaver(ManagedResource):
    """
    Saves Dask DataFrames to Parquet, with a workaround for S3-compatible
    storage providers that misbehave on batch delete operations.

    Assumes `df_result` is a Dask DataFrame.
    """

    def __init__(
        self,
        df_result: dd.DataFrame,
        parquet_storage_path: str,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.df_result = df_result
        self.parquet_storage_path = parquet_storage_path.rstrip("/")
        if not self.fs:
            raise ValueError("File system (fs) must be provided to ParquetSaver.")

        self.protocol = "file"
        if "://" in self.parquet_storage_path:
            self.protocol = self.parquet_storage_path.split(":", 1)[0]

    def save_to_parquet(self, output_directory_name: str = "default_output", overwrite: bool = True):
        """
        Saves the Dask DataFrame to a Parquet dataset.

        If overwrite is True, it manually clears the destination directory before
        writing to avoid issues with certain S3-compatible storage providers.
        """
        full_path = f"{self.parquet_storage_path}/{output_directory_name}"

        if overwrite and self.fs and self.fs.exists(full_path):
            self.logger.info(f"Overwrite is True, clearing destination path: {full_path}")
            self._clear_directory_safely(full_path)

        # Ensure the base directory exists after clearing
        self.fs.mkdirs(full_path, exist_ok=True)

        schema = self._define_schema()
        self.logger.info(f"Saving DataFrame to Parquet dataset at: {full_path}")

        # persist then write (lets the graph be shared if the caller reuses it)
        ddf = self.df_result.persist()

        try:
            ddf.to_parquet(
                path=full_path,
                engine="pyarrow",
                schema=schema,
                overwrite=False,         # we've handled deletion already
                filesystem=self.fs,
                write_index=False,
            )
            self.logger.info(f"Successfully saved Parquet dataset to: {full_path}")
        except Exception as e:
            self.logger.error(f"Failed to save Parquet dataset to {full_path}: {e}")
            raise

    def _clear_directory_safely(self, directory: str):
        """
        Clears the contents of a directory robustly.
        - For S3, deletes files one-by-one to bypass brittle multi-delete.
        - For other filesystems, uses the standard recursive remove.
        """
        if self.protocol == "s3":
            self.logger.warning(
                "Using single-file S3 deletion for compatibility. "
                "This may be slow for directories with many files."
            )
            # Glob all contents (files and subdirs) and delete them individually.
            all_paths = self.fs.glob(f"{directory}/**")
            # delete contents (deepest first)
            for path in sorted([p for p in all_paths if p != directory], key=len, reverse=True):
                self.logger.debug(f"Deleting: {path}")
                try:
                    # prefer rm_file if available (minio, s3fs expose it)
                    if hasattr(self.fs, "rm_file"):
                        self.fs.rm_file(path)
                    else:
                        self.fs.rm(path, recursive=False)
                except Exception as e:
                    self.logger.warning(f"Failed to delete '{path}': {e}")
            # remove the (now empty) directory if present
            try:
                self.fs.rm(directory, recursive=False)
            except Exception:
                pass
        else:
            # Standard, fast deletion for other filesystems (local, etc.)
            self.fs.rm(directory, recursive=True)

    def _define_schema(self) -> pa.Schema:
        """
        Defines a PyArrow schema dynamically based on DataFrame's column types.
        Works for Dask by using known dtypes on the collection.
        """
        pandas_dtype_to_pa = {
            "object": pa.string(), "string": pa.string(),
            "int64": pa.int64(), "Int64": pa.int64(),
            "int32": pa.int32(), "Int32": pa.int32(),
            "float64": pa.float64(), "float32": pa.float32(),
            "bool": pa.bool_(), "boolean": pa.bool_(),
            "datetime64[ns]": pa.timestamp("ns"),
            "datetime64[ns, UTC]": pa.timestamp("ns", tz="UTC"),
            "category": pa.string(),
        }
        fields = [
            pa.field(c, pandas_dtype_to_pa.get(str(d), pa.string()))
            for c, d in self.df_result.dtypes.items()
        ]
        return pa.schema(fields)