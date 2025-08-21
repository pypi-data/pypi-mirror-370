import sys
import click

from tai_sql import pm
from .funcs import run_generate

@click.command()
@click.option('--schema', '-s', help='Nombre del esquema')
@click.option('--all', is_flag=True, help='Generar para todos los esquemas disponibles')
def generate(schema: str=None, all: bool=False):
    """Genera recursos basados en los generadores configurados"""
    
    if schema:
        pm.set_current_schema(schema)

    if not schema and not pm.db:
        click.echo(f"❌ No existe ningún esquema por defecto", err=True)
        click.echo(f"   Puedes definir uno con: tai-sql set-default-schema <nombre>", err=True)
        click.echo(f"   O usar la opción: --schema <nombre_esquema>", err=True)
        sys.exit(1)

    run_generate()