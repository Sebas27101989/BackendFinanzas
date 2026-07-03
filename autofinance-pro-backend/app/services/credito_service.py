"""
Servicio de aplicación: CreditoService.

Es la "fachada" que orquesta los servicios de dominio puros (tasas_service,
amortizacion_service, indicadores_service) para resolver los casos de uso
del negocio: simular un crédito (sin persistir) y registrar un crédito real
(persistiendo cliente/vehículo/entidad ya existentes + su cronograma + sus
indicadores). Aquí es donde vive la "separación de responsabilidades":
este módulo NO sabe cómo se calcula una TIR ni cómo se arma una fila de
amortización -- delega eso en los servicios de dominio -- y tampoco decide
routing HTTP -- eso vive en app/api/.
"""
from app.core.config import settings
from app.repositories.credito_repository import CreditoRepository
from app.schemas.credito import CreditoCreate, CreditoDetalle, CreditoOut
from app.schemas.simulacion import CuotaOut, IndicadoresOut, SimulacionInput, SimulacionResultado
from app.services.amortizacion_service import generar_cronograma
from app.services.indicadores_service import calcular_indicadores
from app.services.tasas_service import obtener_tasa_efectiva_mensual


class CreditoService:
    def __init__(self, repo: CreditoRepository | None = None) -> None:
        self.repo = repo

    # ------------------------------------------------------------------
    # Caso de uso 1: simular (no persiste nada, uso típico del "Simulador
    # de Créditos" de la sección 5.1.2).
    # ------------------------------------------------------------------
    def simular(self, datos: SimulacionInput) -> SimulacionResultado:
        tasa_mensual = obtener_tasa_efectiva_mensual(
            tipo_tasa=datos.tipo_tasa,
            tasa_pct=datos.tasa_interes,
            frecuencia_capitalizacion=datos.frecuencia_capitalizacion,
        )

        resultado = generar_cronograma(
            monto_financiado=datos.monto_financiado,
            tasa_efectiva_mensual=tasa_mensual,
            plazo_meses=datos.plazo_meses,
            tipo_gracia=datos.tipo_gracia,
            meses_gracia=datos.meses_gracia,
            cuota_balon_pct=datos.cuota_balon_pct,
            seguro_vehicular_mensual=datos.seguro_vehicular_mensual,
            seguro_desgravamen_mensual=datos.seguro_desgravamen_mensual,
            fecha_inicio=datos.fecha_inicio,
        )

        totales = [c.total for c in resultado.cronograma]
        total_pagado = round(sum(totales), 2)
        total_intereses = round(sum(c.interes for c in resultado.cronograma), 2)
        costos_adicionales = round(
            sum(c.seguro_vehicular + c.seguro_desgravamen for c in resultado.cronograma)
            + datos.gastos_administrativos,
            2,
        )

        tasa_descuento = (
            datos.tasa_descuento_van
            if datos.tasa_descuento_van is not None
            else settings.TASA_DESCUENTO_DEFECTO
        )
        indicadores_calc = calcular_indicadores(
            monto_financiado=datos.monto_financiado,
            cronograma_totales=totales,
            tasa_descuento_anual=tasa_descuento,
        )

        indicadores = IndicadoresOut(
            monto_financiado=datos.monto_financiado,
            cuota_regular=resultado.cuota_regular,
            cuota_balon_monto=resultado.cuota_balon_monto,
            total_pagado=total_pagado,
            total_intereses=total_intereses,
            costos_adicionales=costos_adicionales,
            van=indicadores_calc["van"],
            tir_mensual=indicadores_calc["tir_mensual"] or 0.0,
            tir_anual=indicadores_calc["tir_anual"] or 0.0,
            tcea=indicadores_calc["tcea"] or 0.0,
        )

        cronograma_out = [CuotaOut(**vars(c)) for c in resultado.cronograma]
        return SimulacionResultado(cronograma=cronograma_out, indicadores=indicadores)

    # ------------------------------------------------------------------
    # Caso de uso 2: registrar el crédito (simula + persiste), sección 8
    # del algoritmo: "Guardar operación dentro de la base de datos".
    # ------------------------------------------------------------------
    def registrar_credito(self, datos: CreditoCreate) -> CreditoDetalle:
        if self.repo is None:
            raise RuntimeError("CreditoService requiere un CreditoRepository para persistir")

        resultado_simulacion = self.simular(datos)
        credito_db = self.repo.crear_credito_con_cronograma(datos, resultado_simulacion)

        return CreditoDetalle(
            credito=CreditoOut.model_validate(credito_db),
            cronograma=resultado_simulacion.cronograma,
            indicadores=resultado_simulacion.indicadores,
        )

    def obtener_detalle(self, id_credito: int) -> CreditoDetalle | None:
        if self.repo is None:
            raise RuntimeError("CreditoService requiere un CreditoRepository para consultar")
        credito_db = self.repo.obtener_por_id(id_credito)
        if credito_db is None:
            return None

        cronograma_out = [
            CuotaOut(
                numero_cuota=c.numero_cuota,
                fecha_pago=c.fecha_pago,
                cuota=c.cuota,
                interes=c.interes,
                amortizacion=c.amortizacion,
                saldo=c.saldo,
                seguro_vehicular=c.seguro_vehicular,
                seguro_desgravamen=c.seguro_desgravamen,
                total=c.total,
                es_periodo_gracia=c.es_periodo_gracia,
                es_cuota_balon=c.es_cuota_balon,
            )
            for c in credito_db.cuotas
        ]
        ind = credito_db.indicador_financiero
        indicadores_out = IndicadoresOut(
            monto_financiado=credito_db.monto_financiado,
            cuota_regular=next((c.cuota for c in credito_db.cuotas if not c.es_periodo_gracia), 0.0),
            cuota_balon_monto=ind.cuota_balon_monto if ind else 0.0,
            total_pagado=ind.total_pagado if ind else 0.0,
            total_intereses=ind.total_intereses if ind else 0.0,
            costos_adicionales=ind.costos_adicionales if ind else 0.0,
            van=ind.van if ind else 0.0,
            tir_mensual=ind.tir_mensual if ind else 0.0,
            tir_anual=0.0,
            tcea=ind.tcea if ind else 0.0,
        )
        return CreditoDetalle(
            credito=CreditoOut.model_validate(credito_db),
            cronograma=cronograma_out,
            indicadores=indicadores_out,
        )
