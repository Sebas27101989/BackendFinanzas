"""
Modelo ORM: IndicadorFinanciero

Guarda, en relación 1-a-1 con CreditoVehicular, los indicadores exigidos por
las normas de transparencia del sistema financiero peruano (sección 4.1.4 y
6.10-6.11 del informe): VAN, TIR y TCEA, además de los totales agregados
usados para exponerlos rápidamente en el dashboard/reportes.
"""
from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class IndicadorFinanciero(Base):
    __tablename__ = "indicadores_financieros"

    id_indicador: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_credito: Mapped[int] = mapped_column(
        ForeignKey("creditos_vehiculares.id_credito"), unique=True, nullable=False
    )

    van: Mapped[float] = mapped_column(Float, nullable=False)
    tir_mensual: Mapped[float] = mapped_column(Float, nullable=False)
    tcea: Mapped[float] = mapped_column(Float, nullable=False)

    total_pagado: Mapped[float] = mapped_column(Float, nullable=False)
    total_intereses: Mapped[float] = mapped_column(Float, nullable=False)
    costos_adicionales: Mapped[float] = mapped_column(Float, nullable=False)
    cuota_balon_monto: Mapped[float] = mapped_column(Float, default=0.0)

    credito: Mapped["CreditoVehicular"] = relationship(back_populates="indicador_financiero")
