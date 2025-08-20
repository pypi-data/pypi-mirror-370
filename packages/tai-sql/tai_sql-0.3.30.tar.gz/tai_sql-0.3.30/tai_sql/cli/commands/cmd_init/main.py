import sys
import click
from .model import InitCommand

@click.command()
@click.option('--name', '-n', default='database', help='Nombre del proyecto a crear')
@click.option('--schema', '-s', default='public', help='Nombre del primer esquema a crear')
def init(name: str, schema: str):
    """Inicializa un nuevo proyecto tai-sql"""
    command = InitCommand(namespace=name, schema_name=schema)
    try:
        command.check_poetry()
        command.check_directory_is_avaliable()
        command.check_virtualenv()
        command.create_project()
        command.add_dependencies()
        command.add_folders()
        command.create_project_config()
        command.msg()
    except Exception as e:
        click.echo(f"❌ Error al inicializar el proyecto: {str(e)}", err=True)
        sys.exit(1)