from __future__ import annotations

from typing import Any, Tuple

import dask.dataframe as dd
import pandas as pd

from sibi_dst.utils import ManagedResource
from sibi_dst.df_helper.core import ParamsConfig, QueryConfig
from ._db_connection import SqlAlchemyConnectionConfig
from ._io_dask import SQLAlchemyDask


class SqlAlchemyLoadFromDb(ManagedResource):
    """
    Orchestrates loading data from a database using SQLAlchemy into a Dask DataFrame.
    """

    def __init__(
        self,
        plugin_sqlalchemy: SqlAlchemyConnectionConfig,
        plugin_query: QueryConfig = None,
        plugin_params: ParamsConfig = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.db_connection = plugin_sqlalchemy
        self.model = self.db_connection.model
        self.engine = self.db_connection.engine
        self.query_config = plugin_query
        self.params_config = plugin_params
        self.chunk_size = kwargs.get("chunk_size", self.params_config.df_params.get("chunk_size", 1000) if self.params_config else 1000)
        self.total_records = -1

    def build_and_load(self) -> Tuple[int, dd.DataFrame]:
        try:
            with SQLAlchemyDask(
                model=self.model,
                filters=self.params_config.filters if self.params_config else {},
                engine=self.engine,
                chunk_size=self.chunk_size,
                logger=self.logger,
                verbose=self.verbose,
                debug=self.debug,
            ) as loader:
                self.logger.debug(f"SQLAlchemyDask loader initialized for model: {self.model.__name__}")
                self.total_records, dask_df = loader.read_frame()
                return self.total_records, dask_df
        except Exception as e:
            self.total_records = -1
            self.logger.error(f"{self.model.__name__} Failed to build and load data: {e}", exc_info=True)
            # empty df with correct columns
            columns = [c.name for c in self.model.__table__.columns]
            return self.total_records, dd.from_pandas(pd.DataFrame(columns=columns), npartitions=1)

# from __future__ import annotations
#
# from typing import Any
#
# import dask.dataframe as dd
# import pandas as pd
#
# from sibi_dst.utils import ManagedResource
# from sibi_dst.df_helper.core import ParamsConfig, QueryConfig
# from ._db_connection import SqlAlchemyConnectionConfig
# from ._io_dask import SQLAlchemyDask
#
# class SqlAlchemyLoadFromDb(ManagedResource):
#     """
#     Orchestrates loading data from a database using SQLAlchemy into a Dask
#     DataFrame by configuring and delegating to the SQLAlchemyDask loader.
#     """
#
#     def __init__(
#             self,
#             plugin_sqlalchemy: SqlAlchemyConnectionConfig,
#             plugin_query: QueryConfig = None,
#             plugin_params: ParamsConfig = None,
#             **kwargs,
#     ):
#         """
#         Initializes the loader with all necessary configurations.
#
#         Args:
#             plugin_sqlalchemy: The database connection configuration object.
#             plugin_query: The query configuration object.
#             plugin_params: The parameters and filters configuration object.
#             logger: An optional logger instance.
#             **kwargs: Must contain 'index_column' for Dask partitioning.
#         """
#         super().__init__(**kwargs)
#         self.db_connection = plugin_sqlalchemy
#         self.model = self.db_connection.model
#         self.engine = self.db_connection.engine
#         self.query_config = plugin_query
#         self.params_config = plugin_params
#         self.chunk_size = kwargs.get("chunk_size", self.params_config.df_params.get("chunk_size", 1000))
#         self.total_records = -1 # Initialize total_records to -1 to indicate no records loaded yet
#
#     def build_and_load(self) -> tuple[int | Any, Any] | dd.DataFrame:
#         """
#         Builds and loads a Dask DataFrame from a SQLAlchemy source.
#
#         This method is stateless and returns the DataFrame directly.
#
#         Returns:
#             A Dask DataFrame containing the queried data or an empty,
#             correctly structured DataFrame if the query fails or returns no results.
#         """
#         try:
#             # Instantiate and use the low-level Dask loader
#             with SQLAlchemyDask(model=self.model,filters=self.params_config.filters if self.params_config else {},
#                 engine=self.engine,
#                 chunk_size=self.chunk_size,
#                 logger=self.logger,
#                 verbose=self.verbose,
#                 debug=self.debug) as sqlalchemy_dask_loader:
#                 self.logger.debug(f"SQLAlchemyDask loader initialized for model: {self.model.__name__}")
#                 # Create the lazy DataFrame and read a record count
#                 # if total_records less than 0, it means an error occurred during the loading process
#                 self.total_records, dask_df = sqlalchemy_dask_loader.read_frame()
#                 return self.total_records, dask_df
#         except Exception as e:
#             self.total_records = -1
#             self.logger.error(f"{self.model.__name__} Failed to build and load data: {e}", exc_info=True)
#             # Return an empty dataframe with the correct schema on failure
#             columns = [c.name for c in self.model.__table__.columns]
#             return self.total_records, dd.from_pandas(pd.DataFrame(columns=columns), npartitions=1)
