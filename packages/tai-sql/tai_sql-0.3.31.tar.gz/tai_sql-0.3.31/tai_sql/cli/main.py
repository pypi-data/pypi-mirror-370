import click
from .commands import (
    deploy_config,
    new_schema,
    set_default_schema,
    init,
    generate,
    ping,
    info,
    push,
    deploy
)
from tai_sql import pm

config = pm.load_config()
default_schema_name = None

if config:
    pm.set_current_schema(config.default_schema)
    default_schema_name = config.default_schema


@click.group()
def cli():
    """CLI para tai-sql: Un framework de ORM basado en SQLAlchemy."""
    pass

cli.add_command(new_schema)
cli.add_command(set_default_schema)
cli.add_command(init)
cli.add_command(generate)
cli.add_command(ping)
cli.add_command(info)
cli.add_command(push)
# cli.add_command(deploy_config)
# cli.add_command(deploy)

if __name__ == '__main__':
    cli()