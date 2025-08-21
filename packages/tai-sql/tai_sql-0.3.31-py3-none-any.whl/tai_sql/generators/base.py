import os
from abc import ABC, abstractmethod
from typing import List, Optional, ClassVar, Union

# Obtener modelos del registro centralizado
import tai_sql
from tai_sql import pm, Table, View, Enum

class BaseGenerator(ABC):
    """
    Clase base abstracta para todos los generadores de tai-sql.
    
    Todos los generadores deben heredar de esta clase e implementar
    el método `generate` para mantener una interfaz común.
    """

    _models: ClassVar[List[Union[Table, View]]] = []  # Atributo de clase privado
    _enums: ClassVar[List[Enum]] = []  # Atributo de clase privado para enumeraciones
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Inicializa el generador.
        
        Args:
            output_dir: Directorio de salida para los archivos generados.
                        Si es None, se usará un directorio por defecto.
        """
        self.config = GeneratorConfig(output_dir)
    
    @classmethod
    def register_model(cls, model: Union[Table, View]) -> None:
        """
        Registra un modelo para ser procesado por el generador.
        
        Args:
            model: Clase del modelo a registrar
        """
        if model not in cls._models:
            cls._models.append(model)
    
    @classmethod
    def register_models(cls, *models: Union[Table, View]) -> None:
        """
        Registra múltiples modelos para ser procesados por el generador.
        
        Args:
            *models: Clases de modelos a registrar
        """
        for model in models:
            cls.register_model(model)
    
    @classmethod
    def clear_models(cls) -> None:
        """
        Limpia la lista de modelos registrados.
        Útil para testing o para reiniciar el estado.
        """
        cls._models.clear()
    
    @property
    def models(self) -> List[Union[Table, View]]:
        """
        Retorna la lista de modelos registrados.
        Si no hay modelos registrados, intenta descubrir los modelos automáticamente.
        
        Returns:
            Lista de modelos registrados
        """
        if not self._models:
            models = pm.db.tables + pm.db.views
            self.register_models(*models)

        return self._models
    
    @property
    def enums(self) -> List[Enum]:
        """
        Retorna la lista de enumeraciones registradas.
        Si no hay enumeraciones registradas, las obtiene del registro centralizado.
        
        Returns:
            Lista de enumeraciones registradas
        """
        if not self._enums:
            self._enums = pm.db.enums
        return self._enums
    
    @abstractmethod
    def generate(self) -> Optional[str]:
        """
        Genera recursos basados en los modelos registrados.
        
        Este método debe ser implementado por todas las subclases.
        
        Returns:
            El resultado de la generación, específico de cada generador
        """
        pass

class GeneratorConfig:
    """
    Configuración para los generadores.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Inicializa la configuración del generador.
        
        Args:
            output_dir: Directorio de salida para los archivos generados
        """
        # Configurar el directorio de salida
        if output_dir is None:
            # Obtener el directorio de instalación del paquete
            output_dir = os.path.dirname(os.path.abspath(tai_sql.__file__))
            output_dir = os.path.join(output_dir, 'generated')
        
        # Crear el directorio si no existe
        os.makedirs(output_dir, exist_ok=True)

        self.output_dir = output_dir