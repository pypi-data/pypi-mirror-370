from typing import get_origin, get_args, Union, Optional, List
from datetime import datetime, date, time
from enum import Enum
from sqlalchemy import (
    Integer, String, Text, Boolean, DateTime, 
    Date, Time, Float, Numeric, LargeBinary,
    BigInteger, Enum as SQLAlchemyEnum
)

# Tipos básicos nativos
NATIVE_TYPES = {
    str, int, float, bool, bytes, list, dict, set, tuple,
    type(None), complex, frozenset, bytearray, memoryview
}

# Tipos temporales
TIME_TYPES = {datetime, date, time}

# Tipos básicos de SQLAlchemy
SQLALCHEMY_TYPES = {
    Integer, String, Text, Boolean, DateTime, 
    Date, Time, Float, Numeric, LargeBinary,
    BigInteger, SQLAlchemyEnum
}

# Mapeo sqlalchemy > native
SQLALCHEMY_TYPE_MAPPER = {
    Integer: int,
    BigInteger: int,
    String: str,
    Text: str,
    Boolean: bool,
    DateTime: datetime,
    Date: date,
    Time: time,
    Float: float,
    Numeric: float,
    LargeBinary: bytes,
    SQLAlchemyEnum: Enum
}

def is_native_python_type(type_hint) -> bool:
    """
    Verifica si un tipo es nativo de Python, incluyendo tipos genéricos.
    
    Args:
        type_hint: El tipo a verificar
        
    Returns:
        bool: True si es un tipo nativo, False en caso contrario
    """
    
    # Manejar tipos envueltos (Optional, List, list)
    origin = get_origin(type_hint)
    
    # Si es Optional[T] (Union[T, None])
    if origin is Union:
        args = get_args(type_hint)
        # Optional[T] se representa como Union[T, None]
        if len(args) == 2 and type(None) in args:
            # Extraer el tipo que no es None
            inner_type = args[0] if args[1] is type(None) else args[1]
            return is_native_python_type(inner_type)  # Recursión para procesar el tipo interno
    
    # Si es List[T] o list[T]
    if origin in (list, List):
        args = get_args(type_hint)
        if args:
            # Extraer el primer tipo genérico
            inner_type = args[0]
            return is_native_python_type(inner_type)  # Recursión para procesar el tipo interno
    
    # Si ya es un tipo nativo o de tiempo, lo devolvemos tal cual
    if type_hint in NATIVE_TYPES or type_hint in TIME_TYPES:
        return True
    
    return False

def is_enum_type(type_hint) -> bool:
    """
    Verifica si un tipo es un Enum.
    
    Args:
        type_hint: El tipo a verificar
        
    Returns:
        bool: True si es un Enum, False en caso contrario
    """
    # Manejar tipos envueltos (Optional, List, list)
    origin = get_origin(type_hint)
    
    # Si es Optional[T] (Union[T, None])
    if origin is Union:
        args = get_args(type_hint)
        # Optional[T] se representa como Union[T, None]
        if len(args) == 2 and type(None) in args:
            # Extraer el tipo que no es None
            inner_type = args[0] if args[1] is type(None) else args[1]
            return is_enum_type(inner_type)  # Recursión para procesar el tipo interno
    
    # Si es List[T] o list[T]
    if origin in (list, List):
        args = get_args(type_hint)
        if args:
            # Extraer el primer tipo genérico
            inner_type = args[0]
            return is_enum_type(inner_type)  # Recursión para procesar el tipo interno
    
    # Verificar si es una clase Enum
    if isinstance(type_hint, type) and issubclass(type_hint, Enum):
        return True
    
    return False

