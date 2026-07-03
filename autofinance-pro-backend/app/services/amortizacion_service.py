"""
Motor de amortización — método francés vencido ordinario, periodos de gracia
y modalidad "Compra Inteligente" (cuota balón).

Este módulo es el corazón matemático de AutoFinance Pro (sección 6 del
informe: 6.1 Método Francés, 6.4 Amortización, 6.5-6.7 Periodos de Gracia,
6.8 Compra Inteligente y Cuota Balón). Es puro: no importa SQLAlchemy ni
FastAPI, sólo recibe números y fechas y devuelve estructuras de datos, lo
que lo hace trivial de probar unitariamente (ver tests/test_amortizacion_service.py).

Algoritmo implementado (validado contra los 3 casos de prueba del informe,
sección 7):

1.  Fase de gracia (si aplica), por `meses_gracia` periodos:
      - Gracia Total:   no se cobra cuota; el interés del periodo se
                        capitaliza sobre el saldo (el saldo crece).
      - Gracia Parcial: se cobra únicamente el interés; el saldo se
                        mantiene constante.
2.  Capital amortizable = monto_financiado * (1 - cuota_balon_pct/100).
    Sólo esa porción se amortiza totalmente en `n = plazo_meses -
    meses_gracia` cuotas con la fórmula francesa estándar:

        R = Capital_amortizable * [ i(1+i)^n / ((1+i)^n - 1) ]

    Esta es la cuota fija que paga el cliente mes a mes (más seguros).
3.  El interés de cada cuota regular se sigue calculando sobre el SALDO
    TOTAL pendiente (que incluye la porción "balón" no amortizada), tal
    como en un crédito vehicular con valor futuro garantizado (GMFV):
    la fracción de interés que la cuota fija R no alcanza a cubrir sobre
    el saldo total queda pendiente y se traslada al saldo (por eso la
    cuota balón final resulta mayor al monto_financiado * cuota_balon_pct
    nominal: incorpora el interés compuesto de esa porción durante todo
    el plazo).
4.  En la última cuota se liquida el saldo remanente como "cuota balón":
    el cliente paga la cuota regular R + el saldo pendiente, dejando el
    crédito completamente cancelado.
"""
from dataclasses import dataclass
from datetime import date

from dateutil.relativedelta import relativedelta


@dataclass
class CuotaCalculada:
    numero_cuota: int
    fecha_pago: date
    cuota: float
    interes: float
    amortizacion: float
    saldo: float
    seguro_vehicular: float
    seguro_desgravamen: float
    total: float
    es_periodo_gracia: bool
    es_cuota_balon: bool


@dataclass
class ResultadoAmortizacion:
    cronograma: list[CuotaCalculada]
    cuota_regular: float
    cuota_balon_monto: float


def cuota_francesa(capital: float, tasa_periodica: float, n_periodos: int) -> float:
    """Cuota constante del método francés: R = C * i(1+i)^n / ((1+i)^n - 1).

    Si la tasa es 0 (caso límite), se reparte el capital en partes iguales.
    """
    if n_periodos <= 0:
        raise ValueError("n_periodos debe ser mayor a 0")
    if tasa_periodica == 0:
        return capital / n_periodos
    factor = (1 + tasa_periodica) ** n_periodos
    return capital * (tasa_periodica * factor) / (factor - 1)


def generar_cronograma(
    monto_financiado: float,
    tasa_efectiva_mensual: float,
    plazo_meses: int,
    tipo_gracia: str,
    meses_gracia: int,
    cuota_balon_pct: float,
    seguro_vehicular_mensual: float,
    seguro_desgravamen_mensual: float,
    fecha_inicio: date,
) -> ResultadoAmortizacion:
    i = tasa_efectiva_mensual
    saldo = monto_financiado
    cronograma: list[CuotaCalculada] = []
    fecha = fecha_inicio

    # --- 1. Fase de gracia -------------------------------------------------
    for mes in range(1, meses_gracia + 1):
        interes = saldo * i
        fecha = fecha + relativedelta(months=1)

        if tipo_gracia == "Total":
            amortizacion = 0.0
            cuota = 0.0
            saldo = saldo + interes  # capitalización del interés (sección 6.6)
        elif tipo_gracia == "Parcial":
            amortizacion = 0.0
            cuota = interes  # sólo se paga el interés (sección 6.7)
            # saldo permanece constante
        else:  # pragma: no cover - protegido por SimulacionInput.validar_consistencia
            amortizacion = 0.0
            cuota = 0.0

        total = cuota + seguro_vehicular_mensual + seguro_desgravamen_mensual
        cronograma.append(
            CuotaCalculada(
                numero_cuota=mes,
                fecha_pago=fecha,
                cuota=round(cuota, 2),
                interes=round(interes, 2),
                amortizacion=round(amortizacion, 2),
                saldo=round(saldo, 2),
                seguro_vehicular=seguro_vehicular_mensual,
                seguro_desgravamen=seguro_desgravamen_mensual,
                total=round(total, 2),
                es_periodo_gracia=True,
                es_cuota_balon=False,
            )
        )

    # --- 2. Cálculo de la cuota fija sobre el capital amortizable -----------
    n_pago = plazo_meses - meses_gracia
    b = cuota_balon_pct / 100
    capital_amortizable = monto_financiado * (1 - b)
    cuota_regular = cuota_francesa(capital_amortizable, i, n_pago)

    cuota_balon_monto = 0.0

    # --- 3. Fase de cuotas regulares (+ balón en la última) -----------------
    for k in range(1, n_pago + 1):
        interes = saldo * i
        amortizacion = cuota_regular - interes
        saldo = saldo - amortizacion
        cuota = cuota_regular
        es_ultima = k == n_pago
        es_balon = False

        if es_ultima:
            # Se liquida el saldo remanente (cuota balón real, sección 6.8)
            cuota_balon_monto = round(saldo, 2)
            amortizacion += saldo
            cuota = cuota_regular + cuota_balon_monto
            saldo = 0.0
            es_balon = True

        fecha = fecha + relativedelta(months=1)
        total = cuota + seguro_vehicular_mensual + seguro_desgravamen_mensual
        cronograma.append(
            CuotaCalculada(
                numero_cuota=meses_gracia + k,
                fecha_pago=fecha,
                cuota=round(cuota, 2),
                interes=round(interes, 2),
                amortizacion=round(amortizacion, 2),
                saldo=round(saldo, 2),
                seguro_vehicular=seguro_vehicular_mensual,
                seguro_desgravamen=seguro_desgravamen_mensual,
                total=round(total, 2),
                es_periodo_gracia=False,
                es_cuota_balon=es_balon,
            )
        )

    return ResultadoAmortizacion(
        cronograma=cronograma,
        cuota_regular=round(cuota_regular, 2),
        cuota_balon_monto=cuota_balon_monto,
    )
