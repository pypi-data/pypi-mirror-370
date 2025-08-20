import sys
import click
from .model import NewSchemaCommand

from tai_sql import pm

@click.command()
@click.argument('name')
def new_schema(name: str):
    """Crea un nuevo esquema en el proyecto"""
    if not name:
        click.echo("❌ Error: Debes proporcionar un nombre para el esquema.", err=True)
        sys.exit(1)
    
    project_root = pm.find_project_root()
    if project_root is None:
        click.echo("❌ Error: No se encontró proyecto TAI-SQL", err=True)
        click.echo("   Ejecuta este comando una vez hecho tai-sql init", err=True)
        sys.exit(1)

    try:
        command = NewSchemaCommand(namespace=project_root.name, schema_name=name)
        command.create()
    except Exception as e:
        click.echo(f"❌ Error al crear el esquema: {str(e)}", err=True)
        sys.exit(1)