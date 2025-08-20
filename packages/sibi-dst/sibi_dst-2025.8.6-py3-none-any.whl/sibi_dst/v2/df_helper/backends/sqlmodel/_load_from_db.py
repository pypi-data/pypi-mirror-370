import dask.dataframe as dd
import pandas as pd

from sibi_dst.v2.df_helper.core import ParamsConfig, QueryConfig
from sibi_dst.v2.utils import Logger
from ._io_dask import SQLModelDask
from ._db_connection import SQLModelConnectionConfig


class SQLModelLoadFromDb:
    """
    The SqlAlchemyLoadFromDb class provides functionality to load data from a
    database using SQLAlchemy into a Dask DataFrame. It is capable of handling
    large datasets efficiently by utilizing the Dask framework for parallel
    computations.

    This class is initialized with a database connection configuration, query
    configuration, optional parameters, and a logger. It can execute a query
    using the specified configurations and read the results into a Dask
    DataFrame. This is useful for processing and analyzing large-scale data.

    :ivar df: Dask DataFrame to store the loaded data.
    :type df: dd.DataFrame
    :ivar db_connection: Database connection configuration object, containing details
        such as the table, model, and engine to be used for the query.
    :type db_connection: SqlAlchemyConnectionConfig
    :ivar table_name: Name of the database table being queried.
    :type table_name: str
    :ivar model: SQLAlchemy model associated with the database connection.
    :type model: sqlalchemy.ext.declarative.api.DeclarativeMeta
    :ivar engine: SQLAlchemy engine used for executing queries.
    :type engine: sqlalchemy.engine.base.Engine
    :ivar logger: Logger instance for logging debug and error information.
    :type logger: Logger
    :ivar query_config: Query configuration, including query-related details such
        as the SQL query or query settings.
    :type query_config: QueryConfig
    :ivar params_config: Parameters configuration, including filter parameters for
        the query.
    :type params_config: ParamsConfig
    :ivar debug: Debug flag indicating whether debug mode is enabled.
    :type debug: bool
    :ivar chunk_size: Size of data chunks to process at a time.
    :type chunk_size: int
    """
    df: dd.DataFrame = None

    def __init__(
            self,
            plugin_sqlalchemy: SQLModelConnectionConfig,  # Expected to be an instance of SqlAlchemyConnection
            plugin_query: QueryConfig = None,
            plugin_params: ParamsConfig = None,
            debug: bool = False,
            logger: Logger = None,
            **kwargs,
    ):
        """
        Initializes an instance of the class, setting up a database connection,
        query configuration, parameter configuration, and other optional settings
        like debugging and logging. The class aims to manage the integration and
        interaction with SQLAlchemy-based database operations.

        :param plugin_sqlalchemy:
            The SQLAlchemy connection configuration object, which provides
            the connection details like engine, table name, and model
            associated with the database operations.
        :param plugin_query:
            The query configuration object, used to define specific query
            options or rules. Defaults to None.
        :param plugin_params:
            The parameters configuration object, used for any additional
            parameterized settings or configurations. Defaults to None.
        :param logger:
            Optional logger instance for logging purposes. If not provided,
            a default logger is instantiated using the standard logging system.
        :param kwargs:
            Optional additional keyword arguments for customization. Can
            include optional settings like `debug` mode or `chunk_size`
            for batch operations.
        """
        self.db_connection = plugin_sqlalchemy
        self.table_name = self.db_connection.table
        self.model = self.db_connection.model
        self.engine = self.db_connection.engine
        self.debug = debug
        self.logger = logger or Logger.default_logger(logger_name=self.__class__.__name__, debug=self.debug)
        self.query_config = plugin_query
        self.params_config = plugin_params
        self.chunk_size = kwargs.pop("chunk_size", 1000)

    def build_and_load(self) -> dd.DataFrame:
        """
        Builds and returns the resulting dataframe after calling the internal
        build and load function. This method triggers the `_build_and_load`
        function to process and prepare the data before returning it as
        a dask dataframe.

        :raises RuntimeError: If any error occurs during the build or load process.

        :return: The processed data in a dask dataframe.
        :rtype: dd.DataFrame
        """
        self._build_and_load()
        return self.df

    def _build_and_load(self) -> dd.DataFrame:
        """
        Builds and loads a Dask DataFrame from a SQLAlchemy-compatible source.

        This method initializes a SQLAlchemyDask object with the provided model,
        filters, engine URL, logger, chunk size, and debug configuration.
        It attempts to load the data using the ``read_frame`` method of
        SQLAlchemyDask. If the data cannot be loaded or the query returns
        no rows, it creates and returns an empty Dask DataFrame.

        :raises Exception: On failure to load data or to create a DataFrame.

        :return: A Dask DataFrame object containing the queried data or an
                 empty DataFrame if the query returns no results or fails.
        :rtype: dask.dataframe.DataFrame
        """
        try:
            self.df = SQLModelDask(
                model=self.model,
                filters=self.params_config.filters,
                engine_url=self.engine.url,
                logger=self.logger,
                chunk_size=self.chunk_size,
                debug=self.debug
            ).read_frame()

            if self.df is None or len(self.df.head().index) == 0:
                self.logger.debug("Query returned no results.")
                dask_df = dd.from_pandas(pd.DataFrame(), npartitions=1)

                return dask_df
            return self.df
        except Exception as e:
            self.logger.debug(f"Failed to load data into Dask DataFrame.{e}")
            dask_df = dd.from_pandas(pd.DataFrame(), npartitions=1)

            return dask_df
