"""Router: simulador de créditos (cálculo en memoria, sin persistencia)."""
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_credito_service_sin_repo, get_current_usuario
from app.schemas.simulacion import SimulacionInput, SimulacionResultado
from app.services.credito_service import CreditoService

router = APIRouter(
    prefix="/simulador", tags=["Simulador"], dependencies=[Depends(get_current_usuario)]
)


@router.post("/simular", response_model=SimulacionResultado)
def simular_credito(
    datos: SimulacionInput,
    service: Annotated[CreditoService, Depends(get_credito_service_sin_repo)],
):
    """Reproduce la pestaña 'Simulador de Créditos' (Parámetros / Cronograma /
    Indicadores) de la maqueta del informe: recibe las condiciones del
    crédito y devuelve el cronograma completo más los indicadores
    financieros, sin guardar nada en la base de datos."""
    return service.simular(datos)
