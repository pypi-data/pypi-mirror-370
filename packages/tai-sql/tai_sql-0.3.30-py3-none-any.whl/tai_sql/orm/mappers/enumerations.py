from __future__ import annotations
from typing import Any, Dict, ClassVar, List, Type
from enum import Enum as BaseEnum, EnumMeta
from tai_sql import pm
import re


class EnumRegistryMeta(EnumMeta):
    """
    Metaclass que registra automáticamente los Enums cuando se crean.
    """
    
    # Registro global de todos los Enums definidos
    registry: ClassVar[List[Type[BaseEnum]]] = []
    
    def __new__(metacls, name, bases, namespace, **kwargs):
        # Crear la clase Enum normalmente
        enum_class = super().__new__(metacls, name, bases, namespace, **kwargs)
        
        # Solo registrar si es una subclase de Enum y no es la clase base
        if (issubclass(enum_class, BaseEnum) and 
            enum_class is not BaseEnum and 
            name != 'Enum'):  # Evitar registrar nuestra clase base
            
            EnumRegistryMeta.registry.append(enum_class)
        
        return enum_class


class Enum(BaseEnum, metaclass=EnumRegistryMeta):
    """
    Clase base para definir enumeraciones que serán utilizadas en columnas de base de datos.
    Los Enums se registran automáticamente al definirlos.
    """
    
    @classmethod
    def get_registered_enums(cls) -> List[Type[BaseEnum]]:
        """
        Obtiene todos los Enums registrados.
        
        Returns:
            List[Type[BaseEnum]]: Lista de clases Enum registradas
        """
        return EnumRegistryMeta.registry.copy()
    
    @classmethod
    def clear_registry(cls) -> None:
        """
        Limpia el registro de Enums (útil para testing).
        """
        EnumRegistryMeta.registry.clear()
    
    @classmethod
    def info(cls) -> Dict[str, Any]:
        """
        Obtiene información sobre el Enum.
        
        Returns:
            Dict[str, Any]: Información del Enum
        """
        return {
            'name': cls._to_snake_case(cls.__name__),
            'hypen_name': cls._to_snake_case(cls.__name__).replace('_', '-'),
            'values': [item.value for item in cls],
            'type': cls.get_type(),
        }
    
    @classmethod
    def get_type(cls) -> type:
        """
        Obtiene el tipo de columna para este Enum.
        
        Returns:
            Type[pm.Enum]: Tipo de columna para el Enum
        """
        types = list(set(type(item.value) for item in cls))
        
        if len(types) > 1:
            raise TypeError(
                f"El modelo '{cls.__name__}' tiene múltiples tipos de valores: {types}. "
                "Debe tener un tipo único."
            )
        
        return types[0].__name__
    
    @classmethod
    def _to_snake_case(cls, name: str) -> str:
        """
        Convierte un string de CapitalCase a snake_case.
        
        Args:
            name (str): String en CapitalCase
            
        Returns:
            str: String convertido a snake_case
        """
        # Insertar guión bajo antes de mayúsculas que siguen a minúsculas o números
        s1 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
        # Insertar guión bajo antes de mayúsculas que siguen a otras mayúsculas seguidas de minúsculas
        s2 = re.sub('([A-Z])([A-Z][a-z])', r'\1_\2', s1)
        return s2.lower()