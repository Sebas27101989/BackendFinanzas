from sqlalchemy.orm import Session

from app.models.vehiculo import Vehiculo
from app.repositories.base_repository import BaseRepository


class VehiculoRepository(BaseRepository[Vehiculo]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Vehiculo)

    def buscar(self, texto: str) -> list[Vehiculo]:
        patron = f"%{texto}%"
        return list(
            self.db.query(Vehiculo).filter((Vehiculo.marca.ilike(patron)) | (Vehiculo.modelo.ilike(patron))).all()
        )
