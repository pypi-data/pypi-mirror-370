from __future__ import annotations
from typing import Any, Dict, ClassVar, List, get_type_hints, TYPE_CHECKING
from abc import ABC, abstractmethod
from sqlalchemy import MetaData

from .columns import Column
from .utils import (
    is_column_type,
    is_optional,
    mapped_type,
    get_type_if_is_sqlalchemy_type,
    enum_options
)

if TYPE_CHECKING:
    from .table import Table  # Evitar circular imports
    from .view import View    # Evitar circular imports


class DatabaseObject(ABC):
    """
    Clase base abstracta para objetos de base de datos (Tables y Views).
    
    Proporciona funcionalidad común para análisis de type hints,
    manejo de columnas y conversión a SQLAlchemy.
    """
    
    __abstract__ = True
    __name__: ClassVar[str]  # Nombre del objeto (tabla o vista)
    __is_view__: ClassVar[bool] = False  # Indica si es una vista
    __description__: ClassVar[str] = ""  # Descripción opcional del objeto
    __examples__: ClassVar[tuple] = ()  # Ejemplos de datos para el objeto
    # Registro centralizado de todos los objetos de BD
    registry: ClassVar[List[DatabaseObject]] = []
    
    # Columnas comunes a tablas y vistas
    columns: ClassVar[Dict[str, Column]] = {}
    
    def __init_subclass__(cls) -> None:
        """Inicialización común para subclases"""
        super().__init_subclass__()
        
        # Inicializar diccionarios para esta clase específica
        cls.columns = {}
        
        if not hasattr(cls, '__name__'):
            raise ValueError(f"El objeto {cls.__name__} debe definir un atributo __name__")
        
        cls._name = cls.__name__
        cls._description = cls.__description__ or cls.__doc__ or ""
        cls._examples = cls.__examples__ or ()

        if cls._name in 'Base':
            raise ValueError(f"El objeto {cls.__name__} no puede llamarse 'Base'")
        
        # Solo añadir al registro si no es una clase abstracta
        if cls._should_register():
            DatabaseObject.registry.append(cls)

    @classmethod
    def _should_register(cls) -> bool:
        """
        Determina si la clase debe ser registrada.
        
        Returns:
            bool: True si debe registrarse, False si es una clase base o abstracta
        """
        # Clases que nunca deben registrarse (clases base del framework)
        framework_classes = {
            'DatabaseObject',
            'Table', 
            'View'
        }
        
        # No registrar clases del framework
        if cls.__name__ in framework_classes:
            return False
        
        # Si llegamos aquí, es una clase concreta que debe registrarse
        return True
    
    @classmethod
    def analyze_columns(cls) -> None:
        """
        Analiza los type hints de la clase para descubrir columnas.
        Método común para Tables y Views.
        """
        type_hints = get_type_hints(cls)
        
        for name, hint in type_hints.items():
            # Ignorar atributos especiales y de clase
            if name.startswith('__') or name.startswith('_') or name in cls.get_ignored_attributes():
                continue
            
            value = getattr(cls, name, None)
            mappedtype = mapped_type(hint)
            user_defined_sqlalchemy_type = get_type_if_is_sqlalchemy_type(hint)
            options = enum_options(hint)

            # Procesar como columna
            if isinstance(value, Column):
                # Ya es una Column (definida con column())
                column = value
                column.name = name
                column.type = mappedtype
                column.user_defined_sqlalchemy_type = user_defined_sqlalchemy_type
                column.options = options
                column.model = cls
                column.nullable = is_optional(hint)
                column.save()
            
            elif value is None and is_column_type(hint):
                # Columna implícita
                column = Column(
                    name=name,
                    type=mappedtype,
                    user_defined_sqlalchemy_type=user_defined_sqlalchemy_type,
                    model=cls,
                    options=options,
                    nullable=is_optional(hint)
                )
                column.save()
                
            
            elif value is not None and is_column_type(hint) and not cls.__is_view__:
                # Columna con valor por defecto
                if mappedtype != mapped_type(type(value)):
                    raise TypeError(
                        f"El tipo del valor por defecto [{value}] no coincide "
                        f"con el tipo esperado '{mappedtype}' para '{name}' en '{cls.__name__}'"
                    )
                
                column = Column(
                    name=name,
                    type=mappedtype,
                    user_defined_sqlalchemy_type=user_defined_sqlalchemy_type,
                    model=cls,
                    options=options,
                    nullable=is_optional(hint)
                )
                column.args.default = value
                column.save()

    @classmethod
    @abstractmethod
    def get_ignored_attributes(cls) -> set:
        """Retorna los atributos que deben ser ignorados durante el análisis"""
        pass

    @classmethod
    @abstractmethod
    def reset(cls) -> None:
        """Reinicia el estado de la clase para permitir reanálisis"""
        pass
    
    @classmethod
    def info(cls) -> Dict[str, Any]:
        """Información básica común"""
        return {
            'name': cls.__name__,
            'object_name': cls._name,
            'columns': [col.info() for col in cls.columns.values()],
            'description': cls._description,
        }
    
    @classmethod
    @abstractmethod
    def validate(cls) -> None:
        """Validación específica del tipo de objeto"""
        pass
    
    @classmethod
    @abstractmethod
    def to_sqlalchemy_object(cls, metadata: MetaData):
        """Conversión a objeto SQLAlchemy"""
        pass

    @classmethod
    def get_registered_tables(cls) -> List[Table]:
        """Retorna solo las tablas registradas"""
        from .table import Table  # Import local para evitar circular imports
        return [obj for obj in cls.registry if isinstance(obj, type) and issubclass(obj, Table)]
    
    @classmethod
    def get_registered_views(cls) -> List[View]:
        """Retorna solo las vistas registradas"""
        from .view import View  # Import local para evitar circular imports
        return [obj for obj in cls.registry if isinstance(obj, type) and issubclass(obj, View)]
    