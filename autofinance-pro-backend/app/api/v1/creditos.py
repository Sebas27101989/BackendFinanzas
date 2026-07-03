"""Router: créditos vehiculares registrados (persistidos en base de datos)."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_credito_service, get_current_usuario
from app.schemas.credito import CreditoCreate, CreditoDetalle
from app.services.credito_service import CreditoService

router = APIRouter(
    prefix="/creditos", tags=["Créditos Vehiculares"], dependencies=[Depends(get_current_usuario)]
)


@router.post("", response_model=CreditoDetalle, status_code=status.HTTP_201_CREATED)
def registrar_credito(datos: CreditoCreate, service: Annotated[CreditoService, Depends(get_credito_service)]):
    """Calcula el cronograma completo (método francés + gracia + cuota
    balón), calcula VAN/TIR/TCEA y persiste todo en una sola operación
    (sección 8 del informe: 'Guardar operación dentro de la base de datos')."""
    return service.registrar_credito(datos)


@router.get("/{id_credito}", response_model=CreditoDetalle)
def obtener_credito(id_credito: int, service: Annotated[CreditoService, Depends(get_credito_service)]):
    """Devuelve el detalle completo de un crédito registrado: condiciones,
    cronograma de cuotas e indicadores financieros (VAN/TIR/TCEA)."""
    detalle = service.obtener_detalle(id_credito)
    if detalle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Crédito {id_credito} no encontrado")
    return detalle
