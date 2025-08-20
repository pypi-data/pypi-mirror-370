import keyword
import re
import threading
from sqlalchemy.engine import Engine

from ._model_registry import ModelRegistry, apps_label


# Global process-wide registry for backward compatibility
_global_model_registry = ModelRegistry()


class SqlAlchemyModelBuilder:
    """
    Builds a single SQLAlchemy ORM model from a specific database table.
    Thread-safe and uses a process-wide registry for reuse.

    Backward compatibility:
      - Keeps CamelCase(table) as preferred class name
      - Publishes classes under `apps_label` unless overridden
      - Public API unchanged
    """

    _lock = threading.Lock()

    def __init__(self, engine: Engine, table_name: str):
        self.engine = engine
        self.table_name = table_name

    def build_model(self) -> type:
        with self._lock:
            return _global_model_registry.get_model(
                engine=self.engine,
                table_name=self.table_name,
                module_label=apps_label,
                prefer_stable_names=True,
            )

    @staticmethod
    def _normalize_class_name(table_name: str) -> str:
        return "".join(word.capitalize() for word in table_name.split("_"))

    @staticmethod
    def _normalize_column_name(column_name: str) -> str:
        sane_name = re.sub(r"\W", "_", column_name)
        sane_name = re.sub(r"^\d", r"_\g<0>", sane_name)
        if keyword.iskeyword(sane_name):
            return f"{sane_name}_field"
        return sane_name

# import re
# import keyword
# import threading
# from sqlalchemy import MetaData, Engine
# from sqlalchemy.orm import DeclarativeBase
#
#
# class Base(DeclarativeBase):
#     """Shared declarative base for all ORM models."""
#     pass
#
#
# apps_label = "datacubes.models"
#
#
# class SqlAlchemyModelBuilder:
#     """
#     Builds a single SQLAlchemy ORM model from a specific database table.
#     This class is thread-safe and caches reflected table metadata to
#     improve performance across multiple instantiations.
#     """
#     _lock = threading.Lock()
#     _metadata_cache: dict[str, MetaData] = {}
#
#     def __init__(self, engine: Engine, table_name: str):
#         """
#         Initializes the model builder for a specific table.
#
#         Args:
#             engine: The SQLAlchemy engine connected to the database.
#             table_name: The name of the table to generate the model for.
#         """
#         self.engine = engine
#         self.table_name = table_name
#         self.class_name = self._normalize_class_name(self.table_name)
#
#         engine_key = str(engine.url)
#
#         # ✅ REFACTOR: Acquire lock to make cache access and creation atomic,
#         # preventing a race condition between multiple threads.
#         with self._lock:
#             if engine_key not in self._metadata_cache:
#                 self._metadata_cache[engine_key] = MetaData()
#             self.metadata = self._metadata_cache[engine_key]
#
#     def build_model(self) -> type:
#         """
#         Builds and returns a database model class for the specified table.
#         This process is atomic and thread-safe.
#
#         Raises:
#             ValueError: If the specified table does not exist in the database.
#         Returns:
#             The dynamically created ORM model class.
#         """
#         with self._lock:
#             # NOTE: Using a private SQLAlchemy API. This is a performance
#             # optimization but may break in future versions of the library.
#             registered_model = Base.registry._class_registry.get(self.class_name)
#             if registered_model:
#                 return registered_model
#
#             # Check if the table's schema is in our metadata cache
#             table = self.metadata.tables.get(self.table_name)
#
#             # If not cached, reflect it from the database
#             if table is None:
#                 self.metadata.reflect(bind=self.engine, only=[self.table_name])
#                 table = self.metadata.tables.get(self.table_name)
#
#             if table is None:
#                 raise ValueError(
#                     f"Table '{self.table_name}' does not exist in the database."
#                 )
#
#             # Create the model class dynamically.
#             attrs = {
#                 "__tablename__": table.name,
#                 "__table__": table,
#                 "__module__": apps_label,
#             }
#             model = type(self.class_name, (Base,), attrs)
#
#             return model
#
#     @staticmethod
#     def _normalize_class_name(table_name: str) -> str:
#         """Converts a snake_case table_name to a CamelCase class name."""
#         return "".join(word.capitalize() for word in table_name.split("_"))
#
#     @staticmethod
#     def _normalize_column_name(column_name: str) -> str:
#         """
#         Sanitizes a column name to be a valid Python identifier.
#         (Kept for utility, though not used in the final model creation).
#         """
#         sane_name = re.sub(r"\W", "_", column_name)
#         sane_name = re.sub(r"^\d", r"_\g<0>", sane_name)
#
#         if keyword.iskeyword(sane_name):
#             return f"{sane_name}_field"
#         return sane_name
#
#
