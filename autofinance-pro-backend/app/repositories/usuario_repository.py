from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.repositories.base_repository import BaseRepository


class UsuarioRepository(BaseRepository[Usuario]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Usuario)

    def obtener_por_username(self, username: str) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.username == username).first()
