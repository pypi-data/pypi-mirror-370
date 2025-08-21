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
    Dict,
    Optional,
    Union,
    List,
    Literal,
    TYPE_CHECKING
)
from sqlalchemy import ForeignKeyConstraint

from tai_sql import pm
if TYPE_CHECKING:
    from .table import Table
    from .columns import Column

@dataclass
class ForeignKey:

    """"Clase para definir una clave foránea compuesta.
    Esta clase se utiliza para definir relaciones entre tablas
    """

    model: Union[Table, str]
    relation: Relation
    is_composite: bool

    def __post_init__(self) -> None:
        self.validate()
                
    def validate(self) -> None:
        if len(self.relation.fields) == 0 or len(self.relation.references) == 0:
            raise ValueError("La relación debe tener al menos un campo definido en 'fields' y 'references'")
    
    def info(self) -> Dict[str, Any]:
        """
        Devuelve un diccionario con la información de la clave foránea.
        """

        return {
            'local_columns': self.local_columns_names,
            'target_columns': self.target_columns_names,
            'constraint_name': self.contraint_name,
            'is_simple': len(self.relation.fields) == 1,
            'is_composite': len(self.relation.fields) > 1,
            'ondelete': self.on_delete,
            'onupdate': self.on_update
        }
    
    @property
    def contraint_name(self) -> str:
        """
        Devuelve el nombre del constraint de la clave foránea.
        """
        return f"fk_{self.model.tablename}_{self.relation.target.tablename}"
    
    @property
    def on_delete(self) -> str:
        """
        Devuelve el comportamiento de eliminación de la relación.
        """
        return self.relation.onDelete.upper()
    
    @property
    def on_update(self) -> str:
        """
        Devuelve el comportamiento de actualización de la relación.
        """
        return self.relation.onUpdate.upper()

    @property
    def local_columns(self) -> List[Column]:
        """
        Devuelve las columnas locales identificadas como ForeignKey
        """
        columns = []
        for name, col in self.model.columns.items():
            if name in self.relation.fields:
                columns.append(col)

        return columns
    
    @property
    def local_columns_names(self) -> List[str]:
        """
        Devuelve los nombres de las columnas locales
        """
        return [col.name for col in self.local_columns]
    
    @property
    def target_columns(self) -> List[Column]:
        """
        Devuelve las columnas objetivo identificadas como PrimaryKey
        """
        columns = []
        for name, col in self.relation.target.columns.items():
            if name in self.relation.references:
                columns.append(col)
        
        return columns
    
    @property
    def target_columns_names(self) -> List[str]:
        """
        Devuelve los nombres de las columnas objetivo
        """
        target_columns = []
        for col in self.target_columns:
            if pm.db.provider.drivername == 'postgresql':
                target_columns.append(f"{pm.db.schema_name}.{self.relation.target.tablename}.{col.name}")
            else:
                target_columns.append(f"{self.relation.target.tablename}.{col.name}")
        return target_columns
    
    def to_sqlalchemy_foreign_key(self):
        """
        Convierte la relación a una ForeignKeyConstraint de SQLAlchemy.
        
        Returns:
            ForeignKeyConstraint: Constraint de clave foránea para SQLAlchemy
            
        Raises:
            ValueError: Si la relación no es válida para ser clave foránea
        """

        # Crear ForeignKeyConstraint
        return ForeignKeyConstraint(
            columns=self.local_columns_names,           # Columnas locales
            refcolumns=self.target_columns_names,     # Columnas de referencia
            name=self.contraint_name,          # Nombre del constraint
            ondelete=self.on_delete,       # Comportamiento al eliminar
            onupdate=self.on_update        # Comportamiento al actualizar
        )
        

