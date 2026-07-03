"""Servicio de dominio: entidades financieras (bancos, cajas, financieras)."""
from app.models.entidad_financiera import EntidadFinanciera
from app.repositories.entidad_repository import EntidadFinancieraRepository
from app.schemas.entidad_financiera import EntidadFinancieraCreate
from app.utils.exceptions import RecursoNoEncontradoError


class EntidadFinancieraService:
    def __init__(self, repo: EntidadFinancieraRepository) -> None:
        self.repo = repo

    def crear(self, datos: EntidadFinancieraCreate) -> EntidadFinanciera:
        return self.repo.crear(EntidadFinanciera(**datos.model_dump()))

    def listar(self, skip: int = 0, limit: int = 100) -> list[EntidadFinanciera]:
        return self.repo.listar(skip, limit)

    def obtener(self, id_entidad: int) -> EntidadFinanciera:
        entidad = self.repo.obtener_por_id(id_entidad)
        if not entidad:
            raise RecursoNoEncontradoError(f"Entidad financiera {id_entidad} no encontrada")
        return entidad
