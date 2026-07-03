"""
Modelo ORM: CreditoVehicular

Entidad central del dominio. Agrupa los "Datos de crédito vehicular" de la
sección 5.1.1 del informe (cuota inicial, monto financiado, TEA/TNA, tipo de
tasa, capitalización, plazo, periodo de gracia y cuota balón) y sirve como
raíz de agregación para el cronograma (Cuota) y los indicadores financieros.
"""
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CreditoVehicular(Base):
    __tablename__ = "creditos_vehiculares"

    id_credito: Mapped[int] = mapped_column(primary_key=True, index=True)

    # --- Relaciones ------------------------------------------------------
    id_cliente: Mapped[int] = mapped_column(ForeignKey("clientes.id_cliente"), nullable=False)
    id_vehiculo: Mapped[int] = mapped_column(ForeignKey("vehiculos.id_vehiculo"), nullable=False)
    id_entidad: Mapped[int] = mapped_column(ForeignKey("entidades_financieras.id_entidad"), nullable=False)

    # --- Condiciones comerciales ------------------------------------------
    cuota_inicial: Mapped[float] = mapped_column(Float, nullable=False)
    monto_financiado: Mapped[float] = mapped_column(Float, nullable=False)
    tipo_moneda: Mapped[str] = mapped_column(String(3), default="PEN", nullable=False)

    # --- Condiciones de tasa ------------------------------------------------
    tipo_tasa: Mapped[str] = mapped_column(String(20), nullable=False)  # "Nominal" | "Efectiva"
    tasa_interes: Mapped[float] = mapped_column(Float, nullable=False)  # valor porcentual, ej. 10.7
    frecuencia_capitalizacion: Mapped[str | None] = mapped_column(String(20), nullable=True)  # solo si Nominal

    # --- Plazo y periodo de gracia -------------------------------------------
    plazo_meses: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo_gracia: Mapped[str] = mapped_column(String(10), default="Ninguno", nullable=False)  # Ninguno|Total|Parcial
    meses_gracia: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # --- Compra inteligente / cuota balón -----------------------------------
    cuota_balon_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # --- Costos adicionales (sección 6.9 Flujo Financiero) --------------------
    seguro_vehicular_mensual: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    seguro_desgravamen_mensual: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    gastos_administrativos: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    estado: Mapped[str] = mapped_column(String(20), default="Simulado", nullable=False)  # Simulado|Activo|Cancelado

    # --- Relaciones inversas -------------------------------------------------
    cliente: Mapped["Cliente"] = relationship(back_populates="creditos")
    vehiculo: Mapped["Vehiculo"] = relationship(back_populates="creditos")
    entidad_financiera: Mapped["EntidadFinanciera"] = relationship(back_populates="creditos")
    cuotas: Mapped[list["Cuota"]] = relationship(
        back_populates="credito", cascade="all, delete-orphan", order_by="Cuota.numero_cuota"
    )
    indicador_financiero: Mapped["IndicadorFinanciero"] = relationship(
        back_populates="credito", uselist=False, cascade="all, delete-orphan"
    )
