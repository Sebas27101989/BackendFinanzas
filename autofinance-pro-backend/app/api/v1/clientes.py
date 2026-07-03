"""Router: gestión de clientes (pantalla "Gestión de Clientes")."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_cliente_service, get_current_usuario
from app.models.usuario import Usuario
from app.schemas.cliente import ClienteCreate, ClienteOut, ClienteUpdate
from app.services.cliente_service import ClienteService

router = APIRouter(
    prefix="/clientes", tags=["Clientes"], dependencies=[Depends(get_current_usuario)]
)


@router.post("", response_model=ClienteOut, status_code=status.HTTP_201_CREATED)
def crear_cliente(datos: ClienteCreate, service: Annotated[ClienteService, Depends(get_cliente_service)]):
    """Registra un nuevo cliente titular de créditos vehiculares."""
    return service.crear(datos)


@router.get("", response_model=list[ClienteOut])
def listar_clientes(
    service: Annotated[ClienteService, Depends(get_cliente_service)],
    q: str | None = Query(default=None, description="Buscar por nombre, apellido o DNI"),
    skip: int = 0,
    limit: int = 100,
):
    """Lista clientes paginados, o los busca por nombre/apellido/DNI si se pasa `q`."""
    if q:
        return service.buscar(q)
    return service.listar(skip, limit)


@router.get("/{id_cliente}", response_model=ClienteOut)
def obtener_cliente(id_cliente: int, service: Annotated[ClienteService, Depends(get_cliente_service)]):
    """Obtiene el detalle de un cliente por su ID."""
    return service.obtener(id_cliente)


@router.put("/{id_cliente}", response_model=ClienteOut)
def actualizar_cliente(
    id_cliente: int, datos: ClienteUpdate, service: Annotated[ClienteService, Depends(get_cliente_service)]
):
    """Actualiza los datos de contacto/ingresos de un cliente existente."""
    return service.actualizar(id_cliente, datos)


@router.delete("/{id_cliente}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cliente(id_cliente: int, service: Annotated[ClienteService, Depends(get_cliente_service)]):
    """Elimina un cliente (no debe tener créditos vehiculares asociados)."""
    service.eliminar(id_cliente)
