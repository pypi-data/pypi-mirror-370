"""
Clases core para la configuración de conexiones.
"""
from __future__ import annotations
from sqlalchemy.util import EMPTY_DICT
from typing import Optional

from .provider import Provider
from tai_sql import pm

def datasource(
    provider: Provider,
    schema: Optional[str] = 'public',
    secret_key_name: str = 'SECRET_KEY',
    sqlalchemy_logs: bool = False,
    pool_pre_ping: bool = True,
    pool_recycle: int = 3600,
    pool_size: int = 5,
    max_overflow: int = 5,
    pool_timeout: int = 30
) -> bool:
    """
    Configura el proveedor de base de datos y los parámetros de conexión del motor SQLAlchemy.
    
    Esta función establece la configuración global del datasource que será utilizada
    por el sistema para conectarse a la base de datos. Configura tanto el proveedor
    de base de datos como los parámetros del pool de conexiones.
    
    Args:
        provider (Provider): Datos de conexión. Usa env, connection_string o params para crear un Provider.
        schema (Optional[str], optional): Esquema de base de datos a utilizar por defecto. 
            Defaults to 'public'.
        secret_key_name (str, optional): Nombre de la variable de entorno que contiene 
            la clave secreta para encriptación de columnas. Defaults to 'SECRET_KEY'.
        sqlalchemy_logs (bool, optional): Habilita o deshabilita los logs de SQLAlchemy 
            para debugging. Defaults to False.
        pool_pre_ping (bool, optional): Verifica la conexión antes de usarla del pool.
            Útil para detectar conexiones perdidas. Defaults to True.
        pool_recycle (int, optional): Tiempo en segundos después del cual una conexión
            será reciclada. Previene timeouts de conexiones inactivas. Defaults to 3600.
        pool_size (int, optional): Número de conexiones que mantendrá el pool.
            Defaults to 5.
        max_overflow (int, optional): Número máximo de conexiones adicionales que se pueden
            crear más allá del pool_size cuando sea necesario. Defaults to 5.
        pool_timeout (int, optional): Tiempo máximo en segundos para esperar una conexión
            disponible del pool antes de generar un timeout. Defaults to 30.
    
    Returns:
        bool: True si la configuración se estableció correctamente.
        
    Example:
        >>> from tai_sql import env
        >>> datasource(
        ...     provider=env('DATABASE_URL'),
        ...     schema='mi_esquema',
        ...     secret_key_name='MY_SECRET_KEY',
        ...     pool_size=10,
        ...     pool_recycle=7200
        ... )
        True
        
    Note:
        Esta función debe llamarse antes de realizar cualquier operación con la base
        de datos. Los parámetros del pool son especialmente importantes para aplicaciones
        con alta concurrencia.
    """

    pm.db.provider = provider
    pm.db.schema_name = schema
    pm.db.secret_key_name = secret_key_name
    pm.db.engine_params.sqlalchemy_logs = sqlalchemy_logs
    pm.db.engine_params.pool_pre_ping = pool_pre_ping
    pm.db.engine_params.pool_recycle = pool_recycle
    pm.db.engine_params.pool_size = pool_size
    pm.db.engine_params.max_overflow = max_overflow
    pm.db.engine_params.pool_timeout = pool_timeout
    return True

def env(variable_name: str = 'MAIN_DATABASE_URL') -> Provider:
    """
    Crea un Provider desde una variable de entorno (método recomendado).
    
    Args:
        variable_name: Nombre de la variable de entorno
        
    Returns:
        Provider configurado desde variable de entorno
        
    Example:
        ```python
        from tai_sql import env, datasource
        
        # Leer desde MAIN_DATABASE_URL
        datasource(provider=env())
        
        # Leer desde variable personalizada
        datasource(provider=env('MY_DB_URL'))
        ```
    """
    return Provider.from_environment(variable_name)


def connection_string(connection_string: str) -> Provider:
    """
    Crea un Provider desde un string de conexión directo.
    
    ⚠️  ADVERTENCIA: Este método expone credenciales en el código fuente.
    Se recomienda usar env() en su lugar.
    
    Args:
        connection_string: String de conexión completo
        
    Returns:
        Provider configurado desde string de conexión
        
    Example:
        ```python
        from tai_sql import connection_string, datasource
        
        # ❌ NO recomendado - credenciales expuestas
        datasource(provider=connection_string('driver://user:pass@host/db'))
        ```
    """
    return Provider.from_connection_string(connection_string)

