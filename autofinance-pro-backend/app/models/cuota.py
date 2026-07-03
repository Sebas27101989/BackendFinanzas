"""
Modelo ORM: Cuota

Cada fila de la tabla de amortización (cronograma de pagos, sección 5.1.1
"Datos de Salida" y sección 6.1 "Método Francés de Amortización" del
informe). Es obligatoria su persistencia según la Resolución SBS N.°
8181-2012 citada en el marco legal.
"""
from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Cuota(Base):
    __tablename__ = "cuotas"

    id_cuota: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_credito: Mapped[int] = mapped_column(ForeignKey("creditos_vehiculares.id_credito"), nullable=False)

    numero_cuota: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_pago: Mapped[date] = mapped_column(Date, nullable=False)

    cuota: Mapped[float] = mapped_column(Float, nullable=False)          # capital + interés (+ balón si aplica)
    interes: Mapped[float] = mapped_column(Float, nullable=False)
    amortizacion: Mapped[float] = mapped_column(Float, nullable=False)
    saldo: Mapped[float] = mapped_column(Float, nullable=False)

    seguro_vehicular: Mapped[float] = mapped_column(Float, default=0.0)
    seguro_desgravamen: Mapped[float] = mapped_column(Float, default=0.0)
    total: Mapped[float] = mapped_column(Float, nullable=False)          # cuota + seguros

    es_periodo_gracia: Mapped[bool] = mapped_column(Boolean, default=False)
    es_cuota_balon: Mapped[bool] = mapped_column(Boolean, default=False)
    estado_pago: Mapped[str] = mapped_column(String(15), default="Pendiente")  # Pendiente | Pagado

    credito: Mapped["CreditoVehicular"] = relationship(back_populates="cuotas")