def is_sqlalchemy_type(type_hint) -> bool:
    """
    Verifica si un tipo es un tipo de SQLAlchemy.
    
    Args:
        type_hint: El tipo a verificar
        
    Returns:
        bool: True si es un tipo de SQLAlchemy, False en caso contrario
    """
        # Manejar tipos envueltos (Optional, List, list)
    origin = get_origin(type_hint)
    
    # Si es Optional[T] (Union[T, None])
    if origin is Union:
        args = get_args(type_hint)
        # Optional[T] se representa como Union[T, None]
        if len(args) == 2 and type(None) in args:
            # Extraer el tipo que no es None
            inner_type = args[0] if args[1] is type(None) else args[1]
            return is_sqlalchemy_type(inner_type)  # Recursión para procesar el tipo interno
    
    # Si es List[T] o list[T]
    if origin in (list, List):
        args = get_args(type_hint)
        if args:
            # Extraer el primer tipo genérico
            inner_type = args[0]
            return is_sqlalchemy_type(inner_type)  # Recursión para procesar el tipo interno

    return type_hint in SQLALCHEMY_TYPES

def is_column_type(type_hint) -> bool:
    """
    Verifica si un type_hint es un tipo de columna válido.
    
    Esta función comprueba si el type_hint es un tipo nativo, un tipo de SQLAlchemy,
    o un tipo customizado registrado como columna.
    
    Args:
        type_hint: El tipo a verificar
        
    Returns:
        bool: True si es un tipo de columna, False en caso contrario
    """
    
    # Verificar tipos nativos y de tiempo
    if is_native_python_type(type_hint) or is_sqlalchemy_type(type_hint) or is_enum_type(type_hint):
        return True
    
    return False


def find_custom_type(type_hint) -> Optional[type]:
    """
    Encuentra el tipo customizado (no nativo) en un type hint.
    
    Esta función busca recursivamente en el type hint para encontrar
    el primer tipo que no sea nativo de Python. Útil para identificar
    clases Table en relaciones.
    
    Args:
        type_hint: El tipo a analizar (puede ser simple, Union, List, etc.)
        
    Returns:
        Optional[type]: El tipo customizado encontrado, o None si no hay ninguno
        
    Examples:
        find_custom_type(str) -> None (es nativo)
        find_custom_type(User) -> User (si User hereda de Table)
        find_custom_type(List[User]) -> User
        find_custom_type(Optional[Post]) -> Post
        find_custom_type(Union[str, User]) -> User
    """
    
    # Si es None, retornar None
    if type_hint is None or type_hint is type(None):
        return None
    
    # Si es un tipo nativo, retornar None
    if is_native_python_type(type_hint):
        return None
    
    # Si es un tipo simple y no es nativo, es nuestro tipo customizado
    if isinstance(type_hint, type):
        return type_hint
    
    # Manejar tipos genéricos
    origin = get_origin(type_hint)
    if origin is not None:
        args = get_args(type_hint)
        
        # Para List[CustomType], Dict[str, CustomType], etc.
        if origin in (list, dict, set, tuple):
            for arg in args:
                custom_type = find_custom_type(arg)
                if custom_type is not None:
                    return custom_type
        
        # Para Union (incluyendo Optional)
        elif origin is Union:
            for arg in args:
                # Saltar type(None) en Optional[CustomType]
                if arg is type(None):
                    continue
                custom_type = find_custom_type(arg)
                if custom_type is not None:
                    return custom_type
    
    # Si llegamos aquí y es una string (forward reference), intentar resolverla
    if isinstance(type_hint, str):
        # Buscar en el registro de Table para ver si coincide con algún modelo
        from . import Table
        for model in Table.registry:
            if model.__name__ == type_hint:
                return model
    
    return None

def is_optional(type_hint) -> bool:
    """
    Verifica si un tipo es Optional (Union[X, None]).
    
    Args:
        type_hint: El tipo a verificar
        
    Returns:
        bool: True si es Optional, False en caso contrario
    """
    
    # Manejar Optional[X] que es Union[X, None]
    origin = get_origin(type_hint)
    if origin is Union:
        args = get_args(type_hint)
        return len(args) == 2 and type(None) in args
    
    return False

