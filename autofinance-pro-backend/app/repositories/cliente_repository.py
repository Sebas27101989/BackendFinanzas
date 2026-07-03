from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.repositories.base_repository import BaseRepository


class ClienteRepository(BaseRepository[Cliente]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Cliente)

    def obtener_por_dni(self, dni: str) -> Cliente | None:
        return self.db.query(Cliente).filter(Cliente.dni == dni).first()

    def buscar(self, texto: str) -> list[Cliente]:
        patron = f"%{texto}%"
        return list(
            self.db.query(Cliente)
            .filter(
                (Cliente.nombre.ilike(patron))
                | (Cliente.apellidos.ilike(patron))
                | (Cliente.dni.ilike(patron))
            )
            .all()
        )
