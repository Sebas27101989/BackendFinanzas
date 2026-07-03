"""Schemas (DTOs) para el catálogo de vehículos financiables (sección 5.1.2)."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Moneda = Literal["PEN", "USD"]
EstadoVehiculo = Literal["Nuevo", "Seminuevo", "Antiguo"]


class VehiculoBase(BaseModel):
    marca: str
    modelo: str
    anio: int = Field(ge=1980, le=2100)
    precio: float = Field(gt=0)
    moneda: Moneda = "PEN"
    estado: EstadoVehiculo = "Nuevo"


class VehiculoCreate(VehiculoBase):
    pass


class VehiculoUpdate(BaseModel):
    marca: str | None = None
    modelo: str | None = None
    anio: int | None = None
    precio: float | None = Field(default=None, gt=0)
    moneda: Moneda | None = None
    estado: EstadoVehiculo | None = None


class VehiculoOut(VehiculoBase):
    model_config = ConfigDict(from_attributes=True)
    id_vehiculo: int
