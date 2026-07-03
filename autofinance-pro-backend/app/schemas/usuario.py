"""Schemas (DTOs) para autenticación y gestión de usuarios."""
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioRegistro(BaseModel):
    """Datos requeridos por la pantalla de 'Registrarse' (sección 5.1.2)."""
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    nombre: str
    apellidos: str
    dni: str = Field(min_length=8, max_length=8)
    telefono: str | None = None
    correo: EmailStr | None = None
    direccion: str | None = None
    ingresos_mensuales: float = Field(ge=0)


class UsuarioLogin(BaseModel):
    username: str
    password: str


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_usuario: int
    username: str
    rol: str
    estado: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