@dataclass
class Relation:
    """Clase para definir una relación entre tablas"""
    name: str = None
    local: Table = None
    target: Table = None
    implicit: bool = False # Indica si es una relación implícita
    columns: List[Column] = field(default_factory=list)  #  List of foreign key columns in the local table
    fields: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    onDelete: str = 'cascade'
    onUpdate: str = 'cascade'
    backref: Optional[str] = None
    direction: Optional[Literal['one-to-many', 'many-to-one']] = None

    def __post_init__(self) -> None:

        if not self.implicit:
            if self.backref is None:
                raise ValueError("El atributo 'backref' no puede ser None para relaciones explícitas")
    
    def validate(self) -> None:

        if len(self.fields) != len(self.references):
            raise ValueError("Los campos de la relación deben tener el mismo número de elementos en 'fields' y 'references'")
        
        if len(self.fields) == 0 or len(self.references) == 0:
            raise ValueError("La relación debe tener al menos un campo definido en 'fields' y 'references'")

        for field_name in self.fields:
            if field_name not in self.local.columns:
                raise ValueError(f"El campo '{field_name}' no se encuentra definido en '{self.local.__name__}'")
            
        for ref_name in self.references:
            if ref_name not in self.target.columns:
                raise ValueError(f"La referencia '{ref_name}' no se encuentra definida en '{self.target.__name__}'")

        for field_name, ref_name in zip(self.fields, self.references):
            local_col = self.local.columns[field_name]
            target_col = self.target.columns[ref_name]
            local_type = local_col.user_defined_sqlalchemy_type or local_col.type
            target_type = target_col.user_defined_sqlalchemy_type or target_col.type

            if local_type != target_type:
                raise ValueError(
                    f"Incompatibilidad de tipos de columnas en la relación '{self.name}':\n"
                    f"  - '{self.local.__name__}.{field_name}' ({local_type})\n"
                    f"  - '{self.target.__name__}.{ref_name}' ({target_type})\n"
                    "Los tipos de datos son incompatibles."
                )

    def info(self) -> Dict[str, Any]:
        """
        Devuelve un diccionario con la información de la relación.
        
        Este método se utiliza para obtener una representación de la relación
        que incluye su nombre, campos, referencias y otros atributos relevantes.
        
        Returns:
            Dict: Diccionario con la información de la relación
        """
        if self.direction == 'one-to-many':
            target_type = f"List[{self.target.__name__}]"
        else:
            target_type = self.target.__name__

        return {
            'name': self.name,
            'local': self.local.__name__,
            'target': self.target.__name__,
            'target_type': target_type,
            'fields': self.fields,
            'references': self.references,
            'onDelete': self.onDelete,
            'onUpdate': self.onUpdate,
            'backref': self.backref,
            'direction': self.direction,
            'is_list': self.direction == 'one-to-many',
            'description': self.target.__doc__ or "",
        }
    
    @property
    def is_composite(self) -> bool:
        """
        Verifica si la relación es compuesta (tiene más de un campo y referencia).
        
        Returns:
            bool: True si es una relación compuesta, False en caso contrario
        """
        return len(self.fields) > 1 and len(self.references) > 1
    
    def store(self) -> None:
        """
        Almacena la relación en el modelo local.
        Esta función se utiliza para registrar la relación en el modelo local
        y establecer las propiedades necesarias.
        """
        if self.name in self.local.relations:
            raise ValueError(f"La relación '{self.name}' ya está definida en '{self.local.__class__.__name__}'")
        
        if self.name in (None, ''):
            raise ValueError("El nombre de la relación no puede ser None o vacío")
        
        if self.local is None:
            raise ValueError("El modelo local no puede ser None")
        
        if self.target is None:
            raise ValueError("El modelo objetivo no puede ser None")
        
        self.local.relations[self.name] = self

    
    def save(self) -> None:
        """
        Guarda la relación en el modelo local.
        Esta función se utiliza para registrar la relación en el modelo local
        y establecer las propiedades necesarias.
        """
        self.validate()
        if not self.implicit:
            self.store()
            self.local.foreign_keys.append(ForeignKey(model=self.local, relation=self, is_composite=self.is_composite))
            for col in self.columns:
                col.is_foreign_key = True
        else:
            setattr(self.local, self.name, self)

    
    def lazy_save(self) -> None:
        """
        Guarda la relación de forma perezosa.
        Esta función se utiliza para registrar la relación en el modelo local
        sin establecer las propiedades necesarias inmediatamente.
        """
        success = False
        
        for target_relation in self.target.relations.values():
            if target_relation.implicit:
                continue
            if target_relation.backref == self.name and self.local is target_relation.target:
                self.fields = target_relation.references
                self.references = target_relation.fields
                self.onDelete = target_relation.onDelete
                self.onUpdate = target_relation.onUpdate
                self.backref = target_relation.name
                success = True
                break
        
        if not success:
            raise ValueError(f"No se pudo encontrar una relación inversa para '{self.name}' en '{self.target.__class__.__name__}'")

        self.save()

def relation(
    fields: List[str],
    references: List[str],
    backref: str,
    onDelete: Literal['cascade', 'set null', 'restrict']='cascade',
    onUpdate: Literal['cascade', 'delete', 'restrict']='cascade',
):
    """
    Define una relación virtual entre tablas.
    
    Args:
        fields: Lista de nombres de campos en esta tabla que forman la relación
        references: Lista de nombres de campos en la tabla relacionada
        backref: Nombre del atributo inverso en la otra tabla
        onDelete: Comportamiento al eliminar ('cascade', 'restrict', 'set null', etc)
        onUpdate: Comportamiento al actualizar ('cascade', 'restrict', 'set null', etc)
        
    Ejemplo:
        author: User = relation(fields=['author_id'], references=['id'])
    """
    return Relation(
        fields=fields,
        references=references,
        onDelete=onDelete,
        onUpdate=onUpdate,
        backref=backref
    )