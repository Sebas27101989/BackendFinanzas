"""
Servicio de reportes (pantalla "Reportes y Exportación", sección 5.1.2 y
algoritmo "Generar el reporte", sección 8, del informe).

Genera PDFs a partir de un `CreditoDetalle` ya calculado. Se apoya en
`reportlab`; si en el futuro se requiere otro formato (Excel, CSV) basta con
añadir un nuevo método en este mismo servicio, sin tocar routers ni el
motor financiero.
"""
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.schemas.credito import CreditoDetalle

styles = getSampleStyleSheet()


def generar_pdf_resumen(detalle: CreditoDetalle) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    elementos = [
        Paragraph("AutoFinance Pro — Resumen del Crédito", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"Crédito N° {detalle.credito.id_credito} — Estado: {detalle.credito.estado}", styles["Heading3"]),
        Spacer(1, 12),
    ]

    datos_credito = [
        ["Monto financiado", f"S/ {detalle.credito.monto_financiado:,.2f}"],
        ["Cuota inicial", f"S/ {detalle.credito.cuota_inicial:,.2f}"],
        ["Tipo de tasa", detalle.credito.tipo_tasa],
        ["Tasa de interés", f"{detalle.credito.tasa_interes:.2f}%"],
        ["Plazo", f"{detalle.credito.plazo_meses} meses"],
        ["Periodo de gracia", f"{detalle.credito.tipo_gracia} ({detalle.credito.meses_gracia} meses)"],
        ["Cuota balón", f"{detalle.credito.cuota_balon_pct:.2f}% -> S/ {detalle.indicadores.cuota_balon_monto:,.2f}"],
        ["Cuota regular", f"S/ {detalle.indicadores.cuota_regular:,.2f}"],
        ["Total pagado", f"S/ {detalle.indicadores.total_pagado:,.2f}"],
        ["Total intereses", f"S/ {detalle.indicadores.total_intereses:,.2f}"],
        ["Costos adicionales", f"S/ {detalle.indicadores.costos_adicionales:,.2f}"],
        ["VAN", f"S/ {detalle.indicadores.van:,.2f}"],
        ["TIR anual", f"{detalle.indicadores.tir_anual * 100:.2f}%"],
        ["TCEA", f"{detalle.indicadores.tcea * 100:.2f}%"],
    ]
    tabla = Table(datos_credito, colWidths=[7 * cm, 8 * cm])
    tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#1E3A8A")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    elementos.append(tabla)
    doc.build(elementos)
    return buffer.getvalue()


def generar_pdf_cronograma(detalle: CreditoDetalle) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    elementos = [
        Paragraph("AutoFinance Pro — Cronograma de Pagos (Método Francés)", styles["Title"]),
        Spacer(1, 12),
    ]

    encabezado = ["N°", "Fecha", "Cuota", "Interés", "Amortización", "Saldo", "Total"]
    filas = [encabezado]
    for c in detalle.cronograma:
        filas.append(
            [
                str(c.numero_cuota),
                c.fecha_pago.strftime("%d/%m/%Y"),
                f"{c.cuota:,.2f}",
                f"{c.interes:,.2f}",
                f"{c.amortizacion:,.2f}",
                f"{c.saldo:,.2f}",
                f"{c.total:,.2f}",
            ]
        )

    tabla = Table(filas, repeatRows=1)
    tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
            ]
        )
    )
    elementos.append(tabla)
    doc.build(elementos)
    return buffer.getvalue()
