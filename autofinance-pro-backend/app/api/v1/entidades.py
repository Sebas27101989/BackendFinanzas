"""Router: entidades financieras (bancos, cajas municipales, financieras)."""
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_usuario, get_entidad_service
from app.schemas.entidad_financiera import EntidadFinancieraCreate, EntidadFinancieraOut
from app.services.entidad_service import EntidadFinancieraService

router = APIRouter(
    prefix="/entidades-financieras", tags=["Entidades Financieras"], dependencies=[Depends(get_current_usuario)]
)


@router.post("", response_model=EntidadFinancieraOut, status_code=status.HTTP_201_CREATED)
def crear_entidad(
    datos: EntidadFinancieraCreate, service: Annotated[EntidadFinancieraService, Depends(get_entidad_service)]
):
    """Registra una entidad financiera (banco, caja municipal, financiera)."""
    return service.crear(datos)


@router.get("", response_model=list[EntidadFinancieraOut])
def listar_entidades(service: Annotated[EntidadFinancieraService, Depends(get_entidad_service)]):
    """Lista todas las entidades financieras registradas."""
    return service.listar()


@router.get("/{id_entidad}", response_model=EntidadFinancieraOut)
def obtener_entidad(id_entidad: int, service: Annotated[EntidadFinancieraService, Depends(get_entidad_service)]):
    """Obtiene el detalle de una entidad financiera por su ID."""
    return service.obtener(id_entidad)
