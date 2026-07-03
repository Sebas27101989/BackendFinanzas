"""
Modelo ORM: Vehiculo

Campos tomados de la tabla "Datos del vehículo" (sección 5.1.1 del informe):
Marca, Modelo, Año, Precio del vehículo, Tipo de moneda, Estado
(Nuevo/Seminuevo/Antiguo).
"""
from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Vehiculo(Base):
    __tablename__ = "vehiculos"

    id_vehiculo: Mapped[int] = mapped_column(primary_key=True, index=True)
    marca: Mapped[str] = mapped_column(String(50), nullable=False)
    modelo: Mapped[str] = mapped_column(String(50), nullable=False)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    precio: Mapped[float] = mapped_column(Float, nullable=False)
    moneda: Mapped[str] = mapped_column(String(3), default="PEN", nullable=False)  # PEN | USD
    estado: Mapped[str] = mapped_column(String(20), default="Nuevo", nullable=False)  # Nuevo | Seminuevo | Antiguo

    creditos: Mapped[list["CreditoVehicular"]] = relationship(back_populates="vehiculo")
