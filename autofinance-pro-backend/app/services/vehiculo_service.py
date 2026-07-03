"""Servicio de dominio: catálogo de vehículos financiables (pantalla "Gestión de Vehículos")."""
from app.models.vehiculo import Vehiculo
from app.repositories.vehiculo_repository import VehiculoRepository
from app.schemas.vehiculo import VehiculoCreate, VehiculoUpdate
from app.utils.exceptions import RecursoNoEncontradoError


class VehiculoService:
    def __init__(self, repo: VehiculoRepository) -> None:
        self.repo = repo

    def crear(self, datos: VehiculoCreate) -> Vehiculo:
        return self.repo.crear(Vehiculo(**datos.model_dump()))

    def listar(self, skip: int = 0, limit: int = 100) -> list[Vehiculo]:
        return self.repo.listar(skip, limit)

    def buscar(self, texto: str) -> list[Vehiculo]:
        return self.repo.buscar(texto)

    def obtener(self, id_vehiculo: int) -> Vehiculo:
        vehiculo = self.repo.obtener_por_id(id_vehiculo)
        if not vehiculo:
            raise RecursoNoEncontradoError(f"Vehículo {id_vehiculo} no encontrado")
        return vehiculo

    def actualizar(self, id_vehiculo: int, datos: VehiculoUpdate) -> Vehiculo:
        vehiculo = self.obtener(id_vehiculo)
        for campo, valor in datos.model_dump(exclude_unset=True).items():
            setattr(vehiculo, campo, valor)
        return self.repo.actualizar(vehiculo)

    def eliminar(self, id_vehiculo: int) -> None:
        vehiculo = self.obtener(id_vehiculo)
        self.repo.eliminar(vehiculo)
