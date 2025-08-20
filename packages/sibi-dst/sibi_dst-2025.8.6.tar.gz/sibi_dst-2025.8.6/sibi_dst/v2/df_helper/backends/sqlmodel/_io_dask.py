import itertools
import dask.dataframe as dd
import pandas as pd

#from sqlmodel import create_engine, Session, select
from sibi_dst.v2.df_helper.core import FilterHandler
from sibi_dst.v2.utils import Logger


class SQLModelDask:
    def __init__(self, model, filters, engine_url, chunk_size=1000, logger=None, debug=False):
        """
        Initialize with a SQLModel query and a database connection URL.

        :param model: SQLModel ORM model.
        :param filters: Filters to apply on the query.
        :param engine_url: Database connection string.
        :param chunk_size: Number of records per chunk for Dask partitions.
        :param logger: Logger instance for logging.
        :param debug: Whether to enable detailed logging.
        """
        self.query = None
        self.model = model
        self.filters = filters
        self.chunk_size = chunk_size
        self.debug = debug
        # Create the engine using SQLModel's create_engine
        self.engine = create_engine(engine_url)
        self.logger = logger or Logger.default_logger(logger_name=self.__class__.__name__, debug=debug)
        self.logger.set_level(self.logger.DEBUG if debug else self.logger.INFO)

    @staticmethod
    def infer_dtypes_from_model(model):
        """
        Infer Dask DataFrame dtypes based on the SQLModel columns.
        """
        # Mapping SQLAlchemy type names to Dask/Pandas dtypes.
        sqlalchemy_to_dask_dtype = {
            'INTEGER': 'Int64',
            'SMALLINT': 'Int64',
            'BIGINT': 'Int64',
            'FLOAT': 'float64',
            'NUMERIC': 'float64',
            'BOOLEAN': 'bool',
            'VARCHAR': 'object',
            'TEXT': 'object',
            'DATE': 'datetime64[ns]',
            'DATETIME': 'datetime64[ns]',
            'TIME': 'object',
            'UUID': 'object',
        }
        dtypes = {}
        for column in model.__table__.columns:
            # Get the column type name in uppercase.
            type_str = str(column.type).upper()
            dtype = sqlalchemy_to_dask_dtype.get(type_str, 'object')
            dtypes[column.name] = dtype
        return dtypes

    def read_frame(self, fillna_value=None):
        """
        Load data from a SQLModel query into a Dask DataFrame.

        :param fillna_value: Value to replace NaN/NULL values with, if any.
        :return: A Dask DataFrame containing the query results.
        """
        try:
            with Session(self.engine) as session:
                # Build the base query.
                self.query = select(self.model.__table__)
                if self.filters:
                    # Apply filters using FilterHandler (assumed to work for SQLModel as well)
                    self.query = FilterHandler(backend="sqlmodel", logger=self.logger, debug=self.debug).apply_filters(
                        self.query, model=self.model, filters=self.filters
                    )
                else:
                    # If no filters provided, limit to a small number of records for safety.
                    n_records = 100
                    self.query = self.query.limit(n_records)
                self.logger.debug(f"query: {self.query}")

                # Infer dtypes from the model.
                dtypes = self.infer_dtypes_from_model(self.model)
                # Get the column order from the model's table.
                ordered_columns = [column.name for column in self.model.__table__.columns]

                # Execute the query and fetch all results.
                results = session.exec(self.query).all()
                iterator = iter(results)
                partitions = []

                while True:
                    chunk = list(itertools.islice(iterator, self.chunk_size))
                    if not chunk:
                        break
                    # Convert each SQLModel instance to a dictionary using the built-in .dict() method.
                    df = pd.DataFrame([row.dict() for row in chunk])
                    # Drop SQLModel/SQLAlchemy internal state if present.
                    df = df.loc[:, ~df.columns.str.contains('_sa_instance_state')]
                    # Reorder columns to match the model's column order.
                    df = df[ordered_columns]
                    if fillna_value is not None:
                        df = df.fillna(fillna_value)
                    # Remove timezone information from datetime columns.
                    for col in df.columns:
                        if isinstance(df[col].dtype, pd.DatetimeTZDtype):
                            df[col] = df[col].dt.tz_localize(None)
                    df = df.astype(dtypes)
                    partitions.append(dd.from_pandas(df, npartitions=1))

                if partitions:
                    dask_df = dd.concat(partitions, axis=0, ignore_index=True)
                else:
                    dask_df = dd.from_pandas(pd.DataFrame(columns=ordered_columns), npartitions=1)

                self.logger.debug(f"Loaded {len(dask_df)} rows into Dask DataFrame.")
                return dask_df

        except Exception as e:
            self.logger.error(f"_io_dask:Error executing query: {str(e)}")
            self.logger.error(f"_io_dask:{self.query})
            # In case of error, return an empty Dask DataFrame with the expected columns.
            return dd.from_pandas(pd.DataFrame(columns=ordered_columns), npartitions=1)