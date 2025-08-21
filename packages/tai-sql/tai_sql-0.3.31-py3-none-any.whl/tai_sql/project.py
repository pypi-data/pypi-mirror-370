"""
Manejo de configuración de proyecto TAI-SQL con soporte para múltiples schemas
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict

from .schema import SchemaManager

@dataclass
class ProjectConfig:
    """Configuración del proyecto TAI-SQL"""
    name: str
    default_schema: Optional[str] = 'public'
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectConfig':
        """Crea ProjectConfig desde diccionario"""
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte ProjectConfig a diccionario"""
        return asdict(self)

class ProjectManager:
    """
    Gestor central de proyectos TAI-SQL con soporte para múltiples SchemaManager
    """
    
    PROJECT_FILE = '.taisqlproject'
    SCHEMAS_DIR = 'schemas'
    VIEWS_DIR = 'views'

    config: Optional[ProjectConfig] = None
    
    _project_root_cache: Optional[Path] = None
    _schema_managers: Dict[str, SchemaManager] = {}
    

    # Variable de clase para el schema en uso
    db: Optional[SchemaManager] = None

    @classmethod
    def find_project_root(cls, start_path: str = '.') -> Optional[Path]:
        """Busca el directorio raíz del proyecto TAI-SQL"""
        if cls._project_root_cache is not None:
            return cls._project_root_cache
            
        current_path = Path(start_path).resolve()

        # Buscar en el directorio actual y subcarpetas
        for dir_path in [current_path] + [p for p in current_path.rglob("*") if p.is_dir()]:
            project_file = dir_path / cls.PROJECT_FILE
            if project_file.exists():
                cls._project_root_cache = dir_path
                return dir_path
        
        return None
    
    @classmethod
    def clear_cache(cls) -> None:
        """Limpia toda la caché del ProjectManager"""
        cls._project_root_cache = None
        cls._schema_managers.clear()
        cls.config = None
        cls.db = None

    @classmethod
    def get_project_config(cls) -> Optional[ProjectConfig]:
        """Obtiene la configuración del proyecto con caché"""
        if cls.config is None:
            cls.load_config()
        return cls.config

    @classmethod
    def create_config(cls, name: str, project_root: Path, default_schema: str=None) -> ProjectConfig:
        """Crea un nuevo proyecto con configuración inicial"""
        config = ProjectConfig(
            name=name,
            default_schema=default_schema or 'public',
        )
        
        cls.save_config(config, project_root)
        return config
    
    @classmethod
    def load_config(cls, project_root: Optional[Path] = None) -> Optional[ProjectConfig]:
        """Carga la configuración del proyecto"""

        if cls.config is not None:
            return cls.config
        
        if project_root is None:
            project_root = cls.find_project_root()
        
        if not project_root:
            return None
        
        project_file = project_root / cls.PROJECT_FILE
        
        if not project_file.exists():
            return None
        
        try:
            with open(project_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

                config = ProjectConfig.from_dict(data)

            cls.config = config  # Guardar en caché
            
            return config
        
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise ValueError(f"Error al leer {cls.PROJECT_FILE}: {e}")
    
    @classmethod
    def save_config(cls, config: ProjectConfig, project_root: Path) -> None:
        """Guarda la configuración del proyecto"""
        project_file = project_root / cls.PROJECT_FILE
        
        try:
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
            
            cls.config = config  # Actualizar caché
        
        except Exception as e:
            raise ValueError(f"Error al escribir {cls.PROJECT_FILE}: {e}")
    
    @classmethod
    def update_config(cls, project_root: Path, **updates) -> ProjectConfig:
        """Actualiza la configuración del proyecto"""
        config = cls.load_config(project_root)
        
        if not config:
            raise ValueError("No se encontró configuración de proyecto")
        
        # Actualizar campos
        for key, value in updates.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        cls.save_config(config, project_root)

        return config
    
    @classmethod
    def discover_schemas(cls, project_root: Optional[Path] = None) -> List[str]:
        """Descubre todos los schemas disponibles en el proyecto"""
        if project_root is None:
            project_root = cls.find_project_root()
        
        if not project_root:
            return []
        
        schemas_dir = project_root / cls.SCHEMAS_DIR
        if not schemas_dir.exists():
            return []
        
        schemas = []
        for schema_file in schemas_dir.glob("*.py"):
            if schema_file.name != "__init__.py":
                schema_name = schema_file.stem
                schemas.append(schema_name)
        
        return schemas
    
    @classmethod
    def get_schema_manager(cls, schema_name: str) -> Optional[SchemaManager]:
        """
        Obtiene o crea un SchemaManager para el schema especificado
        """
        # Verificar caché primero
        if schema_name in cls._schema_managers:
            return cls._schema_managers[schema_name]
        
        # Buscar archivo de schema
        project_root = cls.find_project_root()
        if not project_root:
            return None
        
        schema_file = project_root / cls.SCHEMAS_DIR / f"{schema_name}.py"
        if not schema_file.exists():
            return None
        
        # Crear nuevo SchemaManager
        schema_manager = SchemaManager(schema_name, schema_file)

        cls._schema_managers[schema_name] = schema_manager
        
        return schema_manager
    
    @classmethod
    def get_default_schema(cls) -> Optional[SchemaManager]:
        """Obtiene el SchemaManager del schema por defecto"""
        config = cls.get_project_config()
        if not config or not config.default_schema:
            return None
        
        return cls.get_schema_manager(config.default_schema)
    
    @classmethod
    def set_default_schema(cls, schema_name: str) -> None:
        """Establece el schema por defecto del proyecto en la configuración"""
        project_root = cls.find_project_root()
        if not project_root:
            raise ValueError("No se encontró proyecto TAI-SQL")
        
        # Verificar que el schema existe
        if schema_name not in cls.discover_schemas():
            raise ValueError(f"El schema '{schema_name}' no existe en el proyecto")
        
        # Actualizar configuración
        cls.update_config(project_root, default_schema=schema_name)
    
    @classmethod
    def set_current_schema(cls, schema_name: str) -> SchemaManager:
        """
        Establece el schema actual en la variable db
        
        Args:
            schema_name: Nombre del schema a establecer como actual
            load: Si True, carga automáticamente el schema
            
        Returns:
            SchemaManager del schema establecido
            
        Raises:
            FileNotFoundError: Si el schema no existe
            RuntimeError: Si hay errores al cargar el schema
        """
        schema_manager = cls.get_schema_manager(schema_name)
        if not schema_manager:
            available_schemas = cls.discover_schemas()
            raise FileNotFoundError(
                f"No se encontró el schema '{schema_name}'. "
                f"Schemas disponibles: {available_schemas}"
            )
        
        # Establecer como schema actual
        cls.db = schema_manager
        schema_manager.load()
        schema_manager.validations()
        
        return schema_manager
    
    @classmethod
    def get_project_info(cls) -> Dict[str, Any]:
        """Obtiene información completa del proyecto"""
        config = cls.get_project_config()
        project_root = cls.find_project_root()
        schemas = cls.discover_schemas()
        
        info = {
            'project_root': str(project_root) if project_root else None,
            'config': config.to_dict() if config else None,
            'available_schemas': schemas,
            'loaded_schemas': list(cls._schema_managers.keys()),
            'current_schema': cls.config.default_schema,
            'current_schema_loaded': cls.db.is_loaded if cls.db else False
        }
        
        # Información de cada SchemaManager
        managers_info = {}
        for schema_name, schema_manager in cls._schema_managers.items():
            managers_info[schema_name] = schema_manager.get_info()
        
        info['schema_managers'] = managers_info
        
        return info
    