#  Copyright (c) 2023. ISTMO Center S.A.  All Rights Reserved
#
import json
from typing import Dict

import pandas as pd
from sqlalchemy import String, Text, Integer, BigInteger, SmallInteger, Float, Boolean, DateTime, Date, Time, JSON, \
    Numeric, UUID
from sqlalchemy.dialects.mysql import TINYINT, MEDIUMTEXT

# This is the defaults configuration file for the df_helper module.

# conversion_map is a dictionary that maps the field types to their corresponding data type conversion functions.
# Each entry in the dictionary is a pair of a field type (as a string) and a callable function that performs the
# conversion. This mapping is used to convert the values in a pandas DataFrame to the appropriate data types based on
# the db field type.

sqlalchemy_field_conversion_map_dask: Dict[str, callable] = {
    String.__name__: lambda x: x.astype(str).fillna(""),
    Text.__name__: lambda x: x.fillna('').astype(str),
    Integer.__name__: lambda x: x.fillna(0).astype(int),
    BigInteger.__name__: lambda x: pd.to_numeric(x, errors="coerce"),
    SmallInteger.__name__: lambda x: pd.to_numeric(x, errors="coerce"),
    Float.__name__: lambda x: pd.to_numeric(x, errors="coerce"),
    Numeric.__name__: lambda x: pd.to_numeric(x, errors="coerce"),
    Boolean.__name__: lambda x: x.astype(bool),
    DateTime.__name__: lambda x: pd.to_datetime(x, errors="coerce"),
    Date.__name__: lambda x: pd.to_datetime(x, errors="coerce").map_partitions(lambda x: x.dt.date,
                                                                               meta=("date", "object")),
    Time.__name__: lambda x: pd.to_datetime(x, errors="coerce").map_partitions(lambda x: x.dt.time,
                                                                               meta=("time", "object")),
    JSON.__name__: lambda x: x.map_partitions(lambda s: s.apply(json.loads), meta=("json", "object")),
    UUID.__name__: lambda x: x.astype(str),
}


# Conversion map with normalized SQLAlchemy field types
# sqlalchemy_field_conversion_map_dask: Dict[str, callable] = {
#     "String": lambda x: x.map_partitions(lambda s: s.astype(str), meta=("string", "string")),
#     "Text": lambda x: x.map_partitions(lambda s: s.astype(str), meta=("text", "string")),
#     "Integer": lambda x: pd.to_numeric(x, errors="coerce"),
#     "SmallInteger": lambda x: pd.to_numeric(x, errors="coerce"),
#     "BigInteger": lambda x: pd.to_numeric(x, errors="coerce"),
#     "Float": lambda x: pd.to_numeric(x, errors="coerce"),
#     "Numeric": lambda x: pd.to_numeric(x, errors="coerce"),
#     "Boolean": lambda x: x.map_partitions(lambda s: s.fillna(False).astype(bool), meta=("boolean", "bool")),
#     "DateTime": lambda x: pd.to_datetime(x, errors="coerce"),
#     "Date": lambda x: pd.to_datetime(x, errors="coerce").map_partitions(lambda s: s.dt.date, meta=("date", "object")),
#     "Time": lambda x: pd.to_datetime(x, errors="coerce").map_partitions(lambda s: s.dt.time, meta=("time", "object")),
#     "JSON": lambda x: x.map_partitions(lambda s: s.apply(json.loads), meta=("json", "object")),
# }


def normalize_sqlalchemy_type(field_type):
    """
    Normalize SQLAlchemy field types to generic type names.
    Handles dialect-specific types (e.g., MySQL).
    """
    # Map of generic SQLAlchemy types
    type_mapping = {
        String: "String",
        Text: "Text",
        Integer: "Integer",
        SmallInteger: "SmallInteger",
        BigInteger: "BigInteger",
        Float: "Float",
        Numeric: "Numeric",
        Boolean: "Boolean",
        DateTime: "DateTime",
        Date: "Date",
        Time: "Time",
        JSON: "JSON",
    }

    # Dialect-specific types
    dialect_mapping = {
        TINYINT: "SmallInteger",
        MEDIUMTEXT: "Text",
    }

    # Check if the field matches a generic or dialect-specific type
    for sql_type, name in {**type_mapping, **dialect_mapping}.items():
        if isinstance(field_type, sql_type):
            return name

    # Fallback to raw class name
    return field_type.__class__.__name__
