import sys
import click

from ..utils import verify_server_connection, createdb, createschema
from ...services import DriftManager, DDLManager
from ..cmd_generate import run_generate
from tai_sql import pm


@click.command()
@click.option('--schema', '-s', help='Nombre del esquema')
@click.option('--force', '-f', is_flag=True, help='Forzar la generación de recursos, incluso si ya existen')
@click.option('--dry-run', '-d', is_flag=True, help='Mostrar las sentencias DDL sin ejecutarlas')
@click.option('--verbose', '-v', is_flag=True, help='Mostrar información detallada durante la ejecución')
def push(schema: str, force: bool, dry_run: bool, verbose: bool):
    """Síncroniza el esquema con la base de datos"""

    if schema:
        pm.set_current_schema(schema)

    if not schema and not pm.db:
        click.echo(f"❌ No existe ningún esquema por defecto", err=True)
        click.echo(f"   Puedes definir uno con: tai-sql set-default-schema <nombre>", err=True)
        click.echo(f"   O usar la opción: --schema <nombre_esquema>", err=True)
        sys.exit(1)

    try:
        # Validar la configuración del schema

        click.echo(f"🚀 Push schema: {pm.db.schema_name}")

        click.echo()

        if not verify_server_connection(pm.db.provider.host, pm.db.provider.port):
            sys.exit(1)

        createdb(pm.db.provider.database)
        createschema(pm.db.schema_name)
        
        click.echo()

        drift = DriftManager()
        ddl = DDLManager(pm.db.driver)

        drift.run()

        click.echo()

        drift.show()

        statements = ddl.generate(drift)
        
        # Mostrar DDL
        if statements:
            if verbose or dry_run:
                ddl.show()
            else:
                click.echo("   ℹ️  Modo silencioso: No se mostrarán las sentencias DDL")
        
        if not statements:
            return
        
        if dry_run:
            click.echo("🔍 Modo dry-run: No se ejecutaron cambios")
            return

        # Confirmar ejecución
        if not force:
            confirm = click.confirm("¿Deseas ejecutar estas sentencias en la base de datos?")
            if not confirm:
                click.echo("❌ Operación cancelada")
                return
        
        click.echo()
        # Ejecutar DDL
        changes = ddl.execute()

        if changes:

            click.echo()
            run_generate()
        
    except Exception as e:
        import logging
        logging.exception(e)
        click.echo(f"❌ Error al procesar schema: {e}", err=True)
        sys.exit(1)