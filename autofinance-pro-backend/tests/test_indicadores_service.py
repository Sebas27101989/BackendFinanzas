"""Pruebas de VAN/TIR (sección 6.10 y 6.11 del informe)."""
import pytest

from app.services.indicadores_service import calcular_tir, calcular_van


def test_van_es_cero_cuando_se_descuenta_a_la_propia_tir():
    flujos = [-1000, 300, 300, 300, 300]
    tir = calcular_tir(flujos, estimado_inicial=0.05)
    assert tir is not None
    van_en_tir = calcular_van(flujos, tir)
    assert van_en_tir == pytest.approx(0.0, abs=1e-4)


def test_van_positivo_con_tasa_de_descuento_baja():
    flujos = [-1000, 400, 400, 400, 400]
    van = calcular_van(flujos, 0.05)
    assert van > 0


def test_tir_de_un_prestamo_simple_coincide_con_la_tasa_pactada():
    # Préstamo de 1000 a 1 periodo con tasa 10%: se recibe 1000, se paga 1100
    flujos = [-1000, 1100]
    tir = calcular_tir(flujos, estimado_inicial=0.05)
    assert tir == pytest.approx(0.10, abs=1e-4)
