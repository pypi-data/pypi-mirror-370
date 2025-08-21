# -*- coding: utf-8 -*-
"""
Declarative models for SQLAlchemy.
This module provides the base classes and utilities to define
models using SQLAlchemy's declarative system.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import (
    Any,
    List,
    Dict,
    Optional,
    Union,
    TYPE_CHECKING,
)
from enum import Enum
from pydantic import BaseModel, Field
from sqlalchemy import (
    Integer, String, Text, Boolean, DateTime, 
    Date, Time, Float, Numeric, LargeBinary,
    BigInteger,
    Column as SQLAlchemyColumn,
    Enum as SQLAlchemyEnum
)

if TYPE_CHECKING:
    from .table import Table

class ColumnArgs(BaseModel):
    """
    Clase para definir los argumentos de una columna.
    Utilizada para definir los metadatos de las columnas.
    """
    primary_key: bool = Field(default=False, description="Indica si es clave primaria")
    unique: bool | None = Field(default=None, description="Indica si es única")
    default: Any = Field(default=None, description="Valor por defecto de la columna")
    index: bool = Field(default=False, description="Indica si debe tener un índice")
    autoincrement: bool = Field(default=False, description="Indica si es autoincremental")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte los argumentos de la columna a un diccionario.
        
        Returns:
            dict: Diccionario con los argumentos de la columna
        """
        if self.default is not None:
        
            if isinstance(self.default, Enum):
                self.default = self.default.value

            elif hasattr(self.default, '__self__') and self.default.__self__.__name__ == 'datetime':
                if hasattr(self.default, '__name__') and self.default.__name__ == 'today':
                    self.default = 'datetime.today'
                elif hasattr(self.default, '__name__') and self.default.__name__ == 'now':
                    self.default = 'datetime.now'
                else:
                    self.default = str(self.default)

        return self.model_dump()

@dataclass
class Column:

    name: str = None
    type: Any = None
    user_defined_sqlalchemy_type: Any = None
    model: Optional[Table] = None
    options: Optional[List[Any]] = None
    nullable: bool = False
    is_foreign_key: bool = False
    server_now: bool = False
    encrypt: bool = False
    args: ColumnArgs = field(default_factory=ColumnArgs)
    description: str = ''
    
    def info(self) -> Dict[str, Any]:
        """
        Devuelve un diccionario con la información de la columna.
        """
        return {
            'name': self.name,
            'type': self.type,
            'user_defined_sqlalchemy_type': self.user_defined_sqlalchemy_type,
            'options': self.options,
            'nullable': self.nullable,
            'is_foreign_key': self.is_foreign_key,
            'default': self.args.to_dict().get('default'),
            'encrypt': self.encrypt,
            'args': self.args.to_dict(),
            'no_args': self.no_args,
            'description': self.description or f"Campo { self.name } de la tabla { self.model.tablename }",
        }
    
    @property
    def sqlalchemy_type_mapping(self) -> Dict[str, Any]:
        return {
            'int': Integer,
            'BigInteger': BigInteger,
            'str': String,
            'bool': Boolean,
            'datetime': DateTime,
            'date': Date,
            'time': Time,
            'float': Float,
            'Numeric': Numeric,
            'bytes': LargeBinary,
            'LargeBinary': LargeBinary,
            'Enum': SQLAlchemyEnum,
        }
    
    def to_sqlalchemy_column(self) -> SQLAlchemyColumn:
        """Convierte la definición de columna a SQLAlchemy Column"""
       
        # Obtener tipo SQLAlchemy
        sqlalchemy_type = self.sqlalchemy_type_mapping.get(self.user_defined_sqlalchemy_type or self.type)

        if sqlalchemy_type is None:
            raise ValueError(f"Tipo de dato '{self.type}' no soportado para la columna '{self.name}'")
        
        if self.server_now:
            from sqlalchemy.sql.functions import now
            server_default = now()
        else:
            server_default = None

        # Crear columna SQLAlchemy
        return SQLAlchemyColumn(
            self.name,
            sqlalchemy_type,
            nullable=self.nullable,
            **self.args.to_dict(),
            server_default=server_default
        )

    @property
    def no_args(self) -> bool:
        """
        Verifica si la columna se puede definir solo con su tipo de dato.
        
        Returns:
            bool: True si es una columna simple, False en caso contrario
        """
        return not bool(self.args.model_dump(exclude_defaults=True))
    
    def save(self) -> None:
        """
        Guarda la columna en el modelo.
        Esta función se utiliza para registrar la columna en el modelo
        y establecer las propiedades necesarias.
        """
        if self.model is None:
            raise ValueError("El modelo de la columna no puede ser None")
        
        if self.name in (None, ''):
            raise ValueError("El nombre de la columna no puede ser None o vacío")
        
        if self.type is None:
            raise ValueError("El tipo de la columna no puede ser None")
        
        self.model.columns[self.name] = self

        if getattr(self.model, self.name, None) is None:
            setattr(self.model, self.name, self)

def column(
    primary_key: bool = False,
    unique: bool | None = False,
    default: Any = None,
    server_now: bool = False,
    index: bool = False,
    autoincrement: bool = False,
    encrypt: bool = False,
    description: str = ''
):
    """
    Configurador para añadir metadatos a las columnas definidas por tipado.
    
    Ejemplo:
        id: int = column(primary_key=True, autoincrement=True)
        name: str = column(length=100)
        password: str = column(encrypt=True)
    """
    return Column(
        args=ColumnArgs(
            primary_key=primary_key,
            unique=unique or None,
            default=default,
            index=index,
            autoincrement=autoincrement,
        ),
        server_now=server_now,
        encrypt=encrypt,
        description=description
    )