def from_enum_to_native(type_hint):
    """
    Convierte un Enum a su tipo nativo.
    
    Esta función toma un Enum y devuelve el tipo nativo de sus valores.
    Si el Enum tiene múltiples tipos de valores, lanza un TypeError.
    
    Args:
        type_hint: El Enum a convertir
        
    Returns:
        type: El tipo nativo de los valores del Enum
        
    Raises:
        TypeError: Si el Enum tiene múltiples tipos de valores
    """
    
    types = list(set(type(item.value) for item in type_hint))
    
    if len(types) > 1:
        raise TypeError(
            f"El modelo '{type_hint.__name__}' tiene múltiples tipos de valores: {types}. "
            "Debe tener un tipo único."
        )
    
    if types[0] not in NATIVE_TYPES and types[0] not in TIME_TYPES:
            raise TypeError(
                f"El tipo de Enum '{type_hint.__name__}' debe ser un tipo nativo de python o de tiempo."
            )
    
    return types[0].__name__


def enum_options(type_hint):
    """
    Obtiene las opciones de un Enum como una lista de tuplas (valor, nombre).
    
    Esta función toma un Enum y devuelve una lista de tuplas donde cada tupla
    contiene el valor del Enum y su nombre.
    
    Args:
        type_hint: El Enum del cual obtener las opciones
        
    Returns:
        List[Tuple[Any, str]]: Lista de tuplas con valor y nombre del Enum
    """
    
    if not is_enum_type(type_hint):
        return None
    
    # Manejar tipos envueltos (Optional, List, list)
    origin = get_origin(type_hint)
    # Si es Optional[T] (Union[T, None])
    if origin is Union:
        args = get_args(type_hint)
        # Optional[T] se representa como Union[T, None]
        if len(args) == 2 and type(None) in args:
            # Extraer el tipo que no es None
            inner_type = args[0] if args[1] is type(None) else args[1]
            return is_enum_type(inner_type)  # Recursión para procesar el tipo interno
    
    # Si es List[T] o list[T]
    if origin in (list, List):
        args = get_args(type_hint)
        if args:
            # Extraer el primer tipo genérico
            inner_type = args[0]
            return is_enum_type(inner_type)  # Recursión para procesar el tipo interno
    
    # Verificar si es una clase Enum
    if isinstance(type_hint, type) and issubclass(type_hint, Enum):
        return [item.value for item in type_hint]

def mapped_type(type_hint):
    """
    Devuelve un tipo nativo o de tiempo a partir de un type_hint,
    usando el mapeador SQLALCHEMY_TYPE_MAPPER si es necesario.
    Maneja tipos envueltos en Optional, List o list.
    """
    
    # Manejar tipos envueltos (Optional, List, list)
    origin = get_origin(type_hint)
    
    # Si es Optional[T] (Union[T, None])
    if origin is Union:
        args = get_args(type_hint)
        # Optional[T] se representa como Union[T, None]
        if len(args) == 2 and type(None) in args:
            # Extraer el tipo que no es None
            inner_type = args[0] if args[1] is type(None) else args[1]
            return mapped_type(inner_type)  # Recursión para procesar el tipo interno
    
    # Si es List[T] o list[T]
    if origin in (list, List):
        args = get_args(type_hint)
        if args:
            # Extraer el primer tipo genérico
            inner_type = args[0]
            return mapped_type(inner_type)  # Recursión para procesar el tipo interno
    
    # Si ya es un tipo nativo o de tiempo, lo devolvemos tal cual
    if type_hint in NATIVE_TYPES or type_hint in TIME_TYPES:
        return type_hint.__name__
    
    # Si es un Enum, retornamos el tipo Enum
    if is_enum_type(type_hint):
        return from_enum_to_native(type_hint)  # Retornamos la clase Enum completa

    # Si es un tipo de SQLAlchemy, lo mapeamos a nativo
    if type_hint in SQLALCHEMY_TYPES:
        mapped = SQLALCHEMY_TYPE_MAPPER.get(type_hint)
        if mapped and (mapped in NATIVE_TYPES or mapped in TIME_TYPES):
            return mapped.__name__

    # Si es un string, intentamos buscarlo en los tipos soportados
    if isinstance(type_hint, str):

        # Buscar en NATIVE_TYPES y TIME_TYPES por nombre
        for t in list(NATIVE_TYPES) + list(TIME_TYPES):
            if t.__name__ == type_hint:
                return t.__name__
            
        # Buscar en SQLALCHEMY_TYPES por nombre y mapear
        for sa_type in SQLALCHEMY_TYPES:
            if getattr(sa_type, "__name__", None) == type_hint:
                mapped = SQLALCHEMY_TYPE_MAPPER.get(sa_type)
                if mapped and (mapped in NATIVE_TYPES or mapped in TIME_TYPES):
                    return mapped.__name__

    # Si llegamos aquí, es un tipo customizado que no está en los tipos nativos/tiempo
    # Miramos si es un tipo customizado registrado
    custom_type = find_custom_type(type_hint)
    if custom_type is not None:
        return custom_type

    raise TypeError(
        f"Tipo '{type_hint}' no reconocido en el sistema"
    )

