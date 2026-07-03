"""Router: catálogo de vehículos financiables (pantalla "Gestión de Vehículos")."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_usuario, get_vehiculo_service
from app.schemas.vehiculo import VehiculoCreate, VehiculoOut, VehiculoUpdate
from app.services.vehiculo_service import VehiculoService

router = APIRouter(
    prefix="/vehiculos", tags=["Vehículos"], dependencies=[Depends(get_current_usuario)]
)


@router.post("", response_model=VehiculoOut, status_code=status.HTTP_201_CREATED)
def crear_vehiculo(datos: VehiculoCreate, service: Annotated[VehiculoService, Depends(get_vehiculo_service)]):
    """Agrega un vehículo al catálogo de financiables."""
    return service.crear(datos)


@router.get("", response_model=list[VehiculoOut])
def listar_vehiculos(
    service: Annotated[VehiculoService, Depends(get_vehiculo_service)],
    q: str | None = Query(default=None, description="Buscar por marca o modelo"),
    skip: int = 0,
    limit: int = 100,
):
    """Lista vehículos paginados, o los busca por marca/modelo si se pasa `q`."""
    if q:
        return service.buscar(q)
    return service.listar(skip, limit)


@router.get("/{id_vehiculo}", response_model=VehiculoOut)
def obtener_vehiculo(id_vehiculo: int, service: Annotated[VehiculoService, Depends(get_vehiculo_service)]):
    """Obtiene el detalle de un vehículo del catálogo por su ID."""
    return service.obtener(id_vehiculo)


@router.put("/{id_vehiculo}", response_model=VehiculoOut)
def actualizar_vehiculo(
    id_vehiculo: int, datos: VehiculoUpdate, service: Annotated[VehiculoService, Depends(get_vehiculo_service)]
):
    """Actualiza los datos de un vehículo existente del catálogo."""
    return service.actualizar(id_vehiculo, datos)


@router.delete("/{id_vehiculo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_vehiculo(id_vehiculo: int, service: Annotated[VehiculoService, Depends(get_vehiculo_service)]):
    """Elimina un vehículo del catálogo (no debe estar referenciado por créditos)."""
    service.eliminar(id_vehiculo)
