"""Router: autenticación (login/registro) — pantalla de acceso del sistema."""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_service, get_current_usuario
from app.models.usuario import Usuario
from app.schemas.usuario import Token, UsuarioLogin, UsuarioOut, UsuarioRegistro
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/registro", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def registrar(datos: UsuarioRegistro, auth_service: Annotated[AuthService, Depends(get_auth_service)]):
    """Crea un usuario nuevo (rol 'cliente' por defecto) junto con su perfil de cliente."""
    usuario = auth_service.registrar(datos)
    return usuario


@router.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """Compatible con el formulario estándar OAuth2 (username + password),
    usado también por la documentación interactiva /docs."""
    return auth_service.autenticar(UsuarioLogin(username=form_data.username, password=form_data.password))


@router.get("/yo", response_model=UsuarioOut)
def leer_usuario_actual(usuario_actual: Annotated[Usuario, Depends(get_current_usuario)]):
    """Devuelve los datos del usuario dueño del token JWT enviado."""
    return usuario_actual
