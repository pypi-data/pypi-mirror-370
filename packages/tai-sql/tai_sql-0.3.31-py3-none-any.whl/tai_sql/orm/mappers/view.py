from __future__ import annotations
from typing import Any, Dict, ClassVar, List
from sqlalchemy import MetaData
from sqlalchemy.sql import text

from .base import DatabaseObject

class View(DatabaseObject):
    """
    Clase para definir vistas de base de datos.
    
    Las vistas son consultas SQL almacenadas que se comportan como tablas
    de solo lectura. No tienen foreign keys propias, pero sus columnas
    pueden referenciar datos de múltiples tablas.
    """
    
    __abstract__ = True
    __is_view__ = True  # Indica que es una vista
    __tablename__: ClassVar[str]
    __query__: ClassVar[str] = None  # Consulta SQL que define la vista
    __analized__: ClassVar[bool] = False  # Indica si ya se ha analizado
    
    # Específico de vistas
    dependencies: ClassVar[List[DatabaseObject]] = []  # Tablas/vistas de las que depende
    materialized: ClassVar[bool] = False    # Si es una vista materializada
    
    def __init_subclass__(cls) -> None:
        """Inicialización específica para vistas"""
        super().__init_subclass__()
        
        # Validar atributos requeridos
        if not hasattr(cls, '__tablename__'):
            raise ValueError(f"La vista {cls.__name__} debe definir __viewname__")
        
        # if not hasattr(cls, '__query__'):
        #     raise ValueError(f"La vista {cls.__name__} debe definir __query__")
        
        cls.tablename = cls.__tablename__
        cls._name = cls.__name__  # Para compatibilidad con base
        cls.query = cls.__query__
        cls.is_view = cls.__is_view__  # Marca para identificar que es una vista
        
        # Inicializar atributos específicos
        cls.dependencies = getattr(cls, 'dependencies', [])
        cls.materialized = getattr(cls, 'materialized', False)

    @classmethod
    def get_models(cls) -> List[View]:
        """Retorna solo las tablas registradas"""
        cls.reset()
        cls.analyze()
        return cls.get_registered_views()
    
    @classmethod
    def get_ignored_attributes(cls) -> set:
        """Atributos específicos de vista a ignorar"""
        return {'registry', 'columns', 'tablename', 'query', 'dependencies', 'materialized', '_name', 'is_view'}
    
    @classmethod
    def reset(cls) -> None:
        """Reinicia el estado de la clase para permitir reanálisis"""
        cls.columns.clear()
        cls.__analized__ = False
    
    @classmethod
    def analyze(cls) -> None:
        """Análisis para vistas (solo columnas, no relaciones)"""
        if cls.__analized__:
            return
        
        for model in cls.registry:
            if issubclass(model, View):
                model.analyze_columns()
        
        cls.validate()
        
        cls.__analized__ = True  # Marcar como analizado
    
    @classmethod
    def validate(cls) -> None:
        """Validación específica para vistas"""
        for model in cls.registry:
            if not issubclass(model, View):
                continue
            
            # Validar que tenga al menos una columna
            if not model.columns:
                raise ValueError(f"La vista {model.__name__} debe tener al menos una columna definida")
            
    
    @classmethod
    def info(cls) -> Dict[str, Any]:
        """Información específica de vista"""
        base_info = super().info()
        base_info.update({
            'tablename': cls.tablename,
            'query': cls.query,
            'dependencies': cls.dependencies,
            'materialized': cls.materialized,
            'is_materialized': cls.materialized,
            'is_view': cls.is_view,
            'relations': [],  # Las vistas no tienen relaciones propias. Para compatibilidad, se deja vacío
            'has_relations': False  # Las vistas no tienen relaciones propias
        })
        return base_info
    
    @classmethod
    def to_sqlalchemy_object(cls, metadata: MetaData):
        """Conversión a vista SQLAlchemy"""
        return cls.to_sqlalchemy_view(metadata)
    
    @classmethod
    def to_sqlalchemy_view(cls, metadata: MetaData):
        """
        Convierte la definición a una vista SQLAlchemy
        
        Returns:
            CreateView: Comando DDL para crear la vista
        """       
        
        # Crear comando DDL para la vista
        view_type = "MATERIALIZED VIEW" if cls.materialized else "VIEW"
        
        create_view_sql = f"""
        CREATE {view_type} {cls._name} AS
        {cls.query}
        """
        
        return text(create_view_sql)
    
    @classmethod
    def get_drop_statement(cls) -> str:
        """Genera sentencia DROP para la vista"""
        view_type = "MATERIALIZED VIEW" if cls.materialized else "VIEW"
        return f"DROP {view_type} IF EXISTS {cls._name}"