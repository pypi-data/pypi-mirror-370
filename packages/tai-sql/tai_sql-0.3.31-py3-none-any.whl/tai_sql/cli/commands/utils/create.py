import sys
import click
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

from .connectivity import db_exist, schema_exists
from tai_sql import pm


def createdb(database_name: str) -> bool:
    """
    Crea una base de datos usando el driver específico
    
    Args:
        database_name: Nombre de la base de datos a crear
        
    Returns:
        bool: True si se creó exitosamente o ya existía
    """
    try:

        if db_exist(database_name):
            return True
        
        click.echo(f"🚀 Creando base de datos: {database_name}")

        # Usar la sentencia específica del driver
        create_statement = pm.db.driver.create_database_statement(database_name)
        
        with pm.db.adminengine.connect() as conn:
            conn = conn.execution_options(isolation_level="AUTOCOMMIT")
            conn.execute(text(create_statement))
        
        click.echo(f"✅ Base de datos '{database_name}' creada exitosamente")
        return True
        
    except ValueError as e:
        # Error de driver no soportado
        click.echo(f"❌ {e}", err=True)
        sys.exit(1)
    except OperationalError as e:
        if "already exists" in str(e) or "exists" in str(e):
            click.echo(f"ℹ️  La base de datos '{database_name}' ya existe")
            return True
        else:
            click.echo(f"❌ Error al crear base de datos: {e}", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error inesperado al crear base de datos: {e}", err=True)
        sys.exit(1)


def createschema(schema_name: str) -> bool:
    """
    Crea un schema usando el driver específico
    
    Args:
        schema_name: Nombre del schema a crear
        engine: Engine de SQLAlchemy conectado a la BD
        drivername: Nombre del driver (postgresql, mysql, mssql)
        
    Returns:
        bool: True si se creó exitosamente o ya existía
    """
    try:
        
        # Verificar si el driver soporta schemas
        if not pm.db.driver.supports_schemas():
            click.echo(f"ℹ️  El motor {pm.db.driver.name} no requiere schemas separados")
            return True
        
        # Verificar si ya existe
        if schema_exists(schema_name):
            return True
        
        click.echo(f"🚀 Creando schema: {schema_name}")
        
        # Usar la sentencia específica del driver
        create_statement = pm.db.driver.create_schema_statement(schema_name)
        
        with pm.db.engine.connect() as conn:
            conn = conn.execution_options(autocommit=True)
            conn.execute(text(create_statement))
            conn.execute(text("COMMIT"))
        
        click.echo(f"✅ Schema '{schema_name}' creado exitosamente")
        return True
        
    except ValueError as e:
        # Error de driver no soportado
        click.echo(f"❌ {e}", err=True)
        return False
    except (OperationalError, ProgrammingError) as e:
        if "already exists" in str(e) or "exists" in str(e):
            click.echo(f"ℹ️  El schema '{schema_name}' ya existe")
            return True
        else:
            click.echo(f"❌ Error al crear schema: {e}", err=True)
            return False
    except Exception as e:
        click.echo(f"❌ Error inesperado al crear schema: {e}", err=True)
        return False
