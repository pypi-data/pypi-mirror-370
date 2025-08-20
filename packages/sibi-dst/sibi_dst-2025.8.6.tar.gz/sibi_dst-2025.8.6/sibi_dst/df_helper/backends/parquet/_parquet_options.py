import datetime
from pathlib import Path
from typing import Optional, List

import dask.dataframe as dd
import fsspec
import pandas as pd
from pydantic import BaseModel, model_validator, ConfigDict

from sibi_dst.df_helper.core import FilterHandler
from sibi_dst.utils import FilePathGenerator
from sibi_dst.utils import Logger


class ParquetConfig(BaseModel):
    """
    Represents configuration for managing and validating parquet file operations.

    The `ParquetConfig` class provides attributes and methods necessary to handle operations
    on parquet files in a file system. It includes functionalities for ensuring file paths
    and extensions, validating storage paths and parameters, determining file recency,
    and calculating the size of parquet files. This class is designed with flexibility to handle
    different file systems through the integration with `fsspec` and allows storage path validations
    with optional logging support.

    :ivar load_parquet: Indicates whether parquet data should be loaded based on the
        current configuration and validation.
    :type load_parquet: bool
    :ivar parquet_filename: The name of the parquet file, optional if folders are used.
    :type parquet_filename: Optional[str]
    :ivar parquet_storage_path: The base path for storing or retrieving parquet files.
    :type parquet_storage_path: Optional[str]
    :ivar parquet_full_path: The full path to a specific parquet file, derived from the
        storage path and filename when applicable.
    :type parquet_full_path: Optional[str]
    :ivar parquet_folder_list: A list of folder paths to parquet data, derived from start
        and end dates if specified.
    :type parquet_folder_list: Optional[List[str]]
    :ivar parquet_size_bytes: The total size of the parquet files, in bytes.
    :type parquet_size_bytes: int
    :ivar parquet_max_age_minutes: Maximum acceptable age of the most recent parquet file, in minutes.
    :type parquet_max_age_minutes: int
    :ivar parquet_is_recent: Indicates whether the parquet file is considered recent based
        on the `parquet_max_age_minutes` condition.
    :type parquet_is_recent: bool
    :ivar parquet_start_date: The start date for parquet file validation or file path generation.
    :type parquet_start_date: Optional[str]
    :ivar parquet_end_date: The end date for parquet file validation or file path generation.
    :type parquet_end_date: Optional[str]
    :ivar fs: The file system object used for storage operations, compliant with `fsspec`.
    :type fs: Optional[fsspec.spec.AbstractFileSystem]
    :ivar logger: A logger for handling logging operations.
    :type logger: Optional[Logger]
    """
    load_parquet: bool = False
    parquet_filename: Optional[str] = None
    parquet_storage_path: Optional[str] = None
    parquet_full_path: Optional[str] = None
    parquet_folder_list: Optional[List[str]] = None
    parquet_size_bytes: int = 0
    parquet_max_age_minutes: int = 0
    parquet_is_recent: bool = False
    parquet_start_date: Optional[str] = None
    parquet_end_date: Optional[str] = None
    fs: Optional[fsspec.spec.AbstractFileSystem] = None  # Your fsspec filesystem object
    logger: Optional[Logger] = None
    debug: bool = False
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode='after')
    def check_parquet_params(self):
        """
        Validates and configures the parameters required for managing parquet files. This includes
        configuring paths through `fsspec`, identifying file storage paths, checking the validity of
        dates related to parquet files, ensuring proper parquet file extensions, and determining
        whether existing parquet files are recent and loadable.

        :return: The current instance with validated and migrated attributes configured for
                 handling parquet files.

        :raises ValueError: If certain conditions are not met, such as missing or invalid
                           `parquet_storage_path`, providing only one of
                           `parquet_start_date` or `parquet_end_date`, or if the
                           `parquet_end_date` is earlier than the `parquet_start_date`.
        """
        # Configure paths based on fsspec
        if self.logger is None:
            self.logger = Logger.default_logger(logger_name=self.__class__.__name__)
        self.logger.set_level(Logger.DEBUG if self.debug else Logger.INFO)
        if self.fs is None:
            raise ValueError('Parquet Options: File system (fs) must be specified')

        if self.parquet_storage_path is None:
            raise ValueError('Parquet storage path must be specified')
        self.parquet_storage_path = self.parquet_storage_path.rstrip('/')
        if not self.fs.exists(self.parquet_storage_path):
            self.fs.mkdirs(self.parquet_storage_path, exist_ok=True)
            # raise ValueError('Parquet storage path does not exist')
        self.load_parquet = False
        if self.parquet_filename is not None:
            self.parquet_full_path = self.ensure_file_extension(
                filepath=self.fs.sep.join([str(self.parquet_storage_path), str(self.parquet_filename)]),
                extension='parquet'
            )
            self.parquet_is_recent = self.is_file_recent()
            self.load_parquet = self.parquet_is_recent and self.fs.exists(self.parquet_full_path)

        if self.parquet_start_date is not None:
            if self.parquet_end_date is None:
                raise ValueError('Parquet end date must be specified if start date is provided')

            start_date = datetime.datetime.strptime(self.parquet_start_date, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(self.parquet_end_date, '%Y-%m-%d')
            if end_date < start_date:
                raise ValueError('Parquet end date must be greater than start date')

            # Saving to parquet is disabled when start and end dates are provided, as we will load parquet files
            self.parquet_folder_list = FilePathGenerator(str(self.parquet_storage_path), fs=self.fs,
                                                         logger=self.logger).generate_file_paths(start_date, end_date)

            self.parquet_size_bytes = self.get_parquet_size_bytes()
            self.load_parquet = True
            # self.load_parquet = all([self.fs.exists(folder) for folder in self.parquet_folder_list]) and self.parquet_size_bytes > 0
        elif self.parquet_end_date is not None:
            raise ValueError('Parquet start date must be specified if end date is provided')

        return self

    def is_file_recent(self):
        """
        Determines whether the file at the specified parquet path is considered recent
        based on its modification time and the maximum age limit defined.

        The function first checks for the existence of the file at the specified
        `parquet_full_path`. If the file does not exist, the function will return
        False. If `parquet_max_age_minutes` is set to 0, it implies no maximum age
        limit, and the function will return True. Otherwise, it retrieves the file's
        last modified time and calculates the age of the file by comparing it with the
        current time. The function returns True if the file's age does not exceed the
        maximum age specified by `parquet_max_age_minutes`, otherwise it returns
        False.

        :return: Whether the file is considered recent based on its existence,
                 modification time, and maximum age limit.
        :rtype: bool
        """
        if not self.fs.exists(self.parquet_full_path):
            return False
        if self.parquet_max_age_minutes == 0:
            return True
        file_time = datetime.datetime.fromtimestamp(self.fs.modified(self.parquet_full_path))
        return (datetime.datetime.now() - file_time) <= datetime.timedelta(minutes=self.parquet_max_age_minutes)

    def get_parquet_size_bytes(self):
        """
        Calculate the total size, in bytes, of all Parquet files within the defined
        folders specified by `parquet_folder_list`. The function iteratively goes
        through each folder in the provided list, applying a recursive wildcard
        search to include all levels of nested directories, and calculates the
        cumulative size of all found Parquet files using the file system's size
        retrieval method.

        :raises AttributeError: If `fs` or `parquet_folder_list` attributes are not set
            or improperly configured when the method is called.
        :raises NotImplementedError: If the `fs.size` or `fs.glob` methods are
            unimplemented in the provided file system object or it otherwise lacks
            necessary support for these operations.

        :return: The cumulative size of all Parquet files located in the folders
            defined by `parquet_folder_list`, measured in bytes.
        :rtype: int
        """
        total_size = 0
        for folder in self.parquet_folder_list:
            # Use a double wildcard ** to match any level of nested directories
            for path in self.fs.glob(f"{folder}/**/*.parquet"):
                total_size += self.fs.size(path)
        return total_size

    def load_files(self, **filters):
        """
        Loads parquet files into a Dask DataFrame based on the specified conditions.
        Supports Parquet predicate pushdown (pyarrow) + residual Dask mask.
        """
        if not self.load_parquet:
            self.logger.warning("Parquet loading is disabled. Returning empty DataFrame.")
            return dd.from_pandas(pd.DataFrame(), npartitions=1)

        # Resolve paths
        paths_to_load = []
        if self.parquet_folder_list:
            paths_to_load = [p for p in self.parquet_folder_list if p]
        elif self.parquet_full_path:
            paths_to_load = [self.parquet_full_path]

        if not paths_to_load:
            self.logger.warning("No valid parquet file paths were provided. Returning empty DataFrame.")
            return dd.from_pandas(pd.DataFrame(), npartitions=1)

        # Prepare filters
        fh = None
        expr = None
        pq_filters = None
        residual_filters = None
        if filters:
            fh = FilterHandler(backend="dask", debug=self.debug, logger=self.logger)

            # Use the compiler + pushdown split so we don't double-apply
            try:
                # If you added split_pushdown_and_residual earlier:
                pq_filters, residual_filters = fh.split_pushdown_and_residual(filters)
                expr = fh.compile_filters(residual_filters) if residual_filters else None
            except AttributeError:
                # Fallback if you didn't add split_*: push everything down and also mask (redundant but correct)
                expr = fh.compile_filters(filters)
                pq_filters = expr.to_parquet_filters()

        try:
            self.logger.debug(f"Attempting to load Parquet data from: {paths_to_load}")

            # Optional: prune columns. Keep it simple unless you want to compute from filters.
            columns = None  # or a concrete list if you know it

            if fh and pq_filters:
                self.logger.debug(f"Applying Parquet filters: {pq_filters}")
                dd_result = dd.read_parquet(
                    paths_to_load,
                    engine="pyarrow",
                    filesystem=self.fs,  # your fsspec filesystem (e.g., s3fs)
                    filters=pq_filters,
                    columns=columns,
                    gather_statistics=False,   # uncomment if you have *many* files and don't need global stats
                )
                # Apply only residual mask (if any)
                if expr is not None:
                    dd_result = dd_result[expr.mask(dd_result)]
            else:
                dd_result = dd.read_parquet(
                    paths_to_load,
                    engine="pyarrow",
                    filesystem=self.fs,
                    columns=columns,
                    gather_statistics=False,
                )
                # If we didn't push down, but have filters, apply them here
                if expr is None and fh and filters:
                    expr = fh.compile_filters(filters)
                if expr is not None:
                    dd_result = dd_result[expr.mask(dd_result)]

            return dd_result

        except FileNotFoundError as e:
            self.logger.debug(f"Parquet files not found at paths {paths_to_load}: {e}")
            self.logger.debug("Returning empty DataFrame due to missing parquet files.")
            return dd.from_pandas(pd.DataFrame(), npartitions=1)
        except Exception as e:
            self.logger.debug(f"Parquet loading failed for paths {paths_to_load}: {e}")
            self.logger.debug("Returning empty DataFrame due to loading error.")
            return dd.from_pandas(pd.DataFrame(), npartitions=1)


    @staticmethod
    def ensure_file_extension(filepath: str, extension: str) -> str:
        """
        Ensures that the specified file has the desired extension. If the file already has the
        specified extension, it returns the filepath unchanged. Otherwise, it updates the file
        extension to the given one and returns the modified filepath.

        :param filepath: The path to the file as a string.
        :param extension: The desired file extension, without the leading dot.
        :return: The updated file path as a string, ensuring it has the specified extension.
        """
        path = Path(filepath)
        return str(path.with_suffix(f".{extension}")) if path.suffix != f".{extension}" else filepath
