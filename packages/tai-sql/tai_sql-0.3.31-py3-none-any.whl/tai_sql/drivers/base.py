"""
Sistema de drivers de base de datos para TAI-SQL
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from sqlalchemy import URL, create_engine, Engine, Column, ForeignKeyConstraint

class DatabaseDriver(ABC):
    """Clase base abstracta para drivers de base de datos"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre del driver"""
        pass
    
    @property
    @abstractmethod
    def default_port(self) -> int:
        """Puerto por defecto del motor"""
        pass
    
    @property
    @abstractmethod
    def default_database(self) -> str:
        """Base de datos por defecto para conexiones administrativas"""
        pass
    
    @abstractmethod
    def create_temp_url(self, username: str, password: str, host: str, 
                       port: int, database: str = None) -> URL:
        """Crea URL temporal para conexiones sin BD específica"""
        pass
    
    @abstractmethod
    def get_connect_args(self, timeout: int) -> Dict[str, Any]:
        """Argumentos específicos de conexión para este driver"""
        pass
    
    @abstractmethod
    def database_exists_query(self) -> str:
        """Query para verificar si una base de datos existe"""
        pass
    
    @abstractmethod
    def schema_exists_query(self) -> str:
        """Query para verificar si un schema existe"""
        pass
    
    @abstractmethod
    def create_database_statement(self, database_name: str) -> str:
        """Sentencia para crear una base de datos"""
        pass
    
    @abstractmethod
    def create_schema_statement(self, schema_name: str) -> str:
        """Sentencia para crear un schema"""
        pass
    
    @abstractmethod
    def get_ddl_prefix(self, schema_name: str) -> str:
        """Prefijo para sentencias DDL (schema.tabla)"""
        pass
    
    @abstractmethod
    def supports_schemas(self) -> bool:
        """Indica si el motor soporta schemas"""
        pass

    @property
    @abstractmethod
    def type_mapping(self) -> Dict[str, List[str]]:
        """Retorna un diccionario de mapeo de tipos SQLAlchemy a tipos del motor"""
        pass

    @abstractmethod
    def get_views_statement(self, schema_name: str = None) -> List[str]:
        """Obtiene una lista de vistas en el esquema especificado"""
        pass

    @abstractmethod
    def normalize_query(self, query: str) -> str:
        """Normaliza una consulta SQL para el motor específico"""
        pass

    @abstractmethod
    def get_column_definition(self, column: Column) -> str:
        """
        Genera la definición de columna para CREATE TABLE o ALTER TABLE
        
        Args:
            column: Columna SQLAlchemy
            
        Returns:
            str: Definición de la columna (ej: "name VARCHAR(100) NOT NULL DEFAULT 'John'")
        """
        pass
    
    @abstractmethod
    def alter_column_statements(self, table_name: str, column: Column) -> list[str]:
        """
        Genera sentencias ALTER COLUMN específicas para cada motor de BD
        
        Args:
            table_name: Nombre de la tabla
            column: Columna SQLAlchemy a modificar
            
        Returns:
            Lista de sentencias ALTER COLUMN
        """
        pass
    
    @abstractmethod
    def get_default_value(self, default) -> str:
        """
        Procesa el valor DEFAULT de una columna
        
        Args:
            default: Objeto default de SQLAlchemy
            
        Returns:
            str: Valor DEFAULT formateado para SQL
        """
        pass
    
    @abstractmethod
    def reserved_word_mapper(self, identifier: str) -> str:
        """
        Escapa identificadores que pueden ser palabras reservadas
        
        Args:
            identifier: Nombre de tabla o columna
            
        Returns:
            str: Identificador escapado si es necesario
        """
        pass
    
    @abstractmethod
    def create_table_statement(self, table) -> str:
        """
        Genera una sentencia CREATE TABLE personalizada
        
        Args:
            table: Tabla SQLAlchemy
            
        Returns:
            str: Sentencia CREATE TABLE completa
        """
        pass

    @abstractmethod
    def drop_table_statement(self, table_name: str, schema_name: str = None) -> str:
        """
        Genera una sentencia DROP TABLE
        
        Args:
            table_name: Nombre de la tabla a eliminar
            schema_name: Nombre del schema (opcional)
            
        Returns:
            str: Sentencia DROP TABLE completa
        """
        pass
    
    @abstractmethod
    def foreign_key_statement(self, table, fk: ForeignKeyConstraint) -> str:
        """
        Genera una sentencia ALTER TABLE ADD CONSTRAINT para Foreign Key
        
        Args:
            table: Tabla SQLAlchemy
            fk: ForeignKeyConstraint de SQLAlchemy
            
        Returns:
            str: Sentencia ALTER TABLE ADD CONSTRAINT
        """
        pass
    
    @abstractmethod
    def supports_materialized_views(self) -> bool:
        """
        Indica si el motor soporta vistas materializadas
        
        Returns:
            bool: True si soporta vistas materializadas
        """
        pass
    
    @abstractmethod
    def create_view_statement(self, view) -> str:
        """
        Genera una sentencia CREATE VIEW
        
        Args:
            view: Vista tai-sql
            
        Returns:
            str: Sentencia CREATE VIEW completa
        """
        pass

    @abstractmethod
    def drop_view_statement(self, view_name: str, schema_name: str = None, view_definition: str = None) -> str:
        """Genera la sentencia para eliminar una vista"""
        pass
    
    @abstractmethod
    def alter_view_statement(self, view) -> str:
        """
        Genera una sentencia CREATE OR REPLACE VIEW
        
        Args:
            view: Vista tai-sql
            
        Returns:
            str: Sentencia CREATE OR REPLACE VIEW
        """
        pass
    
    @abstractmethod
    def recreate_materialized_view_statement(self, view) -> list[str]:
        """
        Genera sentencias para recrear una vista materializada
        
        Args:
            view: Vista materializada tai-sql
            
        Returns:
            list[str]: Lista de sentencias [DROP, CREATE]
        """
        pass

    @property
    @abstractmethod
    def reserved_words(self) -> set[str]:
        """
        Lista de palabras reservadas del motor
        
        Returns:
            set: Conjunto de palabras reservadas
        """
        pass

    def get_engine(self, username: str, password: str, host: str,
                       port: int, database: str = None, timeout: int = 5) -> Engine:
        temp_url = self.create_temp_url(username, password, host, port, database)
        connect_args = self.get_connect_args(timeout)
        return create_engine(temp_url, connect_args=connect_args)


class DriverRegistry:
    """Registro centralizado de drivers de base de datos"""
    
    _drivers: Dict[str, DatabaseDriver] = {}
    
    @classmethod
    def register(cls, driver: DatabaseDriver) -> None:
        """Registra un nuevo driver"""
        cls._drivers[driver.name] = driver
    
    @classmethod
    def get(cls, driver_name: str) -> Optional[DatabaseDriver]:
        """Obtiene un driver por nombre"""
        return cls._drivers.get(driver_name)
    
    @classmethod
    def list_available(cls) -> list[str]:
        """Lista todos los drivers disponibles"""
        return list(cls._drivers.keys())
    
    @classmethod
    def get_or_raise(cls, driver_name: str) -> DatabaseDriver:
        """Obtiene un driver o lanza excepción si no existe"""
        driver = cls.get(driver_name)
        if not driver:
            available = cls.list_available()
            raise ValueError(
                f"Driver '{driver_name}' no soportado. "
                f"Drivers disponibles: {available}"
            )
        return driver

# Alias para fácil importación
drivers = DriverRegistry