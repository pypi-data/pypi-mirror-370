"""
Declarative models for SQLAlchemy.
This module provides the base classes and utilities to define
models using SQLAlchemy's declarative system.
"""
from __future__ import annotations
from sqlalchemy.types import (
    BigInteger as bigint,
    Text as text,
    Numeric as numeric,
    LargeBinary as largebinary,
)

from datetime import datetime, date, time
from typing import List, Optional

from .project import ProjectManager as pm
from .core import datasource, generate, env, connection_string, params, query
from .orm import Table, View, Enum, column, relation
from .drivers import postgresql, mysql, sqlserver

# Exportar los elementos principales
__all__ = [
    'datasource', 
    'generate',
    'env',
    'connection_string',
    'params',
    'Table',
    'column',
    'relation',
    'List',
    'Optional',
    'datetime',
    'date',
    'time',
    'bigint',
    'text',
    'numeric',
    'largebinary',
    'query',
    'View',
    'Enum',
]