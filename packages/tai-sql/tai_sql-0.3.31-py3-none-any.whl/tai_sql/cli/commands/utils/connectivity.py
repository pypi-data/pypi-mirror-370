# -*- coding: utf-8 -*-
import socket
import subprocess
import platform
import click
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

from tai_sql import pm


def resolve_hostname(host: str) -> bool:
    """
    Verifica que el hostname se pueda resolver a una IP.
    
    Args:
        host (str): Hostname a resolver
        
    Returns:
        bool: True si se puede resolver
    """
    try:
        ip = socket.gethostbyname(host)
        click.echo(f"   🔍 DNS: {host} → {ip}")
        return True
    except socket.gaierror as e:
        click.echo(f"   ❌ Error de DNS: No se puede resolver {host}: {e}")
        return False


def icmp_ping(host: str, timeout: int = 5) -> bool:
    """
    Realiza un ping ICMP al host.
    
    Args:
        host (str): Host a hacer ping
        timeout (int): Timeout en segundos
        
    Returns:
        bool: True si el ping es exitoso
    """
    try:
        # Detectar sistema operativo para usar el comando correcto
        system = platform.system().lower()
        
        if system == "windows":
            cmd = ["ping", "-n", "1", "-w", str(timeout * 1000), host]
        else:  # Linux, macOS, etc.
            cmd = ["ping", "-c", "1", "-W", str(timeout), host]
        
        # Ejecutar ping con timeout
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 2  # Un poco más de timeout para el proceso
        )
        
        if result.returncode == 0:
            click.echo(f"   ✅ ICMP: {host} responde a ping")
            return True
        else:
            click.echo(f"   ⚠️  ICMP: {host} no responde a ping (puede estar bloqueado)")
            return False
            
    except subprocess.TimeoutExpired:
        click.echo(f"   ⚠️  ICMP: Timeout al hacer ping a {host}")
        return False
    except FileNotFoundError:
        click.echo(f"   ⚠️  ICMP: Comando ping no disponible")
        return False
    except Exception as e:
        click.echo(f"   ⚠️  ICMP: Error al hacer ping a {host}: {e}")
        return False


def tcp_ping(host: str, port: int, timeout: int = 5) -> bool:
    """
    Verifica conectividad TCP al puerto específico.
    
    Args:
        host (str): Host a verificar
        port (int): Puerto a verificar
        timeout (int): Timeout en segundos
        
    Returns:
        bool: True si el puerto está accesible
    """
    try:
        with socket.create_connection((host, port), timeout=timeout):
            click.echo(f"   ✅ TCP: {host}:{port} está accesible")
            return True
    except (socket.timeout, socket.error, ConnectionRefusedError) as e:
        click.echo(f"   ❌ TCP: {host}:{port} no está accesible: {e}")
        return False
    except Exception as e:
        click.echo(f"   ❌ TCP: Error inesperado al conectar a {host}:{port}: {e}")
        return False


def ping_remotehost(host: str, port: int, timeout: int = 5) -> bool:
    """
    Verifica conectividad a un host remoto usando múltiples métodos.
    
    Args:
        host (str): Hostname o IP
        port (int): Puerto del servidor
        timeout (int): Timeout en segundos
        
    Returns:
        bool: True si el host está disponible
    """
    click.echo(f"🔍 Verificando conectividad a {host}:{port}")
    
    # Método 1: Verificar resolución DNS
    if not resolve_hostname(host):
        return False
    
    # Método 2: Ping ICMP (si está disponible)
    icmp_result = icmp_ping(host, timeout)
    
    # Método 3: Verificar conectividad TCP al puerto específico
    tcp_result = tcp_ping(host, port, timeout)
    
    # Mostrar resultados
    if icmp_result and tcp_result:
        click.echo()
        click.echo(f"    ✅ {host}:{port} está completamente disponible")
        return True
    elif tcp_result:
        click.echo()
        click.echo(f"    ✅ {host}:{port} está disponible (TCP), pero ICMP puede estar bloqueado")
        return True
    elif icmp_result:
        click.echo()
        click.echo(f"    ⚠️  {host} responde a ping, pero el puerto {port} no está disponible")
        return False
    else:
        click.echo()
        click.echo(f"    ❌ {host}:{port} no está disponible")
        return False


