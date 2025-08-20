import subprocess
import sys
import os
import shutil
from pathlib import Path
import click

from tai_sql import pm
from ..cmd_schema import NewSchemaCommand

class InitCommand:

    def __init__(self, namespace: str, schema_name: str):
        self.namespace = namespace
        self.schema_name = schema_name
    
    @property
    def subnamespace(self) -> str:
        """Retorna el subnamespace basado en el namespace"""
        return self.namespace.replace('-', '_')
    
    def check_poetry(self):
        """Verifica que Poetry esté instalado y disponible"""
        try:
            subprocess.run(['poetry', '--version'], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            click.echo("❌ Error: Poetry no está instalado o no está en el PATH", err=True)
            click.echo("Instala Poetry desde: https://python-poetry.org/docs/#installation")
            sys.exit(1)
    
    def check_directory_is_avaliable(self):
        """Verifica que el directorio del proyecto no exista"""
        if os.path.exists(self.namespace):
            click.echo(f"❌ Error: el directorio '{self.namespace}' ya existe", err=True)
            sys.exit(1)
    
    def check_virtualenv(self):
        """Verifica que el entorno virtual de Poetry esté activo"""
        if 'VIRTUAL_ENV' not in os.environ:
            click.echo("❌ Error: No hay entorno virutal activo", err=True)
            click.echo("   Puedes crear uno con 'pyenv virtualenv <env_name>' y asignarlo con 'pyenv local <env_name>'", err=True)
            sys.exit(1)
    
    def create_project(self):
        """Crea el proyecto base con Poetry"""
        click.echo(f"🚀 Creando '{self.namespace}'...")
        
        try:
            subprocess.run(['poetry', 'new', self.namespace], 
                        check=True, 
                        capture_output=True)
            subprocess.run(['sed', '-i', '/^python *=/d', 'pyproject.toml'], 
                        cwd=self.namespace,
                        check=True, 
                        capture_output=True)
            subprocess.run(['sed', '-i', '/\\[tool.poetry.dependencies\\]/a python = "^3.10"', 'pyproject.toml'], 
                        cwd=self.namespace,
                        check=True, 
                        capture_output=True)
            # subprocess.run(['poetry', 'add', '--group', 'dev', 'tai-sql'],
            #             cwd=self.namespace,
            #             check=True, 
            #             capture_output=True)
            subprocess.run(['poetry', 'install'],
                        cwd=self.namespace,
                        check=True, 
                        capture_output=True)
            click.echo(f"✅ poetry new '{self.namespace}': OK")
        except subprocess.CalledProcessError as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)

    def add_dependencies(self):
        """Añade las dependencias necesarias al proyecto"""
        click.echo("📦 Añadiendo dependencias...")
        
        dependencies = ['sqlalchemy', 'psycopg2-binary', 'cryptography', 'pydantic']
        
        for dep in dependencies:
            try:
                subprocess.run(['poetry', 'add', dep], 
                            cwd=self.namespace,
                            check=True, 
                            capture_output=True)
                click.echo(f"   ✅ {dep} añadido")
            except subprocess.CalledProcessError as e:
                click.echo(f"   ❌ Error al añadir dependencia {dep}: {e}", err=True)
                sys.exit(1)
    
    def add_folders(self) -> None:
        """Crea la estructura adicional del proyecto"""
        new_schema = NewSchemaCommand(self.namespace, self.schema_name)
        new_schema.create()
        test_dir = Path(self.namespace) / 'tests'
        if test_dir.exists():
            shutil.rmtree(test_dir)
        # Crear directorio para los diagramas
        diagrams_dir = Path(self.namespace) / 'diagrams'
        diagrams_dir.mkdir(parents=True, exist_ok=True)
    
    def create_project_config(self) -> None:
        """Crea el archivo .taisqlproject con la configuración inicial"""
        try:
            project_root = Path(self.namespace)
            pm.create_config(
                name=self.namespace,
                project_root=project_root,
                default_schema=self.schema_name
            )
            
        except Exception as e:
            click.echo(f"❌ Error al crear configuración del proyecto: {e}", err=True)
            sys.exit(1)

    def msg(self):
        """Muestra el mensaje de éxito y next steps con información del proyecto"""
        # ✅ Obtener información del proyecto creado
        project_root = Path(self.namespace)
        project_config = pm.load_config(project_root)
        
        click.echo()
        click.echo(f'🎉 ¡Proyecto "{self.namespace}" creado exitosamente!')
        
        # Mostrar información del proyecto
        if project_config:
            click.echo()
            click.echo("📋 Información del proyecto:")
            click.echo(f"   Nombre: {project_config.name}")
            click.echo(f"   Schema por defecto: {project_config.default_schema}")
        
        click.echo()
        click.echo("📋 Próximos pasos:")
        click.echo("   1. Configurar MAIN_DATABASE_URL en tu entorno:")
        click.echo("      export MAIN_DATABASE_URL='postgresql://user:pass@host:5432/dbname'")
        click.echo(f"   2. Definir tus modelos en schemas/{self.schema_name}.py")
        click.echo("   3. Crear recursos:")
        click.echo("      tai-sql generate    # Usa schema por defecto automáticamente")
        click.echo("      tai-sql push --createdb")
        click.echo()
        click.echo("🔧 Comandos útiles:")
        click.echo("   tai-sql info                       # Ver info del proyecto")
        click.echo("   tai-sql new-schema <nombre>        # Crear nuevo schema")
        click.echo("   tai-sql set-default-schema <path>  # Cambiar schema por defecto")
        click.echo()
        click.echo("🔗 Documentación: https://github.com/triplealpha-innovation/tai-sql")
        