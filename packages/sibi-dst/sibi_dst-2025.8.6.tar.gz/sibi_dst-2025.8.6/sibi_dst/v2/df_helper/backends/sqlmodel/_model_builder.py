import re
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Type, get_args, get_origin

from sqlalchemy import and_, inspect, cast, func
from sqlalchemy.exc import ArgumentError, NoForeignKeysError
from sqlalchemy.orm import relationship, foreign, configure_mappers, clear_mappers
from sqlalchemy.sql.sqltypes import Integer, String, Float, DateTime, Boolean, Numeric, Text

from sqlmodel import SQLModel, create_engine
from sibi_dst.v2.utils import Logger

APPS_LABEL = "datacubes"
RESERVED_COLUMN_NAMES = {"metadata", "class_", "table"}
RESERVED_KEYWORDS = {"class", "def", "return", "yield", "global"}

MODEL_REGISTRY: Dict[str, Type] = {}


class SQLModelModelBuilder:
    """
    Dynamically builds an ORM model for a single table by reflecting its columns
    and reverse-engineering its relationships from foreign key metadata using SQLModel.
    The generated model is mapped solely via its reflected __table__ attribute.
    """

    def __init__(
        self,
        engine,
        table_name: str,
        add_relationships: bool = False,
        debug: bool = False,
        logger: Optional[Logger] = None,
    ) -> None:
        self.engine = engine
        self.table_name = table_name
        self.add_relationships = add_relationships
        self.debug = debug
        self.logger = logger or Logger.default_logger(logger_name="sqlmodel_model_builder", debug=self.debug)
        # Use SQLModel's shared metadata.
        self.metadata = SQLModel.metadata
        self.metadata.bind = self.engine

        try:
            self.metadata.reflect(only=[table_name], bind=self.engine)
        except Exception as e:
            self.logger.warning(f"Could not reflect table '{table_name}': {e}. Skipping model build.")
            self.table = None
        else:
            self.table = self.metadata.tables.get(table_name)
            if self.table is None:
                self.logger.warning(f"Table '{table_name}' not found in the database. Skipping model build.")
        self.model_name: str = self.normalize_class_name(table_name)
        if self.debug:
            self.logger.debug(f"Reflected table for '{table_name}': {self.table}")

    def build_model(self) -> Optional[Type]:
        try:
            self.metadata.reflect(only=[self.table_name], bind=self.engine)
        except Exception as e:
            self.logger.warning(f"Could not reflect table '{self.table_name}': {e}. Skipping model build.")
            return None

        self.table = self.metadata.tables.get(self.table_name)
        if self.table is None:
            self.logger.warning(f"Table '{self.table_name}' not found in the database. Skipping model build.")
            return None

        # Force registration of the reflected table in the metadata.
        try:
            self.metadata._add_table(self.table_name, None, self.table)
        except Exception as e:
            self.logger.debug(f"Error forcing table registration: {e}")

        columns, annotations = self.get_columns(self.table)
        # Build the mapping dictionary using only __table__.
        attrs: Dict[str, Any] = {
            "__table__": self.table,
            "__module__": f"{APPS_LABEL}.models",
            "__mapper_args__": {"eager_defaults": True},
            "__annotations__": annotations,
        }
        attrs.update(columns)
        if self.add_relationships:
            self._add_relationships(attrs, self.table)
        model = type(self.model_name, (SQLModel,), attrs)
        MODEL_REGISTRY[self.table_name] = model

        try:
            configure_mappers()
            self.logger.debug(f"Configured mappers for model {self.model_name}.")
        except Exception as e:
            self.logger.error(f"Mapper configuration error for model {self.model_name}: {e}")
            raise ValueError(f"Invalid mapping in model {self.model_name}: {e}") from e

        # Register the mapping.
        SQLModel.metadata.create_all(self.engine)
        self.logger.debug(f"Created model {self.model_name} for table {self.table_name}.")
        return model

    def get_columns(self, table: Any) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        cols: Dict[str, Any] = {}
        annotations: Dict[str, Any] = {}
        for column in table.columns:
            norm_name = self.normalize_column_name(column.name)
            if norm_name in RESERVED_COLUMN_NAMES:
                continue
            if norm_name in cols:
                self.logger.warning(f"Duplicate normalized column name '{norm_name}'; skipping duplicate for column '{column.name}'.")
                continue
            cols[norm_name] = column
            annotations[norm_name] = self._python_type_for_column(column)
        return cols, annotations

    def _python_type_for_column(self, column: Any) -> Any:
        col_type = type(column.type)
        if issubclass(col_type, Integer):
            return int
        elif issubclass(col_type, (String, Text)):
            return str
        elif issubclass(col_type, (Float, Numeric)):
            return float
        elif issubclass(col_type, DateTime):
            return datetime
        elif issubclass(col_type, Boolean):
            return bool
        else:
            return Any

    def _add_relationships(self, attrs: Dict[str, Any], table: Any) -> None:
        inspector = inspect(self.engine)
        fk_info_list = inspector.get_foreign_keys(self.table.name)
        fk_groups = defaultdict(list)
        for fk_info in fk_info_list:
            referred_table = fk_info.get("referred_table")
            if referred_table:
                fk_groups[referred_table].append(fk_info)

        for related_table_name, fk_dicts in fk_groups.items():
            try:
                if related_table_name not in MODEL_REGISTRY:
                    self.logger.debug(f"Building missing model for related table {related_table_name}.")
                    remote_model = SQLModelModelBuilder(
                        self.engine,
                        related_table_name,
                        add_relationships=False,
                        debug=self.debug,
                        logger=self.logger,
                    ).build_model()
                    if related_table_name not in MODEL_REGISTRY or remote_model is None:
                        raise ValueError(f"Failed to build model for table {related_table_name}.")
                else:
                    remote_model = MODEL_REGISTRY[related_table_name]
            except Exception as e:
                self.logger.warning(f"Could not build model for table {related_table_name}: {e}")
                continue

            remote_table = remote_model.__table__
            join_conditions = []
            local_foreign_keys = []
            remote_side_keys = []
            for fk_info in fk_dicts:
                local_cols = fk_info.get("constrained_columns", [])
                remote_cols = fk_info.get("referred_columns", [])
                if not local_cols or not remote_cols:
                    self.logger.warning(f"Incomplete FK definition for {related_table_name} in {self.table_name}.")
                    continue
                local_col_name = local_cols[0]
                remote_col_name = remote_cols[0]
                try:
                    local_col = self.table.c[local_col_name]
                except KeyError:
                    self.logger.warning(f"Local column {local_col_name} not found in {self.table_name}.")
                    continue
                try:
                    remote_col = remote_table.columns[remote_col_name]
                except KeyError:
                    self.logger.warning(f"Remote column {remote_col_name} not found in model {remote_model.__name__}.")
                    continue
                if not local_col.foreign_keys:
                    self.logger.warning(f"Column {local_col_name} in {self.table_name} is not defined as a foreign key.")
                    continue
                if remote_col.name not in remote_model.__table__.columns.keys():
                    self.logger.warning(f"Remote column {remote_col.name} not in table for model {remote_model.__name__}.")
                    continue
                join_conditions.append(foreign(local_col) == remote_col)
                local_foreign_keys.append(local_col)
                remote_side_keys.append(remote_col)
            if not join_conditions:
                self.logger.warning(f"No valid join conditions for relationship from {self.table_name} to {related_table_name}.")
                continue
            primaryjoin_expr = join_conditions[0] if len(join_conditions) == 1 else and_(*join_conditions)
            relationship_name = self.normalize_column_name(related_table_name)
            if relationship_name in attrs:
                continue
            try:
                rel = relationship(
                    lambda rt=related_table_name: MODEL_REGISTRY[rt],
                    primaryjoin=primaryjoin_expr,
                    foreign_keys=local_foreign_keys,
                    remote_side=remote_side_keys,
                    lazy="joined",
                    viewonly=True,
                )
                attrs[relationship_name] = rel
                attrs.setdefault("__annotations__", {})[relationship_name] = List[remote_model]
                self.logger.debug(f"Added relationship '{relationship_name}' referencing {related_table_name}.")
            except (ArgumentError, NoForeignKeysError) as e:
                self.logger.error(f"Error creating relationship '{relationship_name}' on model {self.model_name}: {e}")
                continue
            try:
                configure_mappers()
                self.logger.debug(f"Validated relationship '{relationship_name}' on model {self.model_name}.")
            except Exception as e:
                self.logger.error(f"Relationship '{relationship_name}' on model {self.model_name} failed configuration: {e}")
                del attrs[relationship_name]
                self.logger.debug(f"Removed relationship '{relationship_name}' from model {self.model_name}.")
                clear_mappers()
                continue

    @staticmethod
    def normalize_class_name(table_name: str) -> str:
        return "".join(word.capitalize() for word in table_name.split("_"))

    def normalize_column_name(self, column_name: Any) -> str:
        try:
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
        reserved_attrs = {"metadata", "__tablename__", "__sqlmodel_relationships__", "__name__"}
        import re
        import typing

        with open(filename, "w") as f:
            f.write("from sqlmodel import SQLModel, Field, Relationship, Column\n")
            f.write("from sqlalchemy import ForeignKey\n")
            f.write("from sqlalchemy.sql.elements import DefaultClause\n")
            f.write("from sqlalchemy.sql.sqltypes import INTEGER, DATE, VARCHAR, SMALLINT, FLOAT, CHAR, TEXT, DATETIME\n")
            f.write("from sqlalchemy.dialects.mysql import TINYINT\n")
            f.write("from typing import Any, List, Optional, Union\n")
            f.write("import typing\n")
            f.write("import sqlalchemy\n\n\n")

            f.write("class Base(SQLModel):\n")
            f.write("    class Config:\n")
            f.write("        arbitrary_types_allowed = True\n\n\n")

            for table_name, model in MODEL_REGISTRY.items():
                f.write(f"class {model.__name__}(SQLModel, table=True):\n")
                f.write(f"    __tablename__ = '{table_name}'\n")
                for column in model.__table__.columns:
                    col_repr = repr(column)
                    col_repr = re.sub(r", table=<[^>]+>", "", col_repr)
                    col_repr = re.sub(r",\s*server_default=DefaultClause\([^)]*\)", "", col_repr)
                    col_repr = re.sub(r",\s*display_width=\d+", "", col_repr)
                    f.write(f"    {column.name}: Any = Field(sa_column={col_repr})\n")
                annotations = typing.get_type_hints(model)
                col_names = {col.name for col in model.__table__.columns}
                for key, type_hint in annotations.items():
                    if key in col_names or key in reserved_attrs or key.startswith("__"):
                        continue
                    origin = get_origin(type_hint)
                    if origin in (list, List):
                        remote_model = get_args(type_hint)[0]
                        remote_model_name = remote_model.__name__
                    elif origin is Optional:
                        args = get_args(type_hint)
                        non_none = [arg for arg in args if arg is not type(None)]
                        remote_model_name = non_none[0].__name__ if non_none else "Any"
                    else:
                        remote_model_name = type_hint.__name__ if hasattr(type_hint, '__name__') else str(type_hint)
                    f.write(f"    {key}: {type_hint} = Relationship(\"{remote_model_name}\")\n")
                f.write("\n\n")
        print(f"Models exported to {filename}")