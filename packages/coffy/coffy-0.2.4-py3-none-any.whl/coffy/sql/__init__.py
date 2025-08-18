# coffy/sql/__init__.py
# author: nsarathy

from typing import Any, Dict, Union

from .engine import execute_query, initialize, close_connection
from .sqldict import SQLDict

# Optional, only if you want advanced users to grab the live connection
# from .engine import get_connection

# ORM re-exports for convenient imports: from coffy.sql import Model, Integer, ...
from .orm import Model as Model
from .orm import Integer as Integer
from .orm import Real as Real
from .orm import Text as Text
from .orm import Blob as Blob
from .orm import Manager as Manager
from .orm import Query as Query
from .orm import raw as raw
from .orm import to_sqldict as to_sqldict


def init(path: str | None = None) -> None:
    """Initialize the SQL engine with the given path. None uses in-memory."""
    initialize(path)


def query(sql: str) -> Union[SQLDict, Dict[str, Any]]:
    """Execute a SQL statement. SELECT returns SQLDict, others return a status dict."""
    return execute_query(sql)


def close() -> None:
    """Close the database connection."""
    close_connection()


__all__ = [
    # core API
    "init",
    "query",
    "close",
    # result wrapper
    "SQLDict",
    # ORM surface
    "Model",
    "Integer",
    "Real",
    "Text",
    "Blob",
    "Manager",
    "Query",
    "raw",
    "to_sqldict",
    # "get_connection",  # uncomment if you choose to expose it
]
