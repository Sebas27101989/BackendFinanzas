"""
Servicio de autenticación: registro, login y emisión de tokens
(pantallas "Iniciar Sesión" / "Registrarse", sección 5.1.2 y algoritmo
"Inicio", sección 8, del informe).
"""
from app.core.security import create_access_token, hash_password, verify_password
from app.models.cliente import Cliente
from app.models.usuario import Usuario
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import Token, UsuarioLogin, UsuarioRegistro
from app.utils.exceptions import CredencialesInvalidasError, RecursoDuplicadoError


class AuthService:
    def __init__(self, usuario_repo: UsuarioRepository, cliente_repo: ClienteRepository) -> None:
        self.usuario_repo = usuario_repo
        self.cliente_repo = cliente_repo

    def registrar(self, datos: UsuarioRegistro) -> Usuario:
        if self.usuario_repo.obtener_por_username(datos.username):
            raise RecursoDuplicadoError(f"El usuario '{datos.username}' ya existe")
        if self.cliente_repo.obtener_por_dni(datos.dni):
            raise RecursoDuplicadoError(f"Ya existe un cliente registrado con DNI '{datos.dni}'")

        usuario = Usuario(
            username=datos.username,
            password_hash=hash_password(datos.password),
            rol="cliente",
            estado="Activo",
        )
        usuario = self.usuario_repo.crear(usuario)

        cliente = Cliente(
            nombre=datos.nombre,
            apellidos=datos.apellidos,
            dni=datos.dni,
            telefono=datos.telefono,
            correo=datos.correo,
            direccion=datos.direccion,
            ingresos_mensuales=datos.ingresos_mensuales,
            id_usuario=usuario.id_usuario,
        )
        self.cliente_repo.crear(cliente)

        return usuario

    def autenticar(self, datos: UsuarioLogin) -> Token:
        usuario = self.usuario_repo.obtener_por_username(datos.username)
        if not usuario or not verify_password(datos.password, usuario.password_hash):
            raise CredencialesInvalidasError("Usuario o contraseña inválidos")
        if usuario.estado != "Activo":
            raise CredencialesInvalidasError("El usuario se encuentra inactivo")

        token = create_access_token(subject=usuario.username, extra_claims={"rol": usuario.rol})
        return Token(access_token=token)
