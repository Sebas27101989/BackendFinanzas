"""Schemas (DTOs) para las entidades financieras (bancos, cajas, financieras)."""
from pydantic import BaseModel, ConfigDict


class EntidadFinancieraBase(BaseModel):
    nombre: str
    tipo_entidad: str
    tasa_base: float | None = None
    estado: str = "Activo"


class EntidadFinancieraCreate(EntidadFinancieraBase):
    pass


class EntidadFinancieraOut(EntidadFinancieraBase):
    model_config = ConfigDict(from_attributes=True)
    id_entidad: int
