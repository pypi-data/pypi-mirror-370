"""
Gestor de base de datos con funcionalidad de carga de schema integrada.
"""
from __future__ import annotations
import sys
import importlib.util
from pathlib import Path
from typing import Optional, List, TYPE_CHECKING
from dataclasses import dataclass
import click
from sqlalchemy import Engine

from .drivers import drivers, DatabaseDriver

if TYPE_CHECKING:
    from generators import BaseGenerator
    from core import Provider
    from .orm import Table, View, Enum

@dataclass
class EngineParams:
    """Parámetros para la creación del motor SQLAlchemy"""
    sqlalchemy_logs: bool = False
    pool_pre_ping: bool = True
    pool_recycle: int = 3600
    pool_size: int = 5
    max_overflow: int = 5
    pool_timeout: int = 30

    def to_dict(self) -> dict:
        return {
            'sqlalchemy_logs': self.sqlalchemy_logs,
            'pool_pre_ping': self.pool_pre_ping,
            'pool_recycle': self.pool_recycle,
            'pool_size': self.pool_size,
            'max_overflow': self.max_overflow,
            'pool_timeout': self.pool_timeout
        }

class SchemaManager:
    """
    Gestor de base de datos con funcionalidad de carga de schema integrada.
    Cada instancia maneja un schema específico.
    """
    
    def __init__(self, schema_name: str, schema_path: Optional[Path] = None):
        """
        Inicializa el gestor de base de datos para un schema específico
        
        Args:
            schema_name: Nombre identificador del schema
            schema_path: Ruta al archivo de schema (opcional, se resuelve automáticamente)
        """
        self.schema_name = schema_name
        self.schema_path = schema_path
        self._provider = None
        self.secret_key_name = 'SECRET_KEY'
        self.engine_params = EngineParams()
        self._generators = []
        self._driver = None
        self._engine = None
        self._adminengine = None  # Motor para operaciones administrativas
        self._tables = None
        self._views = None
        self._enums = None
        self._loaded = False
        self._validated = False
    
    @property
    def provider(self) -> Optional[Provider]:
        """Proveedor de la base de datos"""
        return self._provider
    
    @provider.setter
    def provider(self, value: Provider):
        """Establece el proveedor de la base de datos"""
        self._provider = value
        # Invalidar driver + engine si cambia el provider
        self._driver = None
        self._engine = None
    
    @property
    def driver(self) -> Optional[DatabaseDriver]:
        """Driver de la base de datos"""
        if not self._driver and self.provider:
            # Obtener el driver del proveedor
            self._driver = drivers.get_or_raise(self.provider.drivername)
        
        return self._driver
    
    @property
    def engine(self) -> Engine:
        """Obtiene o crea el motor SQLAlchemy"""
        if not self._engine and self.driver:
            self._engine = self._driver.get_engine(
                username=self.provider.username,
                password=self.provider.password,
                host=self.provider.host,
                port=self.provider.port,
                database=self.provider.database,
                timeout=self.engine_params.pool_timeout
            )
        return self._engine
    
    @property
    def adminengine(self) -> Engine:
        """Obtiene o crea el motor SQLAlchemy"""
        if not self._adminengine and self._driver:
            self._adminengine = self._driver.get_engine(
                username=self.provider.username,
                password=self.provider.password,
                host=self.provider.host,
                port=self.provider.port,
                timeout=self.engine_params.pool_timeout
            )
        return self._adminengine
    
    @property
    def generators(self) -> List[BaseGenerator]:
        """Lista de generadores configurados"""
        return self._generators
    
    @generators.setter
    def generators(self, value: List[BaseGenerator]):
        """Establece la lista de generadores"""
        self._generators = value
    
    @property
    def tables(self) -> List[Table]:
        """Lista de tablas definidas por el usuario"""
        if not self._tables:
            from .orm import Table
            self._tables = Table.get_models()
        return self._tables
    
    @property
    def views(self) -> List[View]:
        """Lista de vistas definidas por el usuario"""
        if not self._views:
            from .orm import View
            self._views = View.get_models()
        return self._views
    
    @property
    def enums(self) -> List[Enum]:
        """Lista de enumeraciones definidas por el usuario"""
        if not self._enums:
            from .orm import Enum
            self._enums = Enum.get_registered_enums()
        return self._enums
    
    @property
    def is_loaded(self) -> bool:
        """Indica si el schema ha sido cargado"""
        return self._loaded
    
    def load(self) -> None:
        """
        Carga el módulo del schema. Integra funcionalidad de SchemaFile.
        """
        if self._loaded:
            return
        
        if not self.schema_path:
            raise ValueError(f"No se ha especificado schema_path para {self.schema_name}")
        
        if not self.schema_path.exists():
            raise FileNotFoundError(f"El archivo de schema {self.schema_path} no existe")
        
        try:
            from .orm.mappers.base import DatabaseObject
            DatabaseObject.registry.clear()  # Limpiar registro previo
            
            # Crear nombre de módulo único para evitar conflictos
            module_name = f"tai_sql_schema_{self.schema_name}"
            
            # Limpiar módulo previo si existe
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            spec = importlib.util.spec_from_file_location(module_name, self.schema_path)
            if spec is None:
                raise ImportError(f"No se pudo cargar el archivo de esquema: {self.schema_path}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            self._loaded = True
            
        except Exception as e:
            raise RuntimeError(f"Error al cargar el schema '{self.schema_name}': {e}")
    
    def validations(self) -> None:
        """
        Ejecuta validaciones del schema cargado. Integra funcionalidad de SchemaFile.
        """
        if self._validated:
            return
        
        if not self._loaded:
            raise RuntimeError(f"El schema '{self.schema_name}' no ha sido cargado")
        
        if not self.provider:
            click.echo(f"❌ No se ha configurado un proveedor de datos en {self.schema_path}", err=True)
            click.echo(f"   Schema: {self.schema_name}", err=True)
            click.echo(f"   Asegúrate de llamar a datasource()", err=True)
            sys.exit(1)
            
        if not self.engine:
            click.echo(f"❌ No se pudo crear el engine de base de datos", err=True)
            click.echo(f"   Schema: {self.schema_name}", err=True)
            click.echo(f"   Verifica la configuración de tu proveedor", err=True)
            sys.exit(1)

        if not self.provider.database:
            click.echo(f"❌ No se pudo encontrar el nombre de la base de datos", err=True)
            click.echo(f"   Schema: {self.schema_name}", err=True)
            click.echo(f"   Verifica la configuración de tu proveedor", err=True)
            sys.exit(1)

        if not self.generators:
            click.echo(f"⚠️ Advertencia: No se han configurado generadores para '{self.schema_name}'. No se generará ningún recurso.", err=True)
        
        if self.provider.source_input_type in ('connection_string', 'params'):
            click.echo(
                f'⚠️  ADVERTENCIA DE SEGURIDAD para schema "{self.schema_name}":\n'
                f'    El método "{self.provider.source_input_type}" expone credenciales en el código fuente.\n'
                f'    Se recomienda usar env() en su lugar.',
                err=True
            )
        
        self._validated = True
    
    def reset(self) -> None:
        """Resetea el estado del DatabaseManager"""
        self._provider = None
        self._engine = None
        self._generators = []
        self._tables = []
        self._views = []
        self._loaded = False
    
    def get_info(self) -> dict:
        """Obtiene información completa del DatabaseManager"""
        return {
            'schema_name': self.schema_name,
            'schema_path': str(self.schema_path) if self.schema_path else None,
            'is_loaded': self.is_loaded,
            'has_provider': self.provider is not None,
            'has_engine': self._engine is not None,
            'generators_count': len(self.generators),
            'tables_count': len(self.tables),
            'views_count': len(self.views),
            'database_name': self.provider.database if self.provider else None
        }