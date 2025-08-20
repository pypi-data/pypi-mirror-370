import os
from typing import List, Union, Optional, Literal, Dict
from pathlib import Path

from tai_sql import pm
from ..base import BaseGenerator
from .sync import SyncCRUDGenerator
from .asyn import AsyncCRUDGenerator
from ..models import ModelsGenerator

class CRUDGenerator(BaseGenerator):
    """
    Generador de clases CRUD para modelos SQLAlchemy con soporte sync/async.
    """
    
    def __init__(self, 
                 output_dir: Optional[str] = None, 
                 models_import_path: Optional[str] = None,
                 mode: Literal['sync', 'async', 'both'] = 'sync',
                 max_depth: int = 5,
                 logger_name: str = 'tai-sql'):
        """
        Inicializa el generador CRUD.
        
        Args:
            output_dir: Directorio de salida para los archivos CRUD
            models_import_path: Ruta de importación donde están los modelos generados
            mode: Modo de generación ('sync', 'async', 'both')
        """
        super().__init__(output_dir)
        self._models_import_path = models_import_path
        self.mode = mode
        self.max_depth = max_depth
        self.logger_name = logger_name
    
    @property
    def models_generator(self) -> ModelsGenerator:
        """
        Obtiene el generador de modelos configurado en la base de datos.
        
        Returns:
            Instancia de ModelsGenerator
        """
        for generator in pm.db.generators:
            if isinstance(generator, ModelsGenerator):
                return generator
        raise ValueError("No se encontró un generador de modelos configurado.")
    
    @property
    def models_import_path(self) -> str:
        """
        Resuelve automáticamente el import path basándose en ModelsGenerator
        o usa el valor proporcionado manualmente
        """
        if self._models_import_path:
            # Si se proporcionó manualmente, usarlo
            return self._models_import_path
        
        # Construir el import path basándose en el output_dir del ModelsGenerator
        output_dir = self.models_generator.file_path

        output_dir = os.path.sep.join(output_dir.parts[1:])  # Eliminar el primer segmento (raíz del proyecto)
        import_path = output_dir.replace('/', '.').replace('\\', '.')
        
        # Remover puntos al inicio/final si existen
        import_path = import_path.strip('.')
        
        return import_path
    
    @property
    def sync_generator(self) -> SyncCRUDGenerator:
        output_dir = os.path.join(self.config.output_dir, pm.db.schema_name, 'crud', 'syn')
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        return SyncCRUDGenerator(
            output_dir=output_dir,
            models_import_path=self.models_import_path,
            max_depth=self.max_depth,
            logger_name=self.logger_name
        )
    
    @property
    def async_generator(self) -> AsyncCRUDGenerator:
        output_dir = os.path.join(self.config.output_dir, pm.db.schema_name, 'crud', 'asyn')
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        return AsyncCRUDGenerator(
            output_dir=output_dir,
            models_import_path=self.models_import_path,
            max_depth=self.max_depth,
            logger_name=self.logger_name
        )
    
    def generate(self) -> Union[tuple[str, str], str]:
        """
        Genera las clases CRUD según el modo especificado.
        
        Returns:
            Ruta al directorio generado
        """
        if self.validate_configuration():
            if self.mode in ['sync', 'both']:
                sync_result = self.sync_generator.generate()
            
            if self.mode in ['async', 'both']:
                async_result = self.async_generator.generate()
            
            if self.mode == 'both':
                return sync_result, async_result
            
            elif self.mode == 'sync':
                return sync_result
            
            elif self.mode == 'async':
                return async_result
    
    def validate_configuration(self) -> bool:
        """
        Valida que la configuración del generador sea correcta
        
        Returns:
            True si la configuración es válida
            
        Raises:
            ValueError: Si la configuración es inválida
        """
        if not pm.db.provider:
            raise ValueError("No se ha configurado un provider. Usa datasource() primero.")
        
        if not pm.db.provider.source_input_type:
            raise ValueError("El provider no tiene source_input_type configurado.")
        
        if self.mode not in ['sync', 'async', 'both']:
            raise ValueError(f"Modo no válido: {self.mode}. Debe ser 'sync', 'async' o 'both'.")
        
        if not self.models:
            raise ValueError("No se encontraron modelos para generar CRUDs.")
        
        return True
    
    def __str__(self) -> str:
        return f"CRUDGenerator(mode={self.mode}, output_dir={self.config.output_dir})"
    
    def __repr__(self) -> str:
        return self.__str__()