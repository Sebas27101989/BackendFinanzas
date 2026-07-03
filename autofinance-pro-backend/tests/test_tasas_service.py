"""Pruebas del servicio de conversión de tasas (sección 6.2 del informe)."""
import pytest

from app.services.tasas_service import obtener_tasa_efectiva_mensual, tna_a_tea


def test_tea_efectiva_directa_se_convierte_a_mensual():
    # TEA 10.7% -> tasa mensual esperada ~0.8507% (validado contra Caso de Prueba 1)
    tasa_mensual = obtener_tasa_efectiva_mensual("Efectiva", 10.7, None)
    assert tasa_mensual == pytest.approx(0.0085071, rel=1e-3)


def test_tna_a_tea_con_capitalizacion_mensual():
    # TNA 12% capitalización mensual -> TEA = (1+0.12/12)^12 - 1 ≈ 12.6825%
    tea = tna_a_tea(12, "Mensual")
    assert tea == pytest.approx(0.126825, rel=1e-4)


def test_tasa_nominal_requiere_frecuencia_capitalizacion():
    with pytest.raises(ValueError):
        obtener_tasa_efectiva_mensual("Nominal", 12, None)
