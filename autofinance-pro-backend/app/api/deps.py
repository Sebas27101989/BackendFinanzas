"""
Dependencias compartidas de la capa API.

Aquí se conectan las capas: la sesión de BD (`get_db`) se inyecta en los
repositorios, los repositorios se inyectan en los servicios, y los routers
sólo dependen de los servicios. Ningún router de app/api/v1 instancia un
repositorio directamente ni abre una sesión por su cuenta.
"""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.usuario import Usuario
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.credito_repository import CreditoRepository
from app.repositories.entidad_repository import EntidadFinancieraRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.vehiculo_repository import VehiculoRepository
from app.services.auth_service import AuthService
from app.services.cliente_service import ClienteService
from app.services.credito_service import CreditoService
from app.services.entidad_service import EntidadFinancieraService
from app.services.vehiculo_service import VehiculoService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

DbSession = Annotated[Session, Depends(get_db)]


# --- Repositorios --------------------------------------------------------
def get_usuario_repository(db: DbSession) -> UsuarioRepository:
    return UsuarioRepository(db)


def get_cliente_repository(db: DbSession) -> ClienteRepository:
    return ClienteRepository(db)


def get_vehiculo_repository(db: DbSession) -> VehiculoRepository:
    return VehiculoRepository(db)


def get_entidad_repository(db: DbSession) -> EntidadFinancieraRepository:
    return EntidadFinancieraRepository(db)


def get_credito_repository(db: DbSession) -> CreditoRepository:
    return CreditoRepository(db)


# --- Servicios -------------------------------------------------------------
def get_auth_service(
    usuario_repo: Annotated[UsuarioRepository, Depends(get_usuario_repository)],
    cliente_repo: Annotated[ClienteRepository, Depends(get_cliente_repository)],
) -> AuthService:
    return AuthService(usuario_repo, cliente_repo)


def get_cliente_service(
    repo: Annotated[ClienteRepository, Depends(get_cliente_repository)],
) -> ClienteService:
    return ClienteService(repo)


def get_vehiculo_service(
    repo: Annotated[VehiculoRepository, Depends(get_vehiculo_repository)],
) -> VehiculoService:
    return VehiculoService(repo)


def get_entidad_service(
    repo: Annotated[EntidadFinancieraRepository, Depends(get_entidad_repository)],
) -> EntidadFinancieraService:
    return EntidadFinancieraService(repo)


def get_credito_service(
    repo: Annotated[CreditoRepository, Depends(get_credito_repository)],
) -> CreditoService:
    return CreditoService(repo)


def get_credito_service_sin_repo() -> CreditoService:
    """Variante usada por /simulador: no requiere persistencia ni sesión de BD."""
    return CreditoService(repo=None)


# --- Seguridad: usuario autenticado actual --------------------------------
async def get_current_usuario(
    token: Annotated[str, Depends(oauth2_scheme)],
    usuario_repo: Annotated[UsuarioRepository, Depends(get_usuario_repository)],
) -> Usuario:
    credenciales_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise credenciales_invalidas

    usuario = usuario_repo.obtener_por_username(payload["sub"])
    if usuario is None:
        raise credenciales_invalidas
    return usuario
