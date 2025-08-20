import warnings
from typing import Any, Dict, Type, TypeVar, Union

import dask.dataframe as dd
import fsspec
import pandas as pd
from pydantic import BaseModel

from sibi_dst.v2.utils import Logger
from sibi_dst.v2.df_helper.core import QueryConfig, ParamsConfig, FilterHandler
from sibi_dst.v2.df_helper.backends.sqlalchemy import SqlAlchemyConnectionConfig, SqlAlchemyLoadFromDb
from sibi_dst.v2.df_helper.backends.sqlmodel import SQLModelConnectionConfig, SQLModelLoadFromDb

# Define a generic type variable for BaseModel subclasses
T = TypeVar("T", bound=BaseModel)

# Suppress warnings about protected member access
warnings.filterwarnings(
    "ignore",
    message="Access to a protected member _meta",
    category=UserWarning,
)


class DfHelper:
    df: Union[dd.DataFrame, pd.DataFrame] = None
    default_config = {
        'parquet_storage_path': None,
        'dt_field': None,
        'as_pandas': False,
        'filesystem': 'file',
        'filesystem_options': {},
        'fs': fsspec.filesystem('file')
    }

    def __init__(self, **kwargs: Any) -> None:
        # Merge default configuration with any provided kwargs
        config = {**self.default_config.copy(), **kwargs}
        self.backend = config.setdefault('backend', 'sqlalchemy')
        self.debug = config.setdefault('debug', False)
        self.as_pandas = config.setdefault('as_pandas', False)
        self.logger = config.setdefault(
            'logger',
            Logger.default_logger(logger_name=self.__class__.__name__, debug=self.debug)
        )
        self.logger.debug("Logger initialized in DEBUG mode.")

        # Propagate logger and debug settings to all components
        config.setdefault('logger', self.logger)
        config.setdefault('debug', self.debug)

        self._initialize_backend_config(**config)

    def __str__(self) -> str:
        return self.__class__.__name__

    def _extract_config_vars(self, model: Type[T], kwargs: Dict[str, Any]) -> T:
        """
        Extracts and initializes a Pydantic model using only the keys that the model accepts.
        The recognized keys are removed from kwargs.
        """
        recognized_keys = set(model.__annotations__.keys())
        self.logger.debug(f"Recognized keys for {model.__name__}: {recognized_keys}")
        model_kwargs = {k: kwargs.pop(k) for k in list(kwargs.keys()) if k in recognized_keys}
        self.logger.debug(f"Initializing {model.__name__} with: {model_kwargs}")
        return model(**model_kwargs)

    def _initialize_backend_config(self, **kwargs: Any) -> None:
        """
        Initializes the backend configurations by extracting the settings required for queries,
        parameters, and SQLAlchemy connections.
        """
        self.logger.debug("Initializing backend configuration.")
        self._backend_query = self._extract_config_vars(QueryConfig, kwargs)
        self._backend_params = self._extract_config_vars(ParamsConfig, kwargs)
        if self.backend == "sqlalchemy":
            self.backend_connection_config = self._extract_config_vars(SqlAlchemyConnectionConfig, kwargs)
        elif self.backend == "sqlmodel":
            self.backend_connection_config = self._extract_config_vars(SQLModelConnectionConfig, kwargs)
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")

    def load(self, **options: Any) -> Union[dd.DataFrame, pd.DataFrame]:
        """
        Loads the data using the underlying SQLAlchemy loader. Returns a pandas DataFrame
        if 'as_pandas' is True; otherwise returns a dask DataFrame.
        """
        df = self._load(**options)
        return df.compute() if self.as_pandas else df

    def _load(self, **options: Any) -> Union[dd.DataFrame, pd.DataFrame]:
        self._backend_params.parse_params(options)
        if self.backend == "sqlalchemy":
            return self._load_from_sqlalchemy(**options)
        elif self.backend == "sqlmodel":
            return self._load_from_sqlmodel(**options)
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")

    def _load_from_sqlalchemy(self, **options: Any) -> Union[dd.DataFrame, pd.DataFrame]:
        """
        Loads data from a SQLAlchemy source. On failure, logs the error and returns an empty
        DataFrame wrapped as a dask DataFrame.
        """
        try:
            db_loader = SqlAlchemyLoadFromDb(
                self.backend_connection_config,
                self._backend_query,
                self._backend_params,
                self.debug,
                self.logger,
                **options
            )
            self.df = db_loader.build_and_load()
            self._process_loaded_data()
            self._post_process_df()
            self.logger.debug("Data successfully loaded from SQLAlchemy database.")
        except Exception as e:
            self.logger.error(f"Failed to load data from SQLAlchemy database: {e}. Options: {options}")
            # Optionally re-raise the exception if in debug mode
            if self.debug:
                raise
            self.df = dd.from_pandas(pd.DataFrame(), npartitions=1)
        return self.df

    def _load_from_sqlmodel(self, **options: Any) -> Union[dd.DataFrame, pd.DataFrame]:
        try:
            db_loader = SQLModelLoadFromDb(
                self.backend_connection_config,
                self._backend_query,
                self._backend_params,
                self.debug,
                self.logger,
                **options
            )
            self.df = db_loader.build_and_load()
            self._process_loaded_data()
            self._post_process_df()
            self.logger.debug("Data successfully loaded from SQLModel database.")
        except Exception as e:
            self.logger.error(f"Failed to load data from SQLModel database: {e}. Options: {options}")
            if self.debug:
                raise
            self.df = dd.from_pandas(pd.DataFrame(), npartitions=1)
        return self.df

    def _post_process_df(self) -> None:
        """
        Post-processes the DataFrame by filtering columns, renaming them, setting the index,
        and converting the index to datetime if requested.
        """
        df_params = self._backend_params.df_params
        fieldnames = df_params.get("fieldnames")
        index_col = df_params.get("index_col")
        datetime_index = df_params.get("datetime_index", False)
        column_names = df_params.get("column_names")

        # Filter columns based on fieldnames
        if fieldnames:
            valid_fieldnames = [col for col in fieldnames if col in self.df.columns]
            self.df = self.df[valid_fieldnames]

        # Rename columns if column_names are provided
        if column_names is not None:
            if not fieldnames or len(fieldnames) != len(column_names):
                raise ValueError(
                    f"Length mismatch: fieldnames ({len(fieldnames) if fieldnames else 0}) and "
                    f"column_names ({len(column_names)}) must match."
                )
            rename_mapping = dict(zip(fieldnames, column_names))
            self.df = self.df.map_partitions(self._rename_columns, mapping=rename_mapping)

        # Set the index column if specified
        if index_col is not None:
            if index_col in self.df.columns:
                self.df = self.df.set_index(index_col)
            else:
                raise ValueError(f"Index column '{index_col}' not found in DataFrame.")

        # Convert the index to datetime if required
        if datetime_index and self.df.index.dtype != 'datetime64[ns]':
            self.df = self.df.map_partitions(self._convert_index_to_datetime)

        self.logger.debug("Post-processing of DataFrame completed.")

    def _process_loaded_data(self) -> None:
        """
        Applies renaming logic based on the field map configuration.
        Logs a warning for any missing columns, and only renames existing columns.
        """
        self.logger.debug(f"Processing loaded data; DataFrame type: {type(self.df)}")
        if self.df.map_partitions(len).compute().sum() > 0:
            field_map = self._backend_params.field_map or {}
            if isinstance(field_map, dict):
                rename_mapping = {k: v for k, v in field_map.items() if k in self.df.columns}
                missing_columns = [k for k in field_map if k not in self.df.columns]
                if missing_columns:
                    self.logger.warning(
                        f"The following columns in field_map are not in the DataFrame: {missing_columns}"
                    )
                if rename_mapping:
                    self.df = self.df.map_partitions(self._rename_columns, mapping=rename_mapping)
        self.logger.debug("Processing of loaded data completed.")

    @staticmethod
    def _rename_columns(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
        """Helper function to rename columns in a DataFrame."""
        return df.rename(columns=mapping)

    @staticmethod
    def _convert_index_to_datetime(df: pd.DataFrame) -> pd.DataFrame:
        """Helper function to convert the DataFrame index to datetime."""
        df.index = pd.to_datetime(df.index, errors='coerce')
        return df