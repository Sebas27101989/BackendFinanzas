"""Router: reportes exportables en PDF (pantalla "Reportes y Exportación")."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response

from app.api.deps import get_credito_service, get_current_usuario
from app.services.credito_service import CreditoService
from app.services.reporte_service import generar_pdf_cronograma, generar_pdf_resumen

router = APIRouter(
    prefix="/reportes", tags=["Reportes"], dependencies=[Depends(get_current_usuario)]
)


def _obtener_detalle_o_404(id_credito: int, service: CreditoService):
    detalle = service.obtener_detalle(id_credito)
    if detalle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Crédito {id_credito} no encontrado")
    return detalle


@router.get("/creditos/{id_credito}/resumen.pdf")
def descargar_resumen_pdf(id_credito: int, service: Annotated[CreditoService, Depends(get_credito_service)]):
    """Genera y descarga el PDF de resumen (condiciones e indicadores) del crédito."""
    detalle = _obtener_detalle_o_404(id_credito, service)
    pdf_bytes = generar_pdf_resumen(detalle)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Resumen_Credito_{id_credito}.pdf"},
    )


@router.get("/creditos/{id_credito}/cronograma.pdf")
def descargar_cronograma_pdf(id_credito: int, service: Annotated[CreditoService, Depends(get_credito_service)]):
    """Genera y descarga el PDF del cronograma de cuotas completo del crédito."""
    detalle = _obtener_detalle_o_404(id_credito, service)
    pdf_bytes = generar_pdf_cronograma(detalle)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Cronograma_Credito_{id_credito}.pdf"},
    )
