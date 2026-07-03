"""Schemas (DTOs) para persistir y consultar un Crédito Vehicular completo."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.simulacion import CuotaOut, IndicadoresOut, SimulacionInput


class CreditoCreate(SimulacionInput):
    """Igual que una simulación, pero además referencia cliente/vehículo/entidad
    y queda persistida en la base de datos (deja de ser una simulación
    efímera y pasa a ser una operación real, sección 8 'Guardar operación
    dentro de la base de datos')."""
    id_cliente: int
    id_vehiculo: int
    id_entidad: int


class CreditoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_credito: int
    id_cliente: int
    id_vehiculo: int
    id_entidad: int
    monto_financiado: float
    cuota_inicial: float
    tipo_moneda: str
    tipo_tasa: str
    tasa_interes: float
    plazo_meses: int
    tipo_gracia: str
    meses_gracia: int
    cuota_balon_pct: float
    estado: str
    fecha_registro: datetime


class CreditoDetalle(BaseModel):
    credito: CreditoOut
    cronograma: list[CuotaOut]
    indicadores: IndicadoresOut
