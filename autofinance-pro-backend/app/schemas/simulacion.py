"""
Schemas (DTOs) del Simulador de Créditos (sección 5.1.2 y 6 del informe).

`SimulacionInput` agrupa exactamente los mismos campos que el formulario
"Configuración del Crédito" de la maqueta de interfaz: precio del vehículo,
cuota inicial, tasa de interés (TEA/TNA), plazo, cuota balón, periodo de
gracia y costos adicionales (seguro vehicular, seguro de desgravamen,
gastos administrativos).
"""
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, model_validator

TipoTasa = Literal["Nominal", "Efectiva"]
TipoGracia = Literal["Ninguno", "Total", "Parcial"]
FrecuenciaCapitalizacion = Literal[
    "Diaria", "Mensual", "Bimestral", "Trimestral", "Cuatrimestral", "Semestral", "Anual"
]


class SimulacionInput(BaseModel):
    precio_vehiculo: float = Field(gt=0, description="Precio comercial del vehículo")
    cuota_inicial: float = Field(ge=0, description="Pago inicial (reduce el monto a financiar)")
    moneda: Literal["PEN", "USD"] = "PEN"

    tasa_interes: float = Field(gt=0, description="Valor porcentual de la tasa, ej. 10.7 = 10.7%")
    tipo_tasa: TipoTasa = "Efectiva"
    frecuencia_capitalizacion: FrecuenciaCapitalizacion | None = Field(
        default=None, description="Obligatorio si tipo_tasa='Nominal'"
    )

    plazo_meses: int = Field(gt=0, le=96)
    cuota_balon_pct: float = Field(default=0.0, ge=0, lt=100, description="% del monto financiado, modalidad Compra Inteligente")

    tipo_gracia: TipoGracia = "Ninguno"
    meses_gracia: int = Field(default=0, ge=0)

    seguro_vehicular_mensual: float = Field(default=0.0, ge=0)
    seguro_desgravamen_mensual: float = Field(default=0.0, ge=0)
    gastos_administrativos: float = Field(default=0.0, ge=0)

    tasa_descuento_van: float | None = Field(
        default=None,
        description="Tasa de descuento (COK) anual para el cálculo del VAN. "
        "Si no se especifica, se usa TASA_DESCUENTO_DEFECTO de la configuración.",
    )

    fecha_inicio: date

    @model_validator(mode="after")
    def validar_consistencia(self) -> "SimulacionInput":
        if self.tipo_tasa == "Nominal" and not self.frecuencia_capitalizacion:
            raise ValueError("frecuencia_capitalizacion es obligatoria cuando tipo_tasa='Nominal'")
        if self.tipo_gracia != "Ninguno" and self.meses_gracia <= 0:
            raise ValueError("meses_gracia debe ser mayor a 0 cuando se define un periodo de gracia")
        if self.tipo_gracia == "Ninguno" and self.meses_gracia > 0:
            raise ValueError("tipo_gracia debe ser 'Total' o 'Parcial' si meses_gracia > 0")
        if self.meses_gracia >= self.plazo_meses:
            raise ValueError("meses_gracia debe ser menor al plazo total en meses")
        if self.cuota_inicial > self.precio_vehiculo:
            raise ValueError("cuota_inicial no puede ser mayor al precio del vehículo")
        return self

    @property
    def monto_financiado(self) -> float:
        return round(self.precio_vehiculo - self.cuota_inicial, 2)


class CuotaOut(BaseModel):
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


class IndicadoresOut(BaseModel):
    monto_financiado: float
    cuota_regular: float
    cuota_balon_monto: float
    total_pagado: float
    total_intereses: float
    costos_adicionales: float
    van: float
    tir_mensual: float
    tir_anual: float
    tcea: float


class SimulacionResultado(BaseModel):
    cronograma: list[CuotaOut]
    indicadores: IndicadoresOut
