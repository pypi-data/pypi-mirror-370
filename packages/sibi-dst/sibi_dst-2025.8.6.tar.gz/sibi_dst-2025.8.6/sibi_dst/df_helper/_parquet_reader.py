from typing import Optional, ClassVar, Dict, Any, Union

import dask.dataframe as dd
import fsspec
import pandas as pd

from sibi_dst.df_helper import DfHelper

class ParquetReader(DfHelper):
    """
    This class is a specialized helper for reading and managing Parquet files.

    The `ParquetReader` class is designed to facilitate working with Parquet
    datasets stored across different filesystems. It initializes the required
    resources, ensures the existence of the specified Parquet directory,
    and provides an abstraction to load the data into a Dask DataFrame.

    The class requires configuration for the storage path and dates defining
    a range of interest. It also supports various filesystem types through
    `fsspec`.

    :ivar config: Holds the final configuration for this instance, combining
        `DEFAULT_CONFIG` with user-provided configuration.
    :type config: dict
    :ivar df: Stores the loaded Dask DataFrame after the `load()` method is
        invoked. Initially set to None.
    :type df: Optional[dd.DataFrame | pd.DataFrame]
    :ivar parquet_storage_path: The path to the Parquet storage directory.
    :type parquet_storage_path: str
    :ivar parquet_start_date: Start date for Parquet data selection. Must
        be set in the configuration.
    :type parquet_start_date: str
    :ivar parquet_end_date: End date for Parquet data selection. Must be
        set in the configuration.
    :type parquet_end_date: str

    :ivar fs: Instance of `fsspec` filesystem used to interact with the
        Parquet storage.
    :type fs: fsspec.AbstractFileSystem
    """
    DEFAULT_CONFIG: ClassVar[Dict[str, Any]] = {
        'backend': 'parquet'
    }
    df: Optional[Union[dd.DataFrame, pd.DataFrame]] = None

    def __init__(self,  **kwargs):
        self.config = {
            **self.DEFAULT_CONFIG,
            **kwargs,
        }
        super().__init__(**self.config)

        self.parquet_storage_path = self.config.setdefault('parquet_storage_path', None)
        if self.parquet_storage_path is None:
            raise ValueError('parquet_storage_path must be set')
        self.parquet_start_date = self.config.setdefault('parquet_start_date', None)
        if self.parquet_start_date is None:
            raise ValueError('parquet_start_date must be set')

        self.parquet_end_date = self.config.setdefault('parquet_end_date', None)
        if self.parquet_end_date is None:
            raise ValueError('parquet_end_date must be set')
        if self.fs is None:
            raise ValueError('Parquet Reader mush be supplied a fs instance')

        if not self.directory_exists():
            raise ValueError(f"{self.parquet_storage_path} does not exist")

    def load(self, **kwargs) -> Union[pd.DataFrame, dd.DataFrame]:
        self.df = super().load(**kwargs)
        return self.df

    def directory_exists(self):
        try:
            info = self.fs.info(self.parquet_storage_path)
            return info['type'] == 'directory'
        except FileNotFoundError:
            return False