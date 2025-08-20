from __future__ import annotations

import hashlib
import threading
from typing import Dict, Optional, Tuple

from sqlalchemy import MetaData, Table
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


# Backward-compatible default module label for generated classes
apps_label = "datacubes.models"


class ModelRegistry:
    """
    Thread-safe registry that reflects tables once per (engine, schema) and
    returns a single mapped class per (engine, schema, table).
    """

    def __init__(self) -> None:
        self._metadata_cache: Dict[Tuple[str, Optional[str]], MetaData] = {}
        self._model_cache: Dict[Tuple[str, Optional[str], str], type] = {}
        self._lock = threading.RLock()
        self._md_locks: Dict[Tuple[str, Optional[str]], threading.Lock] = {}

    # ---------- key helpers ----------
    @staticmethod
    def _engine_key(engine: Engine) -> str:
        return str(engine.url)

    @staticmethod
    def _qualified_key(schema: Optional[str], table: str) -> str:
        return f"{schema}.{table}" if schema else table

    @staticmethod
    def _split_schema_and_table(name: str) -> Tuple[Optional[str], str]:
        if "." in name:
            s, t = name.split(".", 1)
            return (s or None), t
        return None, name

    # ---------- class name helpers ----------
    @staticmethod
    def _normalize_class_name(table_name: str) -> str:
        return "".join(part.capitalize() for part in table_name.split("_"))

    @staticmethod
    def _short_hash(*parts: str, length: int = 8) -> str:
        h = hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()
        return h[:length]

    def _is_class_name_taken(self, class_name: str, module_label: str) -> bool:
        # Avoid SA private registries; inspect mappers instead (public)
        for mapper in list(Base.registry.mappers):
            try:
                cls = mapper.class_
                if getattr(cls, "__name__", None) == class_name and getattr(cls, "__module__", None) == module_label:
                    return True
            except Exception:
                continue
        return False

    def _find_existing_model_for_table(self, tbl: Table) -> Optional[type]:
        for mapper in list(Base.registry.mappers):
            try:
                mapped_cls = mapper.class_
                mapped_tbl = getattr(mapped_cls, "__table__", None)
                if mapped_tbl is tbl:
                    return mapped_cls
                if isinstance(mapped_tbl, Table):
                    if (mapped_tbl.schema == tbl.schema) and (mapped_tbl.name == tbl.name):
                        return mapped_cls
            except Exception:
                continue
        return None

    # ---------- metadata helpers ----------
    def _get_or_create_metadata(self, ekey: str, schema: Optional[str]) -> MetaData:
        md_key = (ekey, schema)
        with self._lock:
            md = self._metadata_cache.get(md_key)
            if md is None:
                md = MetaData(schema=schema)
                self._metadata_cache[md_key] = md
            return md

    def _get_or_create_md_lock(self, md_key: Tuple[str, Optional[str]]) -> threading.Lock:
        with self._lock:
            lock = self._md_locks.get(md_key)
            if lock is None:
                lock = threading.Lock()
                self._md_locks[md_key] = lock
            return lock

    # ---------- public API ----------
    def get_model(
        self,
        engine: Engine,
        table_name: str,
        *,
        refresh: bool = False,
        schema: Optional[str] = None,
        module_label: Optional[str] = None,
        prefer_stable_names: bool = True,
    ) -> type:
        s2, tname = self._split_schema_and_table(table_name)
        schema = schema if schema is not None else s2
        ekey = self._engine_key(engine)
        model_key = (ekey, schema, tname)
        md_key = (ekey, schema)
        module_label = module_label or apps_label

        if refresh:
            with self._lock:
                self._model_cache.pop(model_key, None)
                self._metadata_cache.pop(md_key, None)
                self._md_locks.pop(md_key, None)

        # fast path: already cached model
        with self._lock:
            m = self._model_cache.get(model_key)
            if m is not None:
                return m

        # ensure metadata and reflection are serialized per (engine, schema)
        md = self._get_or_create_metadata(ekey, schema)
        md_lock = self._get_or_create_md_lock(md_key)
        qname = self._qualified_key(schema, tname)

        tbl = md.tables.get(qname)
        if tbl is None:
            with md_lock:
                # double-checked reflection
                tbl = md.tables.get(qname)
                if tbl is None:
                    md.reflect(bind=engine, only=[qname])
                tbl = md.tables.get(qname)

        if tbl is None:
            raise ValueError(f"Table '{qname}' does not exist in the database.")

        # If a mapped model for this Table already exists (anywhere), reuse it
        reused = self._find_existing_model_for_table(tbl)
        if reused is not None:
            with self._lock:
                self._model_cache[model_key] = reused
            return reused

        # pick class name
        base_name = self._normalize_class_name(tname)
        final_name = base_name
        if self._is_class_name_taken(base_name, module_label):
            # optionally keep stable names by suffixing with a short hash
            if prefer_stable_names:
                suffix = self._short_hash(ekey, schema or "", tname)
                final_name = f"{base_name}_{suffix}"
            else:
                # let SQLAlchemy registry replacement occur (not recommended)
                suffix = self._short_hash(ekey, schema or "", tname)
                final_name = f"{base_name}_{suffix}"

        # build the model
        attrs = {
            "__tablename__": tbl.name,
            "__table__": tbl,
            "__module__": module_label,
        }
        model_cls = type(final_name, (Base,), attrs)

        with self._lock:
            self._model_cache[model_key] = model_cls
        return model_cls

    def clear(self) -> None:
        with self._lock:
            self._metadata_cache.clear()
            self._model_cache.clear()
            self._md_locks.clear()


# Process-wide registry & helper
_global_registry = ModelRegistry()

def get_global_registry() -> ModelRegistry:
    return _global_registry