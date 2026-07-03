"""
Infraestructura de acceso a datos: engine, sesión y clase base declarativa.

Esta es la única capa que conoce SQLAlchemy "a bajo nivel". El resto de la
aplicación (repositorios, servicios) recibe una `Session` inyectada y nunca
crea conexiones por su cuenta, lo que permite cambiar de motor de base de
datos (SQLite -> PostgreSQL, por ejemplo) sin tocar la lógica de negocio.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Clase base declarativa de la que heredan todos los modelos ORM."""
    pass


def get_db():
    """Generador de sesión de BD para inyección de dependencias de FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Crea todas las tablas registradas en `Base.metadata`.

    En un entorno productivo esto se reemplaza por migraciones versionadas
    (Alembic); se deja aquí como utilidad de arranque rápido para desarrollo
    y para los entornos de pruebas automatizadas.
    """
    from app import models  # noqa: F401  (registra los modelos en Base.metadata)
    Base.metadata.create_all(bind=engine)
