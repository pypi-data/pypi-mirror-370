import sys
from pathlib import Path
import click
from textwrap import dedent

from tai_sql import pm

class NewSchemaCommand:

    def __init__(self, namespace: str, schema_name: str):
        self.namespace = namespace
        self.schema_name = schema_name

    @property
    def subnamespace(self) -> str:
        """Retorna el subnamespace basado en el namespace"""
        return self.namespace.replace('-', '_')
    
    def exists(self) -> bool:
        """Verifica si el esquema ya existe"""
        schemas_dir = Path(self.namespace) / 'schemas'
        return (schemas_dir / f'{self.schema_name}.py').exists()
    
    def create(self):
        """Crea el esquema con la estructura básica"""
        click.echo(f"🚀 Creando esquema '{self.schema_name}' en '{self.namespace}/schemas'...")

        if self.exists():
            click.echo(f"❌ Error: El esquema '{self.schema_name}' ya existe en '{self.namespace}/schemas'.", err=True)
            sys.exit(1)
        
        # Verificar si estamos en un proyecto existente
        project_root = Path(self.namespace)
        existing_config = None
        
        if project_root.exists():
            existing_config = pm.load_config(project_root)
        
        # Crear directorio para el esquema
        schemas_dir = Path(self.namespace) / 'schemas'
        schemas_dir.mkdir(parents=True, exist_ok=True)
        
        # Crear modulo con el contenido exacto del ejemplo
        content = self.get_content()
        (schemas_dir / f'{self.schema_name}.py').write_text(content, encoding='utf-8')

        # Crear directorio para las vistas
        views_dir = Path(self.namespace) / 'views' / self.schema_name
        views_dir.mkdir(parents=True, exist_ok=True)

        self.view_example()
        
        # Actualizar configuración del proyecto si existe
        if existing_config:
            # Si es el primer schema o queremos cambiar el default
            if not existing_config.default_schema:
                pm.update_config(
                    project_root,
                    default_schema=f'schemas/{self.schema_name}.py'
                )
                click.echo(f"   📄 Schema '{self.schema_name}' establecido como default")
        
        click.echo(f"   ✅ '{self.schema_name}.py' creado en '{self.namespace}/schemas/'")
    
    def view_example(self) -> None:
        """Crea un archivo de ejemplo de vista SQL"""
        views_dir = Path(self.namespace) / 'views' / self.schema_name

        sql_content = dedent('''
            SELECT
                usuario.id AS user_id,
                usuario.name AS user_name,
                COUNT(post.id) AS post_count
            FROM usuario
            LEFT JOIN post ON usuario.id = post.author_id
            GROUP BY usuario.id, usuario.name
        ''').strip()
        
        (views_dir / 'user_stats.sql').write_text(sql_content, encoding='utf-8')
    
    def get_content(self) -> str:
        """Retorna el contenido exacto del archivo public.py de ejemplo"""
        return dedent(f'''
            # -*- coding: utf-8 -*-
            """
            Fuente principal para la definición de esquemas y generación de modelos CRUD.
            Usa el contenido de tai_sql para definir tablas, relaciones, vistas y generar automáticamente modelos y CRUDs.
            Usa tai_sql.generators para generar modelos y CRUDs basados en las tablas definidas.
            Ejecuta por consola tai_sql generate para generar los recursos definidos en este esquema.
            """
            from __future__ import annotations
            from tai_sql import *
            from tai_sql.generators import *


            # Configurar el datasource
            datasource(
                provider=env('MAIN_DATABASE_URL'), # Además de env, también puedes usar (para testing) connection_string y params
                schema='{self.schema_name}', # Esquema del datasource
            )

            # Configurar los generadores
            generate(
                ModelsGenerator(
                    output_dir='{self.namespace}/{self.subnamespace}' # Directorio donde se generarán los modelos
                ),
                CRUDGenerator(
                    output_dir='{self.namespace}/{self.subnamespace}', # Directorio donde se generarán los CRUDs
                    mode='sync' # Modo de generación: 'sync' para síncrono, 'async' para asíncrono, 'both' para ambos
                ),
                ERDiagramGenerator(
                    output_dir='{self.namespace}/diagrams', # Directorio donde se generarán los diagramas
                )
            )

            # Definición de tablas y relaciones

            # Ejemplo de definición de tablas y relaciones. Eliminar estos modelos y definir los tuyos propios.
            class Usuario(Table):
                """Tabla que almacena información de los usuarios del sistema"""
                __tablename__ = "usuario"
                
                id: int = column(primary_key=True, autoincrement=True)
                name: str = column(description='Nombre del usuario')
                pwd: str = column(encrypt=True) # Contraseña encriptada
                email: Optional[str] # Nullable
                
                posts: List[Post] # Relación one-to-many (implícita) con la tabla Post

                
            class ContentType(Enum):
                """Tipos de contenido para los posts"""
                TEXT = 'text'
                IMAGE = 'image'
                VIDEO = 'video'


            class Post(Table):
                """Tabla que almacena los posts de los usuarios"""
                __tablename__ = "post"

                id: bigint = column(primary_key=True, autoincrement=True) # Tipo bigint para PostgreSQL
                title: str = 'Post Title' # Valor por defecto
                content: str = column(description='Contenido del post')
                content_type: ContentType = ContentType.TEXT # Tipo de contenido con valor por defecto
                timestamp: datetime = column(default=datetime.now, description='Fecha y hora del post') # Timestamp con generador de valor por defecto
                author_id: int

                comments: List[Comment]

                author: Usuario = relation(fields=['author_id'], references=['id'], backref='posts') # Relación many-to-one con la tabla User

                
            class Comment(Table):
                """Tabla que almacena los comentarios de los posts"""
                __tablename__ = "comment"

                id: int = column(primary_key=True, autoincrement=True)
                content: str = column(description='Contenido del comentario')
                post_id: bigint

                post: Post = relation(fields=['post_id'], references=['id'], backref='comments') # Relación many-to-one con la tabla Post

                            
            # Definición de vistas

            class UserStats(View):
                """Vista que muestra estadísticas de usuarios y sus posts"""
                __tablename__ = "user_stats"
                __query__ = query('user_stats.sql') # Esto es necesario para usar tai-sql push
                
                user_id: int
                user_name: str
                post_count: int
        ''').strip()
