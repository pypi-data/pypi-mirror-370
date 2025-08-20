"""
Comando deploy-config para configurar entornos de GitHub
"""
import sys
import click
from typing import Optional
from .workflow import create_workflow_file
from ..utils import GitHubAuth, GitHubClient

from tai_sql.core import Provider
from tai_sql import pm

ENVIRONMENTS = ['development', 'preproduction', 'production']

@click.command()
@click.option('--token', help='Token de GitHub (opcional, se intentará obtener automáticamente)')
@click.option('--force', is_flag=True, help='Sobrescribir variables existentes sin preguntar')
def deploy_config(token: Optional[str], force: bool):
    """
    Configura entornos de GitHub y variables de entorno para deployment
    
    Este comando:
    1. Auténtica con GitHub (SSH o navegador)
    2. Crea entornos development, preproduction, production
    3. Configura el connection string para cada entorno
    """
    
    try:
        click.echo("🚀 Configurando entornos de GitHub para deployment")
        click.echo()
        
        # Autenticación
        if token:
            click.echo("🔑 Usando token proporcionado")
        else:
            click.echo("🔑 Obteniendo autenticación con GitHub...")
            token = GitHubAuth.get_token()
            
            if not token:
                click.echo("❌ No se pudo obtener autenticación con GitHub")
                raise click.ClickException("Autenticación fallida")
        
        # Crear cliente GitHub
        github = GitHubClient(token)
        
        # Obtener información del repositorio
        click.echo("📍 Obteniendo información del repositorio...")
        repo_info = github.get_repo_info()
        
        if not repo_info:
            raise click.ClickException("No se pudo obtener información del repositorio GitHub")
        
        owner = repo_info['owner']['login']
        repo_name = repo_info['name']
        
        click.echo(f"   📂 Repositorio: {owner}/{repo_name}")
        click.echo()

        has_permissions = github.display_permissions_report(owner, repo_name)
        click.echo()
        
        if not has_permissions:
            click.echo("❌ Operación cancelada por permisos insuficientes")
            sys.exit(1)
        
        # Configurar cada entorno
        for environment in ENVIRONMENTS:
            click.echo(f"🏗️  Configurando entorno: {click.style(environment, bold=True)}")
            
            # Crear entorno
            if not github.create_environment(owner, repo_name, environment):
                click.echo(f"   ⚠️  No se pudo crear/verificar entorno '{environment}', continuando...")
                click.echo()
                continue
            
            # Verificar variable existente
            existing_url = github.get_environment_secret(owner, repo_name, environment, pm.db.provider.var_name)
            
            if existing_url:
                click.echo(f"   ℹ️  Variable {pm.db.provider.var_name} ya existe")
                
                if not force:
                    action = click.prompt(
                        f"   ¿Qué deseas hacer?",
                        type=click.Choice(['keep', 'update', 'skip'], case_sensitive=False),
                        default='keep',
                        show_choices=True
                    )
                    
                    if action == 'keep':
                        click.echo(f"   ✅ Manteniendo variable existente para {environment}")
                        click.echo()
                        continue
                    elif action == 'skip':
                        click.echo(f"   ⏭️  Saltando configuración para {environment}")
                        click.echo()
                        continue
                    # Si es 'update', continúa para solicitar nuevo valor
            
            # Solicitar nueva URL de base de datos
            click.echo(f"   🔧 Configurando {pm.db.provider.var_name} para {environment}")
            click.echo(f"      Formato: driver://user:password@host:port/database")
            
            while True:
                database_url: str = click.prompt(
                    f"   {pm.db.provider.var_name} para {environment}",
                    type=str,
                    default="",
                    show_default=False
                )
                
                if not database_url.strip():
                    if click.confirm(f"   ¿Saltear configuración para {environment}?", default=True):
                        click.echo(f"   ⏭️  Sin configuración para {environment}")
                        click.echo()
                        break
                    continue
                
                # Validación básica del formato
                if not Provider.validate_connection_string(database_url.strip()):
                    click.echo("   ❌ Formato de URL inválido. Usa: postgresql://user:password@host:port/database")
                    continue
                
                # Establecer la variable
                if github.set_environment_secret(owner, repo_name, environment, pm.db.provider.var_name, database_url):
                    click.echo(f"   ✅ Variable configurada para {environment}")
                    click.echo()
                    break
                else:
                    click.echo(f"   ❌ Error al configurar variable para {environment}")
                    if not click.confirm("   ¿Reintentar?", default=True):
                        click.echo()
                        break
            
            click.echo()
        
        # Crear workflow de GitHub Actions
        click.echo("📝 Generando workflow de GitHub Actions...")
        if create_workflow_file():
            click.echo("   ✅ Workflow creado en .github/workflows/database.yml")
        else:
            click.echo("   ⚠️  Error al crear workflow, pero la configuración de entornos fue exitosa")

        click.echo()
        
        # Resumen final
        click.echo("📋 Resumen de configuración:")
        click.echo(f"   📂 Repositorio: {owner}/{repo_name}")
        
        for environment in ENVIRONMENTS:
            variables = github.list_environment_secrets(owner, repo_name, environment)
            has_main_db = any(var['name'] == pm.db.provider.var_name for var in variables)
            status = "✅ Configurado" if has_main_db else "⚠️  Sin configurar"
            click.echo(f"   🏗️  {environment}: {status}")
        
        click.echo()
        click.echo("🎉 Configuración de entornos completada")
        click.echo()

        # Instrucciones para commit
        click.echo("📝 Próximos pasos:")
        click.echo("   1. Revisar el workflow generado:")
        click.echo(f"      📄 .github/workflows/database.yml")
        click.echo()
        click.echo("   2. Hacer commit del workflow al repositorio:")
        click.echo("      📤 git add .github/workflows/database.yml")
        click.echo("      📤 git commit -m 'feat: añadir workflow TAI-SQL deploy'")
        click.echo("      📤 git push")
        click.echo()
        click.echo("   3. Usar el workflow:")
        click.echo("      🌐  Actions → TAI-SQL Deploy → Run workflow")
        click.echo("      ⚙️  Seleccionar entorno y schema")
        click.echo("           O directamente con el CLI:")
        click.echo("                tai-sql deploy dev")
        click.echo("                tai-sql deploy pre")
        click.echo("                tai-sql deploy pro")
        click.echo()
        click.echo("   4. Configurar reviewers en GitHub:")
        click.echo(f"      🔧 Settings → Environments → Configurar protection rules")
        
        # Advertencia importante
        click.echo()
        click.echo("⚠️  IMPORTANTE:")
        click.echo("   • Configurar reviewers para cada environment en GitHub")
        click.echo("   • Verificar que las URLs de base de datos son correctas")
        
    except click.Abort:
        click.echo("\n❌ Configuración cancelada por el usuario")
        sys.exit(130)
    except Exception as e:
        click.echo(f"\n❌ Error durante la configuración: {e}")
        sys.exit(1)
