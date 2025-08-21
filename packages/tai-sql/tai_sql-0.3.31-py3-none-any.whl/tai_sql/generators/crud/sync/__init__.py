import os
import jinja2
from typing import ClassVar, Optional

from tai_sql import pm
from ...base import BaseGenerator

class SyncCRUDGenerator(BaseGenerator):
    """
    Generador de clases CRUD para modelos SQLAlchemy con soporte sync/async.
    """

    _jinja_env: ClassVar[jinja2.Environment] = None
    
    def __init__(self, 
                 output_dir: Optional[str] = None, 
                 models_import_path: str = "database.models",
                 max_depth: int = 5,
                 logger_name: str = 'tai-sql'):
        """
        Inicializa el generador CRUD.
        
        Args:
            output_dir: Directorio de salida para los archivos CRUD
            models_import_path: Ruta de importación donde están los modelos generados
        """
        super().__init__(output_dir)
        self.models_import_path = models_import_path
        self.max_depth = max_depth
        self.logger_name = logger_name
    
    @property
    def jinja_env(self) -> jinja2.Environment:
        """Retorna el entorno Jinja2 configurado"""
        if self._jinja_env is None:
            templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
            self._jinja_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(templates_dir),
                trim_blocks=True,
                lstrip_blocks=True
            )
            self._jinja_env.filters['repr'] = repr
        return self._jinja_env
    
    def generate(self) -> str:
        """
        Genera las clases CRUD según el modo especificado.
        
        Returns:
            Ruta al directorio generado
        """
        
        # Generar session_manager.py
        self.generate_session_manager()
        
        # Generar daos.py
        self.generate_daos()
        
        # Generar dtos.py
        self.generate_dtos()
        
        # Generar __init__.py
        self.generate_init_file()

        # Generar utils.py
        self.generate_utils()

        return self.config.output_dir
    
    def generate_session_manager(self) -> None:
        """
        Genera el archivo session_manager.py
        """
        template = self.jinja_env.get_template(f'session_manager.py.jinja2')

        imports = [
            'from __future__ import annotations',
            'import os',
            'import re',
            'from urllib.parse import (',
            '    unquote',
            ')',
            'from typing import (',
            '    Optional,',
            '    Generator',
            ')',
            'from contextlib import (',
            '    contextmanager',
            ')',
            'from urllib.parse import (',
            '    urlparse,',
            '    parse_qs',
            ')',
            'from sqlalchemy import (',
            '    create_engine,',
            '    Engine,',
            '    URL',
            ')',
            'from sqlalchemy.orm import (',
            '    sessionmaker,',
            '    Session',
            ')'
        ]
        
        code = template.render(
            imports=imports,
            provider=pm.db.provider,
            engine_params=pm.db.engine_params.to_dict(),
            connection_params=pm.db.provider.get_connection_params()
        )
        
        file_path = os.path.join(self.config.output_dir, 'session_manager.py')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
    
    def generate_daos(self) -> None:
        """
        Genera el archivo daos.py
        """
        template = self.jinja_env.get_template(f'daos.py.jinja2')

        imports = [
            'from __future__ import annotations',
            'from typing import (',
            '    List,',
            '    Optional,',
            '    Dict,',
            '    Literal,',
            '    Any,',
            '    TYPE_CHECKING',
            ')',
            'from sqlalchemy.orm import Session',
            'from sqlalchemy import (',
            '    select,',
            '    update,',
            '    delete,',
            '    func',
            ')',
            'from .session_manager import SyncSessionManager',
            'from .dtos import *',
            '',
            'from .utils import (',
            '    error_handler,',
            '    get_loading_options,',
            '    load_relationships_from_dto',
            ')',
            f'from {self.models_import_path} import *',
            'from tai_alphi import Alphi',
            '',
            '',
            'if TYPE_CHECKING:',
            '    from pandas import DataFrame, Series  # type: ignore[import-untyped]'
        ]

        has_datetime = any(
                any(col.type == 'datetime' or col.type == 'date' or col.type == 'time' for col in model.columns.values())
                for model in self.models
            )
        if has_datetime:
            imports.append('from datetime import datetime, date, time')
        
        models_data = [model.info() for model in self.models]

        code = template.render(
            imports=imports,
            models=models_data,
            models_import_path=self.models_import_path,
            schema_name=pm.db.schema_name,
            max_depth=self.max_depth,
            logger_name=self.logger_name
        )
        
        file_path = os.path.join(self.config.output_dir, 'daos.py')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
    
    def generate_dtos(self) -> None:
        """
        Genera el archivo dtos.py
        """
        template = self.jinja_env.get_template(f'dtos.py.jinja2')

        imports = [
            'from __future__ import annotations',
            'from typing import (',
            '    List,',
            '    Optional,',
            '    Dict,',
            '    Literal,',
            '    Any,',
            '    TYPE_CHECKING',
            ')',
            f'from {self.models_import_path} import *',
            'from pydantic import (',
            '    BaseModel,',
            '    Field,',
            '    ConfigDict',
            ')',
            '',
            'from tai_alphi import Alphi',
            '',
            'from .utils import (',
            '    should_include_relation,',
            '    get_nested_includes,',
            ')',
            '',
            'if TYPE_CHECKING:',
            '    from pandas import DataFrame, Series  # type: ignore[import-untyped]'
        ]

        has_datetime = any(
                any(col.type == 'datetime' or col.type == 'date' or col.type == 'time' for col in model.columns.values())
                for model in self.models
            )
        if has_datetime:
            imports.append('from datetime import datetime, date, time')
        
        models_data = [model.info() for model in self.models]

        code = template.render(
            imports=imports,
            models=models_data,
            models_import_path=self.models_import_path,
            schema_name=pm.db.schema_name,
            max_depth=self.max_depth,
            logger_name=self.logger_name
        )
        
        file_path = os.path.join(self.config.output_dir, 'dtos.py')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
    
    def generate_init_file(self) -> None:
        """
        Genera el archivo __init__.py
        """
        template = self.jinja_env.get_template(f'__init__.py.jinja2')

        imports = [
            'from __future__ import annotations',
            'from typing import Optional',
            'from .session_manager import SyncSessionManager',
            'from .dtos import *',
            'from .daos import *',
        ]
        
        models = [{'name': model._name, 'tablename': model.tablename, 'is_view': model.is_view} for model in self.models]
        enums = [enum.info() for enum in self.enums]
        
        code = template.render(
            imports=imports,
            models=models,
            enums=enums,
            models_import_path=self.models_import_path,
            mode_prefix='Sync',  # 'Sync' o 'Async'
            schema_name=pm.db.schema_name
        )
        
        file_path = os.path.join(self.config.output_dir, '__init__.py')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)

    def generate_utils(self) -> None:
        """
        Genera el archivo utils.py
        """
        template = self.jinja_env.get_template(f'utils.py.jinja2')

        imports = [
            'import functools',
            'from typing import (',
            '    Any,',
            '    List,',
            '    Optional',
            ')',
            '',
            'from sqlalchemy import exc',
            'from sqlalchemy.orm import (',
            '    Session,',
            '    class_mapper,',
            '    selectinload,',
            '    joinedload,',
            '    RelationshipProperty',
            ')',
            '',
            'from pydantic import BaseModel',
            'from tai_alphi import Alphi'
        ]
        
        code = template.render(
            imports=imports,
            logger_name=self.logger_name,
            schema_name=pm.db.schema_name,
        )
        
        file_path = os.path.join(self.config.output_dir, 'utils.py')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)