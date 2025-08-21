import os
import jinja2
from typing import List, ClassVar
from pathlib import Path

from tai_sql import pm
from ..base import BaseGenerator

class ModelsGenerator(BaseGenerator):
    """Generador de modelos SQLAlchemy a partir de clases Table"""

    _jinja_env: ClassVar[jinja2.Environment] = None
    _imports: ClassVar[List[str]] = None
    
    @property
    def jinja_env(self) -> jinja2.Environment:
        """
        Retorna el entorno Jinja2 configurado para renderizar las plantillas
        """
        if self._jinja_env is None:
            templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
            self._jinja_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(templates_dir),
                trim_blocks=True,
                lstrip_blocks=True
            )
        return self._jinja_env
    
    def generate(self) -> str:
        """
        Genera un único archivo con todos los modelos SQLAlchemy.
        
        Returns:
            Ruta al archivo generado
        """

        self.validate_encryption_setup()

        # Preparar datos para la plantilla
        models_data = []
        
        # Analizar cada modelo y recopilar información
        for model in self.models:
            model_info = model.info()
            models_data.append(model_info)
        
        # Cargar la plantilla
        template = self.jinja_env.get_template('__init__.py.jinja2')
        
        # Renderizar la plantilla
        code = template.render(
            imports=self.imports,
            models=models_data,
            is_postgres=pm.db.provider.drivername == 'postgresql',
            schema_name=pm.db.schema_name,
            secret_key_name=pm.db.secret_key_name,
            has_encrypted_columns=self.has_encrypted_columns
        )

        os.makedirs(self.file_path, exist_ok=True)
        
        # Escribir el archivo generado
        path = os.path.join(self.file_path, '__init__.py')

        with open(path, 'w') as f:
            f.write(code)
        
        return self.file_path
    
    @property
    def file_path(self) -> Path:
        """
        Retorna la ruta al archivo generado.
        
        Returns:
            Ruta al archivo de modelos
        """
        return Path(self.config.output_dir) / pm.db.schema_name / 'models'
    
    @property
    def imports(self) -> List[str]:
        """
        Retorna una lista de imports necesarios para el archivo generado.
        
        Returns:
            Lista de strings con los imports
        """
        if self._imports is None:
            
            self._imports = [
                'from __future__ import annotations',
                'from typing import List, Optional',
                'from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship'
            ]

            has_datetime = any(
                any(col.type == 'datetime' or col.type == 'date' or col.type == 'time' for col in model.columns.values())
                for model in self.models
            )
            if has_datetime:
                self._imports.append('from datetime import datetime, date, time')

            # Recopilar todos los tipos de SQLAlchemy únicos de las columnas
            sqlalchemy_imports = set()
            sqlalchemy_imports.add('ForeignKeyConstraint')
            for model in self.models:
                for col in model.columns.values():
                    if hasattr(col, 'user_defined_sqlalchemy_type') and col.user_defined_sqlalchemy_type:
                        sqlalchemy_imports.add(col.user_defined_sqlalchemy_type)
            
            if sqlalchemy_imports:
                types_str = ', '.join(sorted(sqlalchemy_imports))
                self._imports.append(f'from sqlalchemy import {types_str}')
            
            if self.has_encrypted_columns:
                self._imports.extend([
                    'import os',
                    'from cryptography.fernet import Fernet',
                    'from sqlalchemy.ext.hybrid import hybrid_property',
                    'import base64'
                ])
                
        return self._imports
    
    @property
    def has_encrypted_columns(self) -> bool:
        return any(
            any(hasattr(col, 'encrypt') and col.encrypt for col in model.columns.values())
            for model in self.models
        )
    
    def validate_encryption_setup(self):
        """
        Valida que la configuración de encriptación sea correcta.
        Verifica que existe la variable de entorno de la clave secreta si hay columnas encriptadas.
        """
        
        # Si hay columnas encriptadas, verificar que existe la variable de entorno
        if self.has_encrypted_columns:
            secret_key = os.getenv(pm.db.secret_key_name)
            if not secret_key:
                raise ValueError(
                    f"Se encontraron columnas con encrypt=True pero "
                    f"la variable de entorno '{pm.db.secret_key_name}' no está definida. "
                    f"Por favor, define esta variable con una clave secreta segura."
                )
            
            # Verificar que la clave tenga una longitud mínima
            if len(secret_key) < 32:
                raise ValueError(
                    f"La clave secreta en '{pm.db.secret_key_name}' debe tener al menos 32 caracteres. "
                    f"Longitud actual: {len(secret_key)}"
                )
            # Verificar que la clave sea una cadena válida para Fernet
            try:
                # Verificar que se puede crear una instancia válida de Fernet
                import base64
                from cryptography.fernet import Fernet
                Fernet(base64.urlsafe_b64encode(secret_key.encode()[:32].ljust(32, b'0')))
            except ImportError:
                raise ImportError(
                    "La librería 'cryptography' no está instalada. "
                    "Para usar columnas encriptadas, instala la dependencia con: "
                    "poetry add cryptography | pip install cryptography"
                )
            except Exception as e:
                raise ValueError(
                    f"Error al validar la clave secreta para encriptación: {e}. "
                    f"Asegúrate de que la clave en '{pm.db.secret_key_name}' sea válida."
                )