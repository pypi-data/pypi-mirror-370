import click
import sys
from tai_sql import pm

def run_generate():
    """Run the configured generators."""
    # Ejecutar cada generador
    click.echo("🚀 Ejecutando generadores...")
    click.echo()

    for generator in pm.db.generators:
        try:
            generator_name = generator.__class__.__name__
            click.echo(f"Ejecutando: {click.style(generator_name, bold=True)}")
            
            # El generador se encargará de descubrir los modelos internamente
            result = generator.generate()
            
            click.echo(f"✅ Generador {generator_name} completado con éxito.")
            if result:
                click.echo(f"   Recursos en: {result}")
        except Exception as e:
            click.echo(f"❌ Error al ejecutar el generador {generator_name}: {str(e)}", err=True)
            sys.exit(1)
        
        finally:
            click.echo()