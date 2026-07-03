"""
Servicio de conversión de tasas de interés (sección 4.1.3 y 6.2 del informe).

Responsabilidad única: recibir la tasa tal como la ingresa el usuario
(nominal o efectiva, anual) y devolver la Tasa Efectiva Periódica (TEP)
mensual que necesita el motor de amortización francesa. No conoce nada de
créditos, cuotas ni de la base de datos.
"""
from app.core.config import settings


def tna_a_tea(tna_pct: float, frecuencia_capitalizacion: str) -> float:
    """Convierte una Tasa Nominal Anual (%) a Tasa Efectiva Anual (decimal).

    TEA = (1 + TNA/m)^m - 1
    """
    m = settings.FRECUENCIAS_CAPITALIZACION[frecuencia_capitalizacion]
    tna = tna_pct / 100
    return (1 + tna / m) ** m - 1


def tea_a_tep(tea: float, dias_periodo: int = 30) -> float:
    """Convierte una Tasa Efectiva Anual (decimal) a la Tasa Efectiva Periódica
    correspondiente a `dias_periodo` días (30 = mensual, según sección 6.2):

    TEP = (1 + TEA)^(dias_periodo/360) - 1
    """
    return (1 + tea) ** (dias_periodo / settings.DIAS_ANIO_COMERCIAL) - 1


def obtener_tasa_efectiva_mensual(tipo_tasa: str, tasa_pct: float, frecuencia_capitalizacion: str | None) -> float:
    """Punto de entrada único del servicio: dado lo que el usuario configuró en
    el simulador (tipo_tasa + tasa_pct [+ frecuencia_capitalizacion si es
    nominal]), devuelve la tasa efectiva periódica MENSUAL (decimal) lista
    para usarse en el método francés.
    """
    if tipo_tasa == "Nominal":
        if not frecuencia_capitalizacion:
            raise ValueError("Se requiere frecuencia_capitalizacion para una tasa Nominal (TNA)")
        tea = tna_a_tea(tasa_pct, frecuencia_capitalizacion)
    elif tipo_tasa == "Efectiva":
        tea = tasa_pct / 100
    else:
        raise ValueError(f"tipo_tasa inválido: {tipo_tasa}")

    return tea_a_tep(tea, dias_periodo=settings.DIAS_MES_COMERCIAL)


def tea_desde_tep_mensual(tep_mensual: float) -> float:
    """Inverso de `tea_a_tep`: anualiza una tasa efectiva mensual -> TEA (decimal).
    Se usa para expresar la TIR mensual del flujo como TIR/TCEA anual.
    """
    return (1 + tep_mensual) ** 12 - 1
