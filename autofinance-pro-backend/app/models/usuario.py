"""
Modelo ORM: Usuario

Representa la cuenta de acceso al sistema (login/registro, sección 5.1.2 del
informe). Un Usuario puede estar asociado a un Cliente (perfil de negocio)
o representar a un colaborador interno de la entidad financiera (rol
"administrador" / "analista").
"""
from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(20), default="cliente", nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="Activo", nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    cliente: Mapped["Cliente"] = relationship(back_populates="usuario", uselist=False)
