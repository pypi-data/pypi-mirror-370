"""
Provider class for managing database connection parameters.
This class allows creating a database connection provider from environment variables,
connection strings, or individual parameters. It supports parsing connection strings,
handling special characters, and provides a structured way to access connection details.
It also includes methods for creating a URL object compatible with SQLAlchemy.
"""
from __future__ import annotations
import os
import re
from typing import Optional, Literal, ClassVar
from urllib.parse import urlparse, parse_qs, unquote
from sqlalchemy import URL
from sqlalchemy.util import EMPTY_DICT


class Provider:
    """
    Class to manage database connection parameters.
    """

    # Variable de clase para identificar el tipo de origen de datos
    source_input_type: ClassVar[Optional[Literal['env', 'connection_string', 'params']]] = None
    var_name: ClassVar[Optional[str]] = None
    
    def __repr__(self) -> str:
        """Return a string representation of the Provider instance."""
        return f"Provider(DRIVER={self.drivername}, HOST={self.host}:{self.port}, DB={self.database})"

    @classmethod
    def from_environment(cls, var_name: str = 'DATABASE_URL') -> Provider:
        """
        Crea un Provider desde una variable de entorno.
        
        Args:
            variable_name: Nombre de la variable de entorno
            fallback: URL de fallback si la variable no existe
            
        Returns:
            Instancia de Provider configurada desde entorno
        """
        connection_string = os.getenv(var_name)
        if connection_string is None:
            raise ValueError(f'Debes añadir "{var_name}" como variable de entorno')
        
        instance = cls.from_connection_string(connection_string)
        instance.source_input_type = 'env'
        instance.var_name = var_name
        return instance
    
    @classmethod
    def from_connection_string(cls, connection_string: str) -> Provider:
        """
        Crea un Provider desde un string de conexión directo.
        
        ADVERTENCIA: Este método expone credenciales en el código fuente.
        
        Args:
            connection_string: String de conexión completo
            
        Returns:
            Instancia de Provider configurada desde string
            
        Raises:
            ValueError: Si el string de conexión no es válido
        """
        try:
            instance = cls()
            
            # Mejorar el parsing para manejar caracteres especiales
            connection_string = connection_string.strip()
            
            # Verificar formato básico
            if '://' not in connection_string:
                raise ValueError("String de conexión debe tener formato: driver://user:pass@host:port/db")
            
            # Usar urlparse con manejo mejorado de caracteres especiales
            parse = urlparse(connection_string)
            
            # Validar componentes esenciales
            if not parse.scheme:
                raise ValueError("Driver no especificado en el string de conexión")
            
            if not parse.hostname:
                raise ValueError("Host no especificado en el string de conexión")
            
            # Manejar la base de datos (puede estar vacía para algunos casos)
            database = parse.path[1:] if parse.path and len(parse.path) > 1 else None
            # Manejar puerto con valor por defecto según el driver
            port = parse.port
            if port is None:
                # Asignar puertos por defecto según el driver
                default_ports = {
                    'postgresql': 5432,
                    'mysql': 3306,
                    'sqlite': None,
                    'mssql': 1433,
                    'oracle': 1521
                }
                port = default_ports.get(parse.scheme, None)
            
            # Parsear query parameters de forma más robusta
            query_params = {}
            if parse.query:
                try:
                    query_params = parse_qs(parse.query)
                    # Convertir listas de un elemento a valores únicos
                    query_params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
                except Exception as e:
                    # Si falla el parsing de query, continuar sin ellos
                    print(f"⚠️  Advertencia: No se pudieron parsear los parámetros de consulta: {e}")
                    query_params = {}
            
            # Crear la URL con manejo de errores mejorado
            try:
                instance.url = URL.create(
                    drivername=parse.scheme,
                    username=parse.username,
                    password=parse.password,  # urlparse maneja el unquoting automáticamente
                    host=parse.hostname,
                    port=port,
                    database=database,
                    query=query_params
                )
            except Exception as url_error:
                # Proporcionar información más detallada del error
                raise ValueError(
                    f"Error creando URL: {url_error}\n"
                    f"Componentes parseados:\n"
                    f"  - Driver: {parse.scheme}\n"
                    f"  - Usuario: {parse.username}\n"
                    f"  - Host: {parse.hostname}\n"
                    f"  - Puerto: {port}\n"
                    f"  - Base de datos: {database}\n"
                    f"  - Tiene contraseña: {'Sí' if parse.password else 'No'}"
                )
            
            instance.source_input_type = 'connection_string'
            return instance
            
        except Exception as e:
            return cls.from_connection_string_escaped(connection_string)

    @classmethod
    def from_connection_string_escaped(cls, connection_string: str) -> Provider:
        """
        Versión alternativa que maneja manualmente el escaping de caracteres especiales.
        
        Útil cuando urlparse falla con caracteres especiales en las contraseñas.
        
        Args:
            connection_string: String de conexión que puede contener caracteres especiales
            
        Returns:
            Provider configurado
        """
        
        try:
            instance = cls()
            
            # Parsear manualmente para manejar caracteres especiales
            # Patrón para extraer componentes: driver://user:pass@host:port/db
            pattern = r'^([^:]+)://([^:]+):([^@]+)@([^:/]+)(?::(\d+))?(?:/(.*))?$'
            match = re.match(pattern, connection_string.strip())
            
            if not match:
                raise ValueError(
                    "Formato de connection string no válido.\n"
                    "Esperado: driver://username:password@host:port/database"
                )
            
            driver, username, password, host, port, database_and_query = match.groups()
            
            # Separar database de query parameters si existen
            database = None
            query_params = {}
            
            if database_and_query:
                if '?' in database_and_query:
                    database, query_string = database_and_query.split('?', 1)
                    # Parsear query parameters
                    for param in query_string.split('&'):
                        if '=' in param:
                            key, value = param.split('=', 1)
                            query_params[unquote(key)] = unquote(value)
                else:
                    database = database_and_query
            
            # Convertir puerto a entero si existe
            if port:
                try:
                    port = int(port)
                except ValueError:
                    raise ValueError(f"Puerto inválido: {port}")
            
            else:
                # Asignar puertos por defecto según el driver
                default_ports = {
                    'postgresql': 5432,
                    'mysql': 3306,
                    'sqlite': None,
                    'mssql': 1433,
                    'oracle': 1521
                }
                port = default_ports.get(driver, None)
            
            # Crear URL SQLAlchemy
            instance.url = URL.create(
                drivername=driver,
                username=unquote(username) if username else None,
                password=unquote(password) if password else None,
                host=unquote(host) if host else None,
                port=port,
                database=unquote(database) if database else None,
                query=query_params
            )
            
            instance.source_input_type = 'connection_string'
            return instance
            
        except Exception as e:
            raise ValueError(f"Error en parsing manual: {e}")
    
    @classmethod
    def validate_connection_string(cls, connection_string: str) -> bool:
        """
        Valida si un string de conexión tiene el formato correcto.

        Args:
            connection_string: String de conexión a validar

        Returns:
            True si el formato es válido, False en caso contrario
        """
        try:
            cls.from_connection_string(connection_string)
            return True
        except ValueError as e:
            return False
    
    @classmethod
    def from_params(
            cls,
            drivername: str,
            username: str,
            password: str,
            host: str,
            port: int,
            database: str,
            query: dict = EMPTY_DICT
    ) -> Provider:
        """
        Crea un Provider desde parámetros individuales.
        
        ADVERTENCIA: Este método expone credenciales en el código fuente.
        
        Args:
            host: Servidor de base de datos
            database: Nombre de la base de datos
            username: Usuario de conexión
            password: Contraseña de conexión
            port: Puerto de conexión
            driver: Driver de base de datos
            
        Returns:
            Instancia de Provider configurada desde parámetros
        """
        instance = cls()
        instance.url = URL.create(
            drivername=drivername,
            username=username,
            password=password,
            host=host,
            port=port,
            database=database,
            query=query
        )
        instance.source_input_type = 'params'
        return instance

    @property
    def url(self) -> URL:
        """Get the URL object."""
        return self._url
    
    @url.setter
    def url(self, value: URL):
        """Set the URL object."""
        self._url = value
    
    def get_connection_params(self) -> dict:
        """
        Get the connection parameters as a dictionary.
        
        Returns:
            Dictionary with connection parameters
        """
        return {
            'drivername': self.drivername,
            'username': self.username,
            'password': self.password,
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'query': self.query
        }

    @property
    def drivername(self) -> str:
        """Get the driver name."""
        return self.url.drivername
    
    @property
    def username(self) -> Optional[str]:
        """Get the username."""
        return self.url.username
    
    @property
    def password(self) -> str:
        """Get the password."""
        return self.url.password
    
    @property
    def host(self) -> Optional[str]:
        """Get the host."""
        return self.url.host
    
    @property
    def port(self) -> Optional[int]:
        """Get the port."""
        return self.url.port
    
    @property
    def database(self) -> Optional[str]:
        """Get the database name."""
        return self.url.database
    
    @property
    def query(self) -> dict:
        """Get the query parameters."""
        return self.url.query
