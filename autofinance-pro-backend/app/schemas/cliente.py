"""Schemas (DTOs) para la gestión de clientes (CRUD, sección 5.1.2)."""
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClienteBase(BaseModel):
    nombre: str
    apellidos: str
    dni: str = Field(min_length=8, max_length=8)
    telefono: str | None = None
    correo: EmailStr | None = None
    direccion: str | None = None
    ingresos_mensuales: float = Field(ge=0)


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nombre: str | None = None
    apellidos: str | None = None
    telefono: str | None = None
    correo: EmailStr | None = None
    direccion: str | None = None
    ingresos_mensuales: float | None = Field(default=None, ge=0)


class ClienteOut(ClienteBase):
    model_config = ConfigDict(from_attributes=True)
    id_cliente: int
