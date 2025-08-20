import sys
import click

from tai_sql import pm
from ..utils import verify_server_connection, db_exist

@click.command()
@click.option('--schema', '-s', help='Nombre del esquema')
@click.option('--timeout', '-t', default=5, help='Timeout en segundos para la verificación (default: 5)')
@click.option('--check-db', '-d', is_flag=True, help='También verificar si la base de datos específica existe')
def ping(schema: str=None, timeout: int=5, check_db: bool=False):
    """Verifica la conectividad con el servidor"""

    if schema:
        pm.set_current_schema(schema)

    if not schema and not pm.db:
        click.echo(f"❌ No existe ningún esquema por defecto", err=True)
        click.echo(f"   Puedes definir uno con: tai-sql set-default-schema <nombre>", err=True)
        click.echo(f"   O usar la opción: --schema <nombre_esquema>", err=True)
        sys.exit(1)
    
    # Mostrar información de conexión si no está en modo silencioso

    click.echo("🔧 Información de conexión:")
    click.echo(f"   Motor: {pm.db.provider.drivername}")
    click.echo(f"   Host: {pm.db.provider.host}")
    click.echo(f"   Puerto: {pm.db.provider.port}")
    click.echo(f"   Base de datos: {pm.db.provider.database}")
    click.echo(f"   Usuario: {pm.db.provider.username}")
    click.echo()
    
    success = True
    
    try:
            
        if not verify_server_connection(pm.db.provider.host, pm.db.provider.port, timeout):
            success = False
        
        # Verificar existencia de la base de datos si se solicita
        if check_db and success:

            if not db_exist(pm.db.provider.database):
                success = False
            
        
        click.echo()

        if success:
            click.echo("🎉 Verificación de conectividad completada exitosamente")
        else:
            click.echo("❌ CONECTIVIDAD FALLIDA")
            click.echo("💥 Falló la verificación de conectividad")
        
        # Exit code apropiado
        sys.exit(0 if success else 1)
        
    except click.Abort:
        click.echo()
        click.echo("⚠️  Verificación interrumpida por el usuario")
        sys.exit(130)
    except Exception as e:
        click.echo(f"❌ Error inesperado durante la verificación: {str(e)}", err=True)
        sys.exit(1)