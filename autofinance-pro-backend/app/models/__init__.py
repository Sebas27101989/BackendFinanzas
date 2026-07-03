"""
Punto único de importación de todos los modelos ORM.

Importar este paquete garantiza que las 7 entidades del diagrama de base de
datos del informe (sección 9) queden registradas en `Base.metadata` antes de
llamar a `Base.metadata.create_all()`.
"""
from app.models.usuario import Usuario
from app.models.cliente import Cliente
from app.models.vehiculo import Vehiculo
from app.models.entidad_financiera import EntidadFinanciera
from app.models.credito_vehicular import CreditoVehicular
from app.models.cuota import Cuota
from app.models.indicador_financiero import IndicadorFinanciero

__all__ = [
    "Usuario",
    "Cliente",
    "Vehiculo",
    "EntidadFinanciera",
    "CreditoVehicular",
    "Cuota",
    "IndicadorFinanciero",
]
