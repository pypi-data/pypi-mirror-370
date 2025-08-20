"""
Utilidades para interactuar con la API de GitHub
"""
from dataclasses import dataclass

@dataclass
class RepositoryInfo:
    """Información del repositorio Git"""
    owner: str
    repo: str
    
    @property
    def full_name(self) -> str:
        """Nombre completo del repositorio (owner/repo)"""
        return f"{self.owner}/{self.repo}"

