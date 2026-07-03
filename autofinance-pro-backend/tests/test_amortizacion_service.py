"""
Pruebas del motor de amortización, validadas contra los 3 Casos de Prueba
documentados en la sección 7 del informe original ("Trabajo Parcial —
Finanzas e Ingeniería Económica"): crédito estándar, gracia parcial y
gracia total. Las tolerancias son pequeñas (±0.5 soles / ±0.01%) para
absorber redondeos de la tasa de interés reportada en las capturas del
informe.
"""
from datetime import date

import pytest

from app.services.amortizacion_service import generar_cronograma
from app.services.tasas_service import obtener_tasa_efectiva_mensual


def test_caso_1_credito_estandar_toyota_corolla():
    """Caso de Prueba 1: monto financiado S/68,000, TEA 10.7%, 60 meses,
    sin gracia, cuota balón 25%."""
    tasa_mensual = obtener_tasa_efectiva_mensual("Efectiva", 10.7, None)

    resultado = generar_cronograma(
        monto_financiado=68000,
        tasa_efectiva_mensual=tasa_mensual,
        plazo_meses=60,
        tipo_gracia="Ninguno",
        meses_gracia=0,
        cuota_balon_pct=25,
        seguro_vehicular_mensual=150,
        seguro_desgravamen_mensual=45,
        fecha_inicio=date(2026, 5, 14),
    )

    primera_cuota = resultado.cronograma[0]

    assert resultado.cuota_regular == pytest.approx(1088.84, abs=1.0)
    assert primera_cuota.interes == pytest.approx(578.48, abs=1.0)
    assert primera_cuota.amortizacion == pytest.approx(510.36, abs=1.0)
    assert primera_cuota.saldo == pytest.approx(67489.64, abs=1.0)
    assert len(resultado.cronograma) == 60
    # La última cuota liquida el saldo (cuota balón real)
    assert resultado.cronograma[-1].es_cuota_balon is True
    assert resultado.cronograma[-1].saldo == pytest.approx(0.0, abs=0.01)


def test_caso_2_credito_con_gracia_parcial_honda_civic():
    """Caso de Prueba 2: monto financiado S/102,000, TEA 11.8%, 72 meses,
    gracia PARCIAL de 3 meses, cuota balón 30%."""
    tasa_mensual = obtener_tasa_efectiva_mensual("Efectiva", 11.8, None)

    resultado = generar_cronograma(
        monto_financiado=102000,
        tasa_efectiva_mensual=tasa_mensual,
        plazo_meses=72,
        tipo_gracia="Parcial",
        meses_gracia=3,
        cuota_balon_pct=30,
        seguro_vehicular_mensual=150,
        seguro_desgravamen_mensual=45,
        fecha_inicio=date(2026, 5, 15),
    )

    cuotas_gracia = resultado.cronograma[:3]
    for cuota in cuotas_gracia:
        assert cuota.es_periodo_gracia is True
        assert cuota.amortizacion == pytest.approx(0.0, abs=0.01)
        assert cuota.saldo == pytest.approx(102000, abs=0.5)  # saldo constante en gracia parcial
        assert cuota.interes == pytest.approx(952.52, abs=1.0)
        assert cuota.cuota == pytest.approx(952.52, abs=1.0)  # sólo paga interés

    primera_cuota_regular = resultado.cronograma[3]
    assert primera_cuota_regular.es_periodo_gracia is False
    assert primera_cuota_regular.interes == pytest.approx(952.52, abs=1.0)
    assert primera_cuota_regular.amortizacion == pytest.approx(455.86, abs=1.0)
    assert primera_cuota_regular.cuota == pytest.approx(1408.38, abs=1.0)

    assert len(resultado.cronograma) == 72
    assert resultado.cronograma[-1].saldo == pytest.approx(0.0, abs=0.01)


def test_caso_3_credito_con_gracia_total_capitaliza_intereses():
    """Caso de Prueba 3: monto financiado S/24,000, TNA 12% capitalización
    mensual, 48 meses, gracia TOTAL de 2 meses, cuota balón 20%. Durante la
    gracia total el saldo debe crecer por capitalización de intereses."""
    tasa_mensual = obtener_tasa_efectiva_mensual("Nominal", 12, "Mensual")

    resultado = generar_cronograma(
        monto_financiado=24000,
        tasa_efectiva_mensual=tasa_mensual,
        plazo_meses=48,
        tipo_gracia="Total",
        meses_gracia=2,
        cuota_balon_pct=20,
        seguro_vehicular_mensual=150,
        seguro_desgravamen_mensual=45,
        fecha_inicio=date(2026, 5, 15),
    )

    mes1, mes2 = resultado.cronograma[0], resultado.cronograma[1]
    assert mes1.cuota == 0.0
    assert mes1.amortizacion == 0.0
    assert mes1.saldo > 24000  # el interés se capitaliza: el saldo crece
    assert mes2.saldo > mes1.saldo  # sigue creciendo en el segundo mes de gracia

    assert len(resultado.cronograma) == 48
    assert resultado.cronograma[-1].saldo == pytest.approx(0.0, abs=0.01)


def test_tasa_cero_reparte_capital_en_partes_iguales():
    resultado = generar_cronograma(
        monto_financiado=12000,
        tasa_efectiva_mensual=0.0,
        plazo_meses=12,
        tipo_gracia="Ninguno",
        meses_gracia=0,
        cuota_balon_pct=0,
        seguro_vehicular_mensual=0,
        seguro_desgravamen_mensual=0,
        fecha_inicio=date(2026, 1, 1),
    )
    assert resultado.cuota_regular == pytest.approx(1000.0, abs=0.01)
    assert resultado.cronograma[-1].saldo == pytest.approx(0.0, abs=0.01)