def params(
        host: str,
        database: str,
        username: str,
        password: str,
        port: int = 5432,
        driver: str = 'postgresql',
        query: dict = EMPTY_DICT
) -> Provider:
    """
    Crea un Provider desde parámetros individuales de conexión.
    
    ⚠️  ADVERTENCIA DE SEGURIDAD: Este método expone credenciales en el código fuente.
    Se recomienda usar env() en su lugar.
    
    Args:
        host: Servidor de base de datos
        database: Nombre de la base de datos
        username: Usuario de conexión
        password: Contraseña de conexión
        port: Puerto de conexión (default: 5432)
        driver: Driver de base de datos (default: 'postgresql')
        
    Returns:
        Provider configurado desde parámetros
        
    Example:
        ```python
        from tai_sql import params, datasource
        
        # ❌ NO recomendado - credenciales expuestas
        datasource(provider=params(
            host='localhost',
            database='mydb',
            username='user',
            password='secret'
        ))
        ```
    """    
    return Provider.from_params(driver, username, password, host, port, database, query)

def generate(*generators) -> bool:
    """
    Configura los generadores a utilizar para la generación de recursos.
    
    Args:
        *generators: Funciones generadoras a configurar
    
    Custom:
    -
        Puedes crear tus propios generadores heredando de BaseGenerator y pasarlos aquí.
    
    Returns:
        bool: True si la configuración se estableció correctamente.
    
    Example:
        >>> from tai_sql.generators import ModelsGenerator, CRUDGenerator
        >>> generate(
        ...     ModelsGenerator(output_dir='models'),
        ...     CRUDGenerator(output_dir='crud', models_import_path='database.models')
        ... )
        True
    """
    
    pm.db.generators = generators
    return True


def query(name: str) -> str:
    """
    Carga una sentencia SQL desde un archivo en la subcarpeta correspondiente al schema.
    
    Esta función está diseñada para ser utilizada dentro de archivos de schema
    ubicados en schemas/ y busca archivos SQL en views/<nombre_del_archivo_schema>/
    
    Args:
        name (str): Nombre del archivo SQL (con o sin extensión .sql)
        
    Returns:
        str: Contenido del archivo SQL como string
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si el archivo está vacío o no contiene SQL válido
        
    Example:
        ```python
        # En schemas/blog.py
        from tai_sql import query
        from tai_sql.orm import View
        
        class UserStats(View):
            __viewname__ = "user_stats"
            __query__ = query("user_stats.sql")  # Lee views/blog/user_stats.sql
            
            # Definir columnas...
            id: int
            name: str
            post_count: int
        
        # O sin extensión
        class PostSummary(View):
            __viewname__ = "post_summary"
            __query__ = query("post_summary")  # Lee views/blog/post_summary.sql
        ```
        
    Directory Structure:
        ```
        project/
        ├── schemas/
        │   ├── blog.py          # ← Archivo de schema que llama query()
        │   └── analytics.py     # ← Otro archivo de schema
        └── views/               # ← Carpeta base de vistas
            ├── blog/            # ← Subcarpeta para blog.py
            │   ├── user_stats.sql
            │   └── post_summary.sql
            └── analytics/       # ← Subcarpeta para analytics.py
                ├── sales_report.sql
                └── monthly_summary.sql
        ```
        
    File Content Example:
        ```sql
        -- views/blog/user_stats.sql
        SELECT 
            u.id,
            u.name,
            u.email,
            COUNT(p.id) as post_count,
            MAX(p.created_at) as last_post_date
        FROM users u
        LEFT JOIN posts p ON u.id = p.author_id
        GROUP BY u.id, u.name, u.email
        ORDER BY post_count DESC
        ```
    """
    

    try:

        filename = name if name.endswith('.sql') else f"{name}.sql"
        views_path = pm.find_project_root() / pm.VIEWS_DIR / pm.db.schema_name 
        sqlfile = views_path/ filename

        if not sqlfile.exists():
            raise FileNotFoundError(
                f"Archivo SQL '{filename}' no encontrado en 'views/{pm.db.schema_name}/'.\n"
                f"La carpeta está vacía. Crea el archivo '{filename}' en:\n"
                f"  {views_path}\n"
                f"\nEstructura esperada:\n"
                f"  project/\n"
                f"  ├── schemas/{pm.db.schema_name}.py    ← Tu archivo de schema\n"
                f"  └── views/{pm.db.schema_name}/        ← Carpeta para tus archivos SQL\n"
                f"      └── {filename}                    ← Tu archivo SQL aquí"
            )
        
        content = sqlfile.read_text(encoding='utf-8').strip()
        
        if not content: 
            raise ValueError(f"El archivo '{filename}' está vacío")
        
        # Validación básica de SQL
        content_upper = content.upper().strip()
        content_list = content_upper.splitlines()

        for line in content_list:
            if line.strip().startswith('--'):
                continue
            if any(line.startswith(keyword) for keyword in ['SELECT', 'WITH', '(']):
                return content

        raise ValueError(
            f"El archivo '{filename}' no parece contener una consulta SELECT válida.\n"
            f"Las vistas deben empezar con SELECT, WITH o '('.\n"
            f"Archivo: {sqlfile}"
        )
        
    except UnicodeDecodeError as e:
        raise ValueError(f"Error de codificación al leer '{filename}': {e}")
    except Exception as e:
        raise ValueError(f"Error leyendo el archivo '{filename}': {e}")