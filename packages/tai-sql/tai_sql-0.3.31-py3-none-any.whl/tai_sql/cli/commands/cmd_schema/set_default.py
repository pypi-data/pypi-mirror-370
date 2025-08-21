import sys
import click
from tai_sql import pm


@click.command()
@click.argument('schema_name')
def set_default_schema(schema_name: str):
    """Establece el schema por defecto del proyecto"""
    
    try:
        # Verificar que estamos en un proyecto TAI-SQL
        project_root = pm.find_project_root()
        if not project_root:
            click.echo("❌ No se encontró proyecto TAI-SQL", err=True)
            click.echo("   Ejecuta este comando desde un directorio de proyecto", err=True)
            sys.exit(1)
        
        # Obtener configuración actual
        config = pm.get_project_config()
        if not config:
            click.echo("❌ No se pudo cargar la configuración del proyecto", err=True)
            sys.exit(1)
        
        click.echo(f"📁 Proyecto: {config.name}")
        
        # Verificar que el schema existe
        available_schemas = pm.discover_schemas()
        
        if schema_name not in available_schemas:
            click.echo(f"❌ El schema '{schema_name}' no existe en el proyecto", err=True)
            
            if available_schemas:
                click.echo()
                click.echo("📄 Schemas disponibles:")
                for schema in available_schemas:
                    marker = "✅" if schema == config.default_schema else "  "
                    click.echo(f"   {marker} {schema}")
                
                if config.default_schema:
                    click.echo()
                    click.echo(f"📌 Schema por defecto actual: {config.default_schema}")
            else:
                click.echo("   No se encontraron schemas en el proyecto")
                click.echo("   💡 Crea un schema con: tai-sql new-schema <nombre>")
            
            sys.exit(1)
        
        # Verificar si ya es el schema por defecto
        if schema_name == config.default_schema:
            click.echo(f"ℹ️  '{schema_name}' ya es el schema por defecto")
            sys.exit(0)
        
        # Establecer como schema por defecto
        click.echo(f"🔄 Estableciendo '{schema_name}' como schema por defecto...")
        
        pm.set_default_schema(schema_name)
        
        # Actualizar el schema actual en memoria
        pm.set_current_schema(schema_name)
        
        click.echo(f"✅ Schema por defecto actualizado: {schema_name}")
        
        # Mostrar información adicional
        schema_file = project_root / pm.SCHEMAS_DIR / f"{schema_name}.py"
        click.echo(f"📄 Archivo: {schema_file.relative_to(project_root)}")
        
        click.echo()
        click.echo("💡 Próximos pasos:")
        click.echo("   • Los comandos sin --schema usarán este schema automáticamente")
        click.echo("   • tai-sql generate")
        click.echo("   • tai-sql push")
        click.echo("   • tai-sql ping")
        
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error inesperado: {e}", err=True)
        sys.exit(1)