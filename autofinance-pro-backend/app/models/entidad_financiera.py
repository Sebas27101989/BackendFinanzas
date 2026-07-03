"""
Modelo ORM: EntidadFinanciera

Representa al banco, financiera o caja municipal (supervisados por la SBS,
sección 3.1 del informe) que otorga el crédito vehicular.
"""
from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class EntidadFinanciera(Base):
    __tablename__ = "entidades_financieras"

    id_entidad: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo_entidad: Mapped[str] = mapped_column(String(30), nullable=False)  # Banco | Financiera | Caja Municipal
    tasa_base: Mapped[float] = mapped_column(Float, nullable=True)  # tasa de referencia ofrecida
    estado: Mapped[str] = mapped_column(String(20), default="Activo", nullable=False)

    creditos: Mapped[list["CreditoVehicular"]] = relationship(back_populates="entidad_financiera")
