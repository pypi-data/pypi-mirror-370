import re
from collections import defaultdict
from typing import Dict, Any, Type

from sqlalchemy import MetaData, Table, and_
from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import ArgumentError, NoForeignKeysError
from sqlalchemy.orm import declarative_base, relationship, foreign, configure_mappers, clear_mappers

from sibi_dst.v2.utils import Logger

# Base class for dynamically created models.
Base = declarative_base()

# Constants.
APPS_LABEL = "datacubes"
RESERVED_COLUMN_NAMES = {"metadata", "class_", "table"}
RESERVED_KEYWORDS = {"class", "def", "return", "yield", "global"}

# Global registry keyed by the original table name (snake_case).
MODEL_REGISTRY: Dict[str, Type] = {}


class SqlAlchemyModelBuilder:
    """
    Dynamically builds an ORM model for a single table by reflecting its columns
    and reverse-engineering its relationships from foreign key metadata.

    In add_relationships(), the builder groups FKs by related table, then uses SQLAlchemy's
    inspect() to retrieve the remote model's mapped columns (instead of accessing __table__ directly).
    This ensures that the columns used in the join condition are actually present on the mapped models.
    """

    def __init__(self, engine: Engine, table_name: str, add_relationships: bool = False, debug: bool = False,
                 logger: Logger = None) -> None:
        self.engine = engine
        self.table_name = table_name
        self.add_relationships = add_relationships
        self.debug = debug
        self.logger = logger or Logger.default_logger(logger_name="sqlalchemy_model_builder", debug=self.debug)
        self.metadata = MetaData()
        # Try to reflect the specified table.
        try:
            self.metadata.reflect(only=[table_name], bind=self.engine)
        except Exception as e:
            self.logger.warning(f"Could not reflect table '{table_name}': {e}. Skipping model build.")
            self.table = None
        else:
            self.table = self.metadata.tables.get(table_name)
            if self.table is None:
                self.logger.warning(f"Table '{table_name}' not found in the database. Skipping model build.")
        # Generate a CamelCase model name.

        self.model_name: str = self.normalize_class_name(table_name)

    def build_model(self) -> Type:
        try:
            self.metadata.reflect(only=[self.table_name], bind=self.engine)
        except Exception as e:
            self.logger.warning(
                f"Could not reflect table '{self.table_name}': {e}. Skipping model build."
            )
            return None

        self.table = self.metadata.tables.get(self.table_name)
        if self.table is None:
            self.logger.warning(
                f"Table '{self.table_name}' not found in the database. Skipping model build."
            )
            return None
        columns = self.get_columns(self.table)
        attrs: Dict[str, Any] = {
            "__tablename__": self.table_name,
            "__table__": self.table,
            "__module__": f"{APPS_LABEL}.models",
            "__mapper_args__": {"eager_defaults": True},
        }
        attrs.update(columns)
        if self.add_relationships:
            self._add_relationships(attrs, self.table)
        model = type(self.model_name, (Base,), attrs)
        MODEL_REGISTRY[self.table_name] = model
        # Validate relationships by forcing SQLAlchemy to configure all mappers.
        try:
            configure_mappers()
            self.logger.debug(f"Successfully configured mappers for model {self.model_name}.")
        except Exception as e:
            self.logger.error(f"Mapper configuration error for model {self.model_name}: {e}")
            # Optionally, you could remove or adjust relationships here before proceeding.
            raise ValueError(f"Invalid relationship configuration in model {self.model_name}: {e}") from e

        self.logger.debug(f"Created model {self.model_name} for table {self.table_name} with relationships.")
        return model

    def get_columns(self, table: Table) -> Dict[str, Any]:
        cols: Dict[str, Any] = {}
        for column in table.columns:
            norm_name = self.normalize_column_name(column.name)
            if norm_name not in RESERVED_COLUMN_NAMES:
                cols[norm_name] = column
        return cols

    def _add_relationships(self, attrs: Dict[str, Any], table: Table) -> None:
        """
        Groups foreign keys by related table name and builds explicit join conditions.
        For each group, it uses the first FK to define foreign_keys and remote_side.
        Uses SQLAlchemy’s inspect() to obtain the remote model's mapped columns.
        Temporarily adds the relationship, forces mapper configuration, and if the relationship
        fails configuration (for example, if the FK column is not marked as a foreign key on either side),
        the relationship is removed.
        """
        inspector = inspect(self.engine)
        fk_info_list = inspector.get_foreign_keys(self.table.name)

        fk_groups = defaultdict(list)
        for fk_info in fk_info_list:
            referred_table = fk_info.get("referred_table")
            if referred_table:
                fk_groups[referred_table].append(fk_info)

        for related_table_name, fk_dicts in fk_groups.items():
            # Ensure the remote model is built.
            try:
                if related_table_name not in MODEL_REGISTRY:
                    self.logger.debug(f"Building missing model for related table {related_table_name}.")
                    remote_model = SqlAlchemyModelBuilder(
                        self.engine,
                        related_table_name,
                        add_relationships=False,  # Skip recursive relationship building.
                        debug=self.debug,
                        logger=self.logger
                    ).build_model()
                    if related_table_name not in MODEL_REGISTRY or remote_model is None:
                        raise ValueError(f"Failed to build model for table {related_table_name}.")
                else:
                    remote_model = MODEL_REGISTRY[related_table_name]
            except Exception as e:
                self.logger.warning(f"Could not build model for table {related_table_name}: {e}")
                continue

            # Get the mapper directly.
            remote_mapper = remote_model.__mapper__
            join_conditions = []
            local_foreign_keys = []
            remote_side_keys = []

            # Build join conditions from FK dictionaries.
            for fk_info in fk_dicts:
                local_cols = fk_info.get("constrained_columns", [])
                remote_cols = fk_info.get("referred_columns", [])
                if not local_cols or not remote_cols:
                    self.logger.warning(
                        f"Incomplete foreign key definition for table {related_table_name} in table {self.table_name}."
                    )
                    continue

                local_col_name = local_cols[0]
                remote_col_name = remote_cols[0]

                try:
                    local_col = self.table.c[local_col_name]
                except KeyError:
                    self.logger.warning(
                        f"Local column {local_col_name} not found in table {self.table_name}. Skipping FK."
                    )
                    continue

                try:
                    remote_col = remote_mapper.columns[remote_col_name]
                except KeyError:
                    self.logger.warning(
                        f"Remote column {remote_col_name} not found in model {remote_model.__name__}. Skipping FK."
                    )
                    continue

                # --- Extra Validation Step ---
                # Ensure the local column is actually defined as a foreign key.
                if not local_col.foreign_keys:
                    self.logger.warning(
                        f"Local column {local_col_name} in table {self.table_name} is not defined as a foreign key. Skipping relationship."
                    )
                    continue
                # Optionally, check that the remote column is part of the remote table.
                if remote_col.name not in remote_model.__table__.columns.keys():
                    self.logger.warning(
                        f"Remote column {remote_col_name} is not present in table for model {remote_model.__name__}. Skipping relationship."
                    )
                    continue

                # Annotate the local column as foreign.
                join_conditions.append(foreign(local_col) == remote_col)
                local_foreign_keys.append(local_col)
                remote_side_keys.append(remote_col)

            if not join_conditions:
                self.logger.warning(
                    f"No valid join conditions for relationship from {self.table_name} to {related_table_name}."
                )
                continue

            primaryjoin_expr = join_conditions[0] if len(join_conditions) == 1 else and_(*join_conditions)
            relationship_name = self.normalize_column_name(related_table_name)
            if relationship_name in attrs:
                continue

            # --- Temporarily add the relationship with the fixed lambda ---
            try:
                attrs[relationship_name] = relationship(
                    lambda rt=related_table_name: MODEL_REGISTRY[rt],
                    primaryjoin=primaryjoin_expr,
                    foreign_keys=local_foreign_keys,
                    remote_side=remote_side_keys,
                    lazy="joined",
                    viewonly=True  # Use viewonly=True if persistence is not needed.
                )
                self.logger.debug(
                    f"Temporarily added relationship {relationship_name} on model {self.model_name} for testing."
                )
            except (ArgumentError, NoForeignKeysError) as e:
                self.logger.error(
                    f"Error creating relationship '{relationship_name}' on model {self.model_name} referencing {related_table_name}: {e}"
                )
                continue

            # --- Validate the relationship by forcing mapper configuration ---
            try:
                configure_mappers()
                self.logger.debug(
                    f"Relationship {relationship_name} on model {self.model_name} validated successfully."
                )
            except Exception as e:
                self.logger.error(
                    f"Relationship '{relationship_name}' on model {self.model_name} failed configuration: {e}"
                )
                del attrs[relationship_name]
                self.logger.debug(
                    f"Removed relationship '{relationship_name}' from model {self.model_name} due to configuration error."
                )
                clear_mappers()
                continue

    @staticmethod
    def normalize_class_name(table_name: str) -> str:
        table_name = str(table_name)
        return "".join(word.capitalize() for word in table_name.split("_"))

    def normalize_column_name(self, column_name: Any) -> str:
        try:
            # Force the column name into a string.
            s = str(column_name)
        except Exception as e:
            self.logger.debug(f"Failed to convert column name {column_name} to string: {e}")
            s = ""
        norm_name = re.sub(r"\W|^(?=\d)", "_", s)
        if norm_name in RESERVED_KEYWORDS:
            norm_name += "_field"
        return norm_name

    @staticmethod
    def export_models_to_file(filename: str) -> None:
        """
        Export dynamically built models (from MODEL_REGISTRY) to a Python file.
        This function writes out a simplified version of each model definition.
        """
        with open(filename, "w") as f:
            # Write header imports.
            f.write("from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey\n")
            f.write("from sqlalchemy.orm import relationship\n")
            f.write("from sqlalchemy.ext.declarative import declarative_base\n\n")
            f.write("Base = declarative_base()\n\n\n")

            for table_name, model in MODEL_REGISTRY.items():
                print(f"Exporting model for table {table_name} as {model.__name__}...")
                # Write the class header.
                f.write(f"class {model.__name__}(Base):\n")
                f.write(f"    __tablename__ = '{table_name}'\n")

                # Write column definitions.
                for column in model.__table__.columns:
                    # Get the column type name (this is a simple conversion).
                    col_type = column.type.__class__.__name__
                    col_def = f"    {column.name} = Column({col_type}"
                    if column.primary_key:
                        col_def += ", primary_key=True"
                    # If needed, you can add more column attributes here.
                    col_def += ")\n"
                    f.write(col_def)

                # Write relationship definitions.
                # This simple example prints relationships with just the target class name.
                for rel in model.__mapper__.relationships:
                    f.write(f"    {rel.key} = relationship('{rel.mapper.class_.__name__}')\n")

                f.write("\n\n")

        print(f"Models exported to {filename}")
