"""
Modelo ORM: Cliente

Campos tomados directamente de la tabla "Datos del cliente" (sección 5.1.1
del informe): Nombre, Apellidos, DNI, Teléfono, Correo, Ingresos Mensuales,
Dirección.
"""
from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id_cliente: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(100), nullable=False)
    dni: Mapped[str] = mapped_column(String(8), unique=True, index=True, nullable=False)
    telefono: Mapped[str] = mapped_column(String(20), nullable=True)
    correo: Mapped[str] = mapped_column(String(120), nullable=True)
    direccion: Mapped[str] = mapped_column(String(200), nullable=True)
    ingresos_mensuales: Mapped[float] = mapped_column(Float, nullable=False)

    # Un cliente puede (opcionalmente) tener una cuenta de acceso propia.
    id_usuario: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id_usuario"), nullable=True)

    usuario: Mapped["Usuario"] = relationship(back_populates="cliente")
    creditos: Mapped[list["CreditoVehicular"]] = relationship(back_populates="cliente")
