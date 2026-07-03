from sqlalchemy.orm import Session

from app.models.entidad_financiera import EntidadFinanciera
from app.repositories.base_repository import BaseRepository


class EntidadFinancieraRepository(BaseRepository[EntidadFinanciera]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, EntidadFinanciera)
