"""
Auto-importar todos los drivers disponibles
"""
from .base import DatabaseDriver, drivers

# Función de conveniencia
def get_driver(driver_name: str) -> DatabaseDriver:
    """Obtiene un driver por nombre"""
    return drivers.get_or_raise(driver_name)

def list_supported_drivers() -> list[str]:
    """Lista todos los drivers soportados"""
    return drivers.list_available()

__all__ = ['DatabaseDriver', 'drivers', 'get_driver', 'list_supported_drivers']