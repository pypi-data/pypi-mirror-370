import sys
from typing import Optional
import click
import subprocess
from ..utils import GitHubAuth, GitHubClient
from tai_sql import pm

@click.command()
@click.argument('entorno', type=click.Choice(['dev', 'pre', 'pro'], case_sensitive=False))
@click.option('--schema', '-s', type=str)
@click.option('--message', '-m', help='Mensaje personalizado para el deploy')
@click.option('--auto-merge', is_flag=True, help='Auto-merge para development (no recomendado para production)')
@click.option('--dry-run', is_flag=True, help='Solo mostrar qué se haría, sin crear PR')
def deploy(entorno: str, schema: Optional[str]=None, message: Optional[str]=None, auto_merge: bool=False, dry_run: bool=False):
    """
    Crear deployment via Pull Request automática
    
    Este comando:
    1. Valida cambios locales del schema
    2. Crea una rama efímera database-deploy
    3. Crea un PR con metadata del deployment
    4. El workflow de GitHub valida y despliega automáticamente
    
    Ejemplos:
        tai-sql deploy dev public
        tai-sql deploy pro schema_users -m "Deploy nueva tabla usuarios"
        tai-sql deploy pre billing --dry-run
    """
    
    try:

        if schema:
            pm.set_current_schema(schema)

        if not schema and not pm.db:
            click.echo(f"❌ No existe ningún esquema por defecto", err=True)
            click.echo(f"   Puedes definir uno con: tai-sql set-default-schema <nombre>", err=True)
            click.echo(f"   O usar la opción: --schema <nombre_esquema>", err=True)
            sys.exit(1)
        
        schema = pm.db.schema_name

        click.echo(f"🚀 Iniciando deployment: {entorno}/{schema}")
        click.echo()

        # Normalizar entorno
        entorno = entorno.lower()
        if entorno == 'dev':
            entorno = 'development'
        elif entorno == 'pre':
            entorno = 'preproduction'
        elif entorno == 'pro':
            entorno = 'production'
        
        # Autenticación con GitHub
        
        click.echo("🔑 Autenticando con GitHub...")
        token = GitHubAuth.get_token()
        if not token:
            raise click.ClickException("No se pudo obtener autenticación con GitHub")
        
        github = GitHubClient(token)
        
        # Verificar estado del repositorio Git
        click.echo("📂 Verificando repositorio Git...")
        git_status = github.check_git_repository_status()
        
        if not git_status['is_git_repo'] or git_status['error']:
            raise click.ClickException(f"Error de Git: {git_status['error']}")
        
        click.echo(f"   📍 Rama: {git_status['current_branch']}")
        click.echo(f"   📌 Commit: {git_status['current_sha'][:8]}")
        
        if git_status['has_uncommitted_changes']:
            click.echo("   ⚠️  Cambios sin confirmar detectados")
        else:
            click.echo("   ✅ Repositorio limpio")
        
        if dry_run:
            click.echo("🔍 DRY RUN - Mostrando qué se haría:")
            click.echo(f"   1. Crear rama: database-deploy/{entorno}-{schema}-{{timestamp}}")
            click.echo(f"   2. Crear PR para: {entorno}/{schema}")
            click.echo(f"   3. Auto-merge: {'Sí' if auto_merge else 'No'}")
            click.echo(f"   4. Mensaje: {message or 'Sin mensaje'}")
            click.echo("   5. GitHub Actions validaría contra BD del entorno")
            click.echo("   6. Workflow manejaría aprobación y deployment")
            return
        
        # Advertir sobre cambios sin confirmar
        if git_status['has_uncommitted_changes']:
            click.echo("⚠️  ADVERTENCIA: Hay cambios sin confirmar")
            click.echo("   El deployment usará el último commit, no los cambios locales")
            if not click.confirm("¿Continuar con el deployment?", default=False):
                click.echo("💡 Tip: Haz commit de tus cambios antes del deployment")
                return
        
        # Crear PR de deployment
        click.echo("📄 Creando Pull Request de deployment...")
        pr_url = github.create_deployment_pr(entorno, schema, git_status, message, auto_merge)
        
        if not pr_url:
            raise click.ClickException("No se pudo crear el Pull Request")
        
        click.echo(f"✅ Pull Request creada: {pr_url}")
        click.echo()
        
        # Información sobre el flujo
        click.echo("🔄 Flujo de deployment iniciado:")
        click.echo("   1. ⏳ GitHub Actions validará contra la BD del entorno")
        click.echo("   2. 📊 Se generará un comentario con los cambios detectados")
        
        if entorno == 'development':
            if auto_merge:
                click.echo("   3. 🟢 Development con auto-merge: deployment automático tras validación")
            else:
                click.echo("   3. 🟢 Development: cambios seguros se aprobarán automáticamente")
        else:
            required_reviewers = 2 if entorno == 'production' else 1
            click.echo(f"   3. 🟡 {entorno.title()}: requiere {required_reviewers} reviewer(s)")
        
        click.echo("   4. 🚀 Deployment automático al hacer merge")
        click.echo("   5. 🧹 Cleanup automático de la rama")
        
        click.echo()
        click.echo("📋 Próximos pasos:")
        click.echo(f"   👀 Monitorear la PR: {pr_url}")
        click.echo("   📊 Revisar el comentario de validación automática")
        
        if entorno != 'development':
            click.echo("   👥 Solicitar reviews según el entorno")
            
        click.echo("   🔀 Hacer merge cuando esté aprobado")
        
        # Enlaces útiles
        repo_info = github.get_repo_info()
        if repo_info:
            click.echo()
            click.echo("🔗 Enlaces útiles:")
            click.echo(f"   📄 Pull Request: {pr_url}")
            click.echo(f"   🌐 Actions: https://github.com/{repo_info['owner']['login']}/{repo_info['name']}/actions")
        
        # Advertencia importante
        click.echo()
        click.echo("⚠️  IMPORTANTE:")
        click.echo("   • La validación se realiza contra la BD real del entorno")
        click.echo("   • NO se valida localmente para evitar inconsistencias")
        click.echo("   • Espera el comentario de validación antes de aprobar")
        
        if entorno == 'production':
            click.echo("   • Para PRODUCTION: revisa cuidadosamente los cambios destructivos")
        
    except click.Abort:
        click.echo("\n❌ Deployment cancelado por el usuario")
        sys.exit(130)
    except Exception as e:
        click.echo(f"\n❌ Error durante el deployment: {e}")
        sys.exit(1)