import sys
import click

from tai_sql import pm

@click.command()
def info():
    """Muestra información del proyecto actual"""
    
    try:
        # Verificar que estamos en un proyecto TAI-SQL
        project_root = pm.find_project_root()
        if not project_root:
            click.echo("❌ No se encontró proyecto TAI-SQL", err=True)
            click.echo("   Ejecuta este comando desde un directorio de proyecto", err=True)
            sys.exit(1)
        
        # Obtener información del proyecto
        config = pm.get_project_config()
        available_schemas = pm.discover_schemas()
        current_schema = pm.db.schema_name
        
        # Mostrar información
        click.echo("📁 Información del proyecto:")
        if config:
            click.echo(f"   Nombre: {config.name}")
            click.echo(f"   Directorio: {project_root}")
            click.echo(f"   Schema por defecto: {config.default_schema or 'No configurado'}")
        else:
            click.echo("   ⚠️  No se pudo cargar la configuración")
        
        click.echo()
        click.echo("📄 Schemas disponibles:")
        
        if available_schemas:
            for schema in available_schemas:
                markers = []
                
                # Marcar schema por defecto
                if config and schema == config.default_schema:
                    markers.append("✅ default")
                
                # Marcar schema actual en memoria
                if schema == current_schema:
                    markers.append("📌 current")
                
                marker_text = f" ({', '.join(markers)})" if markers else ""
                click.echo(f"   • {schema}{marker_text}")
                
                # Mostrar si está cargado
                schema_manager = pm.get_schema_manager(schema)
                if schema_manager and schema_manager.is_loaded:
                    click.echo(f"     └─ Estado: Cargado")
        else:
            click.echo("   (No se encontraron schemas)")
            click.echo("   💡 Crea un schema con: tai-sql new-schema <nombre>")
        
        # Información adicional
        if config and config.default_schema:
            click.echo()
            click.echo("🔧 Comandos disponibles:")
            click.echo("   tai-sql generate              # Usa schema por defecto")
            click.echo("   tai-sql push                  # Usa schema por defecto")
            click.echo("   tai-sql set-default-schema <nombre>  # Cambiar default")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)