def ping_localhost(port: int=5432, timeout: int=5) -> bool:
    """
    Verifica conectividad a localhost usando socket.
    
    Args:
        port (int): Puerto del servidor
        timeout (int): Timeout en segundos
        
    Returns:
        bool: True si localhost:port está disponible
    """
    click.echo(f"🔍 Verificando conectividad a localhost:{port}")
    
    try:
        with socket.create_connection(('localhost', port), timeout=timeout):
            click.echo(f"    ✅ localhost:{port} está disponible")
            return True
    except (socket.timeout, socket.error, ConnectionRefusedError) as e:
        click.echo(f"   ❌ localhost:{port} no está disponible: {e}")
        return False


def test_connection() -> bool:
    """
    Verifica la conectividad al servidor usando el driver específico
    """
    try:
        click.echo(f"🔍 Verificando accesibilidad al servidor para: {pm.db.provider.username} ")
        
        # Probar conexión
        with pm.db.adminengine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
            
        click.echo(f"    ✅ {pm.db.provider.username} tiene acceso a {pm.db.provider.host}:{pm.db.provider.port}")
        return True
        
    except ValueError as e:
        click.echo(f"❌ {e}", err=True)
        return False
    except OperationalError as e:
        if "authentication" in str(e).lower() or "access denied" in str(e).lower():
            click.echo("⚠️  Servidor accesible pero hay problemas de autenticación")
            click.echo(f"   Verifica usuario/contraseña para {pm.db.provider.username}")
            return True
        else:
            click.echo(f"❌ Error de conexión al servidor: {e}")
            return False
    except Exception as e:
        click.echo(f"❌ Error inesperado al conectar al servidor: {e}")
        return False


def verify_server_connection(host: str, port: int, timeout: int = 5) -> bool:
    """
    Verifica la conectividad completa al servidor de base de datos.
    
    Args:
        timeout (int): Timeout en segundos
        
    Returns:
        bool: True si hay conectividad completa
    """

    # Para localhost, usar métodos específicos
    if host in ['localhost', '127.0.0.1', '::1']:
        ping = ping_localhost(port, timeout)
    else: 
        # Para hosts remotos, intentar múltiples métodos
        ping = ping_remotehost(host, port, timeout)
    
    # Ping básico al host
    if not ping:
        click.echo("❌ No hay conectividad de red al servidor")
        return False
    
    # Intentar conexión a nivel de base de datos
    return test_connection()


def db_exist(database: str) -> bool:
    """
    Verifica si existe la base de datos usando el driver específico
    """
    try:
        click.echo(f"🔍 Verificando existencia de la base de datos: {database}")
        
        with pm.db.adminengine.connect() as conn:
            # Usar query específica del driver
            query = pm.db.driver.database_exists_query()
            result = conn.execute(text(query), {"db_name": database})
            exists = result.fetchone() is not None
            
            if exists:
                click.echo(f"    ✅ La base de datos '{database}' existe")
            else:
                click.echo(f"    ❌ La base de datos '{database}' no existe")
            
            return exists
            
    except ValueError as e:
        click.echo(f"    ❌ {e}", err=True)
        return False
    except (OperationalError, ProgrammingError) as e:
        click.echo(f"    ❌ La base de datos no existe: {e}", err=True)
        return False
    except Exception as e:
        click.echo(f"    ❌ Error inesperado: {e}", err=True)
        return False

def schema_exists(schema_name: str) -> bool:
    """
    Verifica si existe el schema usando el driver específico
    """
    try:
        
        # Verificar si el driver soporta schemas
        click.echo(f"🔍 Verificando existencia del schema: {schema_name}")

        if not pm.db.driver.supports_schemas():
            click.echo(f"    ⚠️  El motor {pm.db.driver.name} no soporta schemas")
            return True  # Asumimos que "existe"

        with pm.db.engine.connect() as conn:
            # Usar query específica del driver
            query = pm.db.driver.schema_exists_query()
            result = conn.execute(text(query), {"schema_name": schema_name})
            exists = result.fetchone() is not None
            
            if exists:
                click.echo(f"    ✅ Schema '{schema_name}' existe")
            else:
                click.echo(f"    ❌ Schema '{schema_name}' no existe")
            
            return exists
            
    except ValueError as e:
        click.echo(f"    ❌ {e}", err=True)
        return False
    except (OperationalError, ProgrammingError) as e:
        click.echo(f"    ❌ Error al verificar schema: {e}", err=True)
        return False
    except Exception as e:
        click.echo(f"    ❌ Error inesperado al verificar schema: {e}", err=True)
        return False
