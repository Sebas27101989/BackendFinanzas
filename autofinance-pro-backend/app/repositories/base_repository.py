"""
Repositorio genérico (patrón Repository).

Encapsula las operaciones CRUD comunes a todas las entidades para que los
repositorios concretos sólo tengan que declarar consultas específicas de su
dominio (p. ej. "buscar cliente por DNI"). Esta es la única capa que
construye objetos `Query` de SQLAlchemy; los servicios nunca lo hacen
directamente, lo que mantiene la lógica de negocio independiente del ORM.
"""
from typing import Generic, TypeVar

from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, db: Session, model: type[ModelType]) -> None:
        self.db = db
        self.model = model

    def obtener_por_id(self, id_: int) -> ModelType | None:
        return self.db.get(self.model, id_)

    def listar(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        return list(self.db.query(self.model).offset(skip).limit(limit).all())

    def crear(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def actualizar(self, obj: ModelType) -> ModelType:
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def eliminar(self, obj: ModelType) -> None:
        self.db.delete(obj)
        self.db.commit()
