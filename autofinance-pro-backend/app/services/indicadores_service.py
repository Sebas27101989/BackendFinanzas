"""
Servicio de indicadores financieros: VAN, TIR y TCEA
(secciones 3.11, 4.1.4, 6.10 y 6.11 del informe).

Trabaja exclusivamente sobre un "flujo financiero" (sección 6.9): una lista
de montos por periodo, donde el periodo 0 es el desembolso (monto
financiado, flujo positivo desde la óptica del cliente que lo recibe) y los
periodos 1..n son las salidas de caja (cuotas totales, incluyendo seguros).
"""
import math

from app.services.tasas_service import tea_desde_tep_mensual


def calcular_van(flujos: list[float], tasa_periodica: float) -> float:
    """VAN = -I0 + sum( Ft / (1+k)^t ), t = 1..n  (fórmula sección 6.10).

    `flujos[0]` se interpreta como I0 con su propio signo (normalmente
    negativo si se evalúa desde la óptica del prestamista, o positivo si se
    evalúa desde la óptica del cliente que recibe el desembolso).
    """
    van = 0.0
    for t, flujo in enumerate(flujos):
        van += flujo / (1 + tasa_periodica) ** t
    return van


def calcular_tir(flujos: list[float], estimado_inicial: float = 0.05, tolerancia: float = 1e-9, max_iter: int = 500) -> float | None:
    """TIR = tasa que hace VAN = 0 (fórmula sección 6.11), resuelta por
    Newton-Raphson con reintento por bisección si no converge (evita
    depender de librerías externas como numpy-financial).
    """
    tasa = estimado_inicial
    for _ in range(max_iter):
        van = calcular_van(flujos, tasa)
        derivada = sum(-t * flujo / (1 + tasa) ** (t + 1) for t, flujo in enumerate(flujos) if t > 0)
        if abs(derivada) < 1e-12:
            break
        nueva_tasa = tasa - van / derivada
        if nueva_tasa <= -0.9999:
            nueva_tasa = (tasa - 0.9999) / 2  # evita (1+tasa) <= 0
        if abs(nueva_tasa - tasa) < tolerancia:
            return nueva_tasa
        tasa = nueva_tasa

    return _tir_por_biseccion(flujos)


def _tir_por_biseccion(flujos: list[float], low: float = -0.9, high: float = 5.0, tolerancia: float = 1e-7, max_iter: int = 200) -> float | None:
    van_low = calcular_van(flujos, low)
    van_high = calcular_van(flujos, high)
    if math.isnan(van_low) or math.isnan(van_high) or van_low * van_high > 0:
        return None  # no hay cambio de signo detectable: no se puede acotar la TIR
    for _ in range(max_iter):
        mid = (low + high) / 2
        van_mid = calcular_van(flujos, mid)
        if abs(van_mid) < tolerancia:
            return mid
        if van_low * van_mid < 0:
            high = mid
        else:
            low, van_low = mid, van_mid
    return (low + high) / 2


def construir_flujo_financiero(monto_financiado: float, cronograma_totales: list[float]) -> list[float]:
    """Sección 6.9: flujo = desembolso inicial (positivo) seguido de las
    salidas de caja (cuotas totales, negativas) en cada periodo.
    """
    return [monto_financiado] + [-total for total in cronograma_totales]


def calcular_indicadores(
    monto_financiado: float,
    cronograma_totales: list[float],
    tasa_descuento_anual: float,
) -> dict:
    """Calcula VAN (con la tasa de descuento/COK anual convertida a mensual),
    TIR mensual, TIR/TCEA anualizada, a partir del flujo financiero completo.
    """
    flujo = construir_flujo_financiero(monto_financiado, cronograma_totales)

    tasa_descuento_mensual = (1 + tasa_descuento_anual) ** (1 / 12) - 1
    # VAN evaluado desde la óptica del prestamista: invierte monto_financiado
    # y recibe las cuotas; se invierte el signo del flujo construido arriba.
    flujo_prestamista = [-f for f in flujo]
    van = calcular_van(flujo_prestamista, tasa_descuento_mensual)

    tir_mensual = calcular_tir(flujo_prestamista, estimado_inicial=0.02)
    tir_anual = tea_desde_tep_mensual(tir_mensual) if tir_mensual is not None else None

    # La TCEA es, por definición regulatoria (Res. SBS 8181-2012), la TIR
    # anualizada del flujo real de pagos (incluye seguros y cargos).
    tcea = tir_anual

    return {
        "van": round(van, 2),
        "tir_mensual": round(tir_mensual, 6) if tir_mensual is not None else None,
        "tir_anual": round(tir_anual, 6) if tir_anual is not None else None,
        "tcea": round(tcea, 6) if tcea is not None else None,
    }
