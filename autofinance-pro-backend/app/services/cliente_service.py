"""Servicio de dominio: gestión de clientes (pantalla "Gestión de Clientes")."""
from app.models.cliente import Cliente
from app.repositories.cliente_repository import ClienteRepository
from app.schemas.cliente import ClienteCreate, ClienteUpdate
from app.utils.exceptions import RecursoDuplicadoError, RecursoNoEncontradoError


class ClienteService:
    def __init__(self, repo: ClienteRepository) -> None:
        self.repo = repo

    def crear(self, datos: ClienteCreate) -> Cliente:
        if self.repo.obtener_por_dni(datos.dni):
            raise RecursoDuplicadoError(f"Ya existe un cliente con DNI '{datos.dni}'")
        return self.repo.crear(Cliente(**datos.model_dump()))

    def listar(self, skip: int = 0, limit: int = 100) -> list[Cliente]:
        return self.repo.listar(skip, limit)

    def buscar(self, texto: str) -> list[Cliente]:
        return self.repo.buscar(texto)

    def obtener(self, id_cliente: int) -> Cliente:
        cliente = self.repo.obtener_por_id(id_cliente)
        if not cliente:
            raise RecursoNoEncontradoError(f"Cliente {id_cliente} no encontrado")
        return cliente

    def actualizar(self, id_cliente: int, datos: ClienteUpdate) -> Cliente:
        cliente = self.obtener(id_cliente)
        for campo, valor in datos.model_dump(exclude_unset=True).items():
            setattr(cliente, campo, valor)
        return self.repo.actualizar(cliente)

    def eliminar(self, id_cliente: int) -> None:
        cliente = self.obtener(id_cliente)
        self.repo.eliminar(cliente)
