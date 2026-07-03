"""
Repositorio de CreditoVehicular.

Además del CRUD básico, sabe cómo persistir -en una sola transacción- la
raíz de agregación completa: el crédito, su cronograma (lista de Cuota) y
sus indicadores financieros (IndicadorFinanciero). Mantener esta lógica
aquí (y no en el servicio) respeta el principio de que sólo el repositorio
conoce los detalles de mapeo objeto-relacional.
"""
from sqlalchemy.orm import Session, joinedload

from app.models.credito_vehicular import CreditoVehicular
from app.models.cuota import Cuota
from app.models.indicador_financiero import IndicadorFinanciero
from app.repositories.base_repository import BaseRepository
from app.schemas.credito import CreditoCreate
from app.schemas.simulacion import SimulacionResultado


class CreditoRepository(BaseRepository[CreditoVehicular]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, CreditoVehicular)

    def obtener_por_id(self, id_: int) -> CreditoVehicular | None:
        return (
            self.db.query(CreditoVehicular)
            .options(joinedload(CreditoVehicular.cuotas), joinedload(CreditoVehicular.indicador_financiero))
            .filter(CreditoVehicular.id_credito == id_)
            .first()
        )

    def listar_por_cliente(self, id_cliente: int) -> list[CreditoVehicular]:
        return list(self.db.query(CreditoVehicular).filter(CreditoVehicular.id_cliente == id_cliente).all())

    def crear_credito_con_cronograma(
        self, datos: CreditoCreate, resultado: SimulacionResultado
    ) -> CreditoVehicular:
        credito = CreditoVehicular(
            id_cliente=datos.id_cliente,
            id_vehiculo=datos.id_vehiculo,
            id_entidad=datos.id_entidad,
            cuota_inicial=datos.cuota_inicial,
            monto_financiado=datos.monto_financiado,
            tipo_moneda=datos.moneda,
            tipo_tasa=datos.tipo_tasa,
            tasa_interes=datos.tasa_interes,
            frecuencia_capitalizacion=datos.frecuencia_capitalizacion,
            plazo_meses=datos.plazo_meses,
            tipo_gracia=datos.tipo_gracia,
            meses_gracia=datos.meses_gracia,
            cuota_balon_pct=datos.cuota_balon_pct,
            seguro_vehicular_mensual=datos.seguro_vehicular_mensual,
            seguro_desgravamen_mensual=datos.seguro_desgravamen_mensual,
            gastos_administrativos=datos.gastos_administrativos,
            fecha_inicio=datos.fecha_inicio,
            estado="Activo",
        )
        self.db.add(credito)
        self.db.flush()  # asigna id_credito sin cerrar la transacción

        for fila in resultado.cronograma:
            self.db.add(
                Cuota(
                    id_credito=credito.id_credito,
                    numero_cuota=fila.numero_cuota,
                    fecha_pago=fila.fecha_pago,
                    cuota=fila.cuota,
                    interes=fila.interes,
                    amortizacion=fila.amortizacion,
                    saldo=fila.saldo,
                    seguro_vehicular=fila.seguro_vehicular,
                    seguro_desgravamen=fila.seguro_desgravamen,
                    total=fila.total,
                    es_periodo_gracia=fila.es_periodo_gracia,
                    es_cuota_balon=fila.es_cuota_balon,
                )
            )

        self.db.add(
            IndicadorFinanciero(
                id_credito=credito.id_credito,
                van=resultado.indicadores.van,
                tir_mensual=resultado.indicadores.tir_mensual,
                tcea=resultado.indicadores.tcea,
                total_pagado=resultado.indicadores.total_pagado,
                total_intereses=resultado.indicadores.total_intereses,
                costos_adicionales=resultado.indicadores.costos_adicionales,
                cuota_balon_monto=resultado.indicadores.cuota_balon_monto,
            )
        )

        self.db.commit()
        self.db.refresh(credito)
        return credito