def get_type_if_is_sqlalchemy_type(type_hint):
    """
    Devuelve el tipo de SQLAlchemy correspondiente a un type_hint.
    
    Esta función mapea tipos nativos y de tiempo a sus equivalentes de SQLAlchemy.
    Si el tipo es un tipo customizado, se devuelve directamente.
    
    Args:
        type_hint: El tipo a mapear
        
    Returns:
        type: El tipo de SQLAlchemy correspondiente
        
    Raises:
        TypeError: Si el tipo no es reconocido
    """
        # Manejar tipos envueltos (Optional, List, list)
    origin = get_origin(type_hint)
    
    # Si es Optional[T] (Union[T, None])
    if origin is Union:
        args = get_args(type_hint)
        # Optional[T] se representa como Union[T, None]
        if len(args) == 2 and type(None) in args:
            # Extraer el tipo que no es None
            inner_type = args[0] if args[1] is type(None) else args[1]
            return get_type_if_is_sqlalchemy_type(inner_type)  # Recursión para procesar el tipo interno
    
    # Si es List[T] o list[T]
    if origin in (list, List):
        args = get_args(type_hint)
        if args:
            # Extraer el primer tipo genérico
            inner_type = args[0]
            return get_type_if_is_sqlalchemy_type(inner_type)  # Recursión para procesar el tipo interno
    
    if is_enum_type(type_hint):
        return None
    
    if is_sqlalchemy_type(type_hint):
        return type_hint.__name__
    
    return None

    
def get_relation_direction(type_hint) -> Optional[str]:
    """
    Determina la dirección de una relación basándose en el type hint.
    
    Esta función analiza el type hint para determinar si la relación es:
    - 'one-to-many': cuando el tipo es List[CustomType] o list[CustomType]
    - 'many-to-one': cuando el tipo es CustomType directamente
    
    Args:
        type_hint: El tipo a analizar
        
    Returns:
        Optional[str]: 'one-to-many', 'many-to-one', o None si no es una relación
        
    Examples:
        get_relation_direction(User) -> 'many-to-one'
        get_relation_direction(List[Post]) -> 'one-to-many'
        get_relation_direction(list[Comment]) -> 'one-to-many'
        get_relation_direction(Optional[User]) -> 'many-to-one'
        get_relation_direction(str) -> None (no es una relación)
    """
    from typing import get_origin, get_args, Union
    
    # Si no hay tipo customizado, no es una relación
    custom_type = find_custom_type(type_hint)
    if custom_type is None:
        return None
    
    # Obtener el origen del tipo
    origin = get_origin(type_hint)
    
    # Si es una lista (List[CustomType] o list[CustomType])
    if origin is list or origin is List:
        return 'one-to-many'
    
    # Si es Union (como Optional[CustomType])
    if origin is Union:
        args = get_args(type_hint)
        # Para Optional[CustomType] = Union[CustomType, None]
        if len(args) == 2 and type(None) in args:
            # Obtener el tipo que no es None
            non_none_type = args[0] if args[1] is type(None) else args[1]
            # Verificar recursivamente el tipo no-None
            return get_relation_direction(non_none_type)
    
    # Si es un tipo customizado directo (CustomType)
    if isinstance(type_hint, type) and custom_type is not None:
        return 'many-to-one'
    
    # Si es una forward reference (string) que apunta a un tipo customizado
    if isinstance(type_hint, str) and custom_type is not None:
        return 'many-to-one'
    
    return None