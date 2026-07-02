"""Vistas de reportes: dashboard con Chart.js, exportar PDF y Excel."""

import json
from datetime import date, timedelta
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.core.paginator import Paginator

from ..models import Reserva, Usuario, Cancha, PuntosHistorial
from .helpers import rol_requerido


# ──────────────────────────────────────────────
# 11. Reportes (P6: municipio puede acceder)
# ──────────────────────────────────────────────

@rol_requerido('administrador', 'municipio')
def reportes_view(request):
    total_reservas = Reserva.objects.count()
    reservas_confirmadas = Reserva.objects.filter(estado='confirmada').count()
    reservas_canceladas = Reserva.objects.filter(estado='cancelada').count()
    reservas_no_asistidas = Reserva.objects.filter(estado='no_asistida').count()
    reservas_asistidas = Reserva.objects.filter(estado='asistida').count()
    total_usuarios = Usuario.objects.count()
    total_canchas = Cancha.objects.count()

    historial_puntos = PuntosHistorial.objects.select_related(
        'usuario', 'reserva'
    ).order_by('-fecha')[:50]

    ultimas_reservas = Reserva.objects.select_related(
        'usuario', 'cancha'
    ).order_by('-fecha_creacion')[:20]

    # Data for Chart.js
    # 1. Reservas por día (últimos 30 días)
    hace_30_dias = date.today() - timedelta(days=30)
    reservas_por_dia = (
        Reserva.objects.filter(fecha__gte=hace_30_dias)
        .annotate(dia=TruncDate('fecha'))
        .values('dia')
        .annotate(total=Count('id'))
        .order_by('dia')
    )
    chart_dias_labels = [r['dia'].strftime('%d/%m') if r['dia'] else '' for r in reservas_por_dia]
    chart_dias_data = [r['total'] for r in reservas_por_dia]

    # 2. Canchas más populares (top 5)
    canchas_populares = (
        Reserva.objects.values('cancha__nombre')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )
    chart_canchas_labels = [r['cancha__nombre'] for r in canchas_populares]
    chart_canchas_data = [r['total'] for r in canchas_populares]

    # 3. Distribución por deporte
    por_deporte = (
        Reserva.objects.values('cancha__tipo_deporte')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    chart_deporte_labels = [r['cancha__tipo_deporte'].capitalize() for r in por_deporte]
    chart_deporte_data = [r['total'] for r in por_deporte]

    usuario = request.usuario
    return render(request, 'reservas/reportes.html', {
        'total_reservas': total_reservas,
        'reservas_confirmadas': reservas_confirmadas,
        'reservas_canceladas': reservas_canceladas,
        'reservas_no_asistidas': reservas_no_asistidas,
        'reservas_asistidas': reservas_asistidas,
        'total_usuarios': total_usuarios,
        'total_canchas': total_canchas,
        'historial_puntos': historial_puntos,
        'ultimas_reservas': ultimas_reservas,
        'usuario': usuario,
        # Chart data (JSON serialized)
        'chart_dias_labels': json.dumps(chart_dias_labels),
        'chart_dias_data': json.dumps(chart_dias_data),
        'chart_canchas_labels': json.dumps(chart_canchas_labels),
        'chart_canchas_data': json.dumps(chart_canchas_data),
        'chart_deporte_labels': json.dumps(chart_deporte_labels),
        'chart_deporte_data': json.dumps(chart_deporte_data),
    })


# ──────────────────────────────────────────────
# Exportar PDF
# ──────────────────────────────────────────────

@rol_requerido('administrador', 'municipio')
def exportar_pdf_view(request):
    """Exporta los reportes a PDF usando reportlab."""
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.units import cm
    import io

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=1.5*cm, bottomMargin=1.5*cm)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=20)
    elements.append(Paragraph('Reporte del Polideportivo', title_style))
    elements.append(Paragraph(f'Generado: {date.today().strftime("%d/%m/%Y")}', styles['Normal']))
    elements.append(Spacer(1, 1*cm))

    # KPI Summary
    total_reservas = Reserva.objects.count()
    reservas_confirmadas = Reserva.objects.filter(estado='confirmada').count()
    reservas_canceladas = Reserva.objects.filter(estado='cancelada').count()
    reservas_no_asistidas = Reserva.objects.filter(estado='no_asistida').count()
    reservas_asistidas = Reserva.objects.filter(estado='asistida').count()
    total_usuarios = Usuario.objects.count()
    total_canchas = Cancha.objects.count()

    elements.append(Paragraph('Resumen General', styles['Heading2']))
    kpi_data = [
        ['Métrica', 'Valor'],
        ['Total Reservas', str(total_reservas)],
        ['Confirmadas', str(reservas_confirmadas)],
        ['Asistidas', str(reservas_asistidas)],
        ['Canceladas', str(reservas_canceladas)],
        ['No Asistidas', str(reservas_no_asistidas)],
        ['Total Usuarios', str(total_usuarios)],
        ['Total Canchas', str(total_canchas)],
    ]
    kpi_table = Table(kpi_data, colWidths=[8*cm, 4*cm])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c4dff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 1*cm))

    # Últimas reservas
    elements.append(Paragraph('Últimas 20 Reservas', styles['Heading2']))
    reservas = Reserva.objects.select_related('usuario', 'cancha').order_by('-fecha_creacion')[:20]
    reserva_data = [['#', 'Usuario', 'Cancha', 'Fecha', 'Horario', 'Estado']]
    for r in reservas:
        reserva_data.append([
            str(r.id),
            r.usuario.nombre[:20],
            r.cancha.nombre[:20],
            r.fecha.strftime('%d/%m/%Y'),
            f'{r.hora_inicio.strftime("%H:%M")}-{r.hora_fin.strftime("%H:%M")}',
            r.get_estado_display(),
        ])

    reserva_table = Table(reserva_data, colWidths=[2*cm, 5*cm, 5*cm, 3*cm, 4*cm, 3*cm])
    reserva_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c4dff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    elements.append(reserva_table)

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_polideportivo_{date.today().strftime("%Y%m%d")}.pdf"'
    return response


# ──────────────────────────────────────────────
# Exportar Excel
# ──────────────────────────────────────────────

@rol_requerido('administrador', 'municipio')
def exportar_excel_view(request):
    """Exporta los reportes a Excel usando openpyxl."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    import io

    wb = Workbook()

    # Sheet 1: Resumen
    ws1 = wb.active
    ws1.title = 'Resumen'

    header_font = Font(bold=True, color='FFFFFF', size=11)
    header_fill = PatternFill(start_color='7C4DFF', end_color='7C4DFF', fill_type='solid')
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin'),
    )

    ws1.append(['Reporte del Polideportivo'])
    ws1['A1'].font = Font(bold=True, size=16)
    ws1.append([f'Generado: {date.today().strftime("%d/%m/%Y")}'])
    ws1.append([])

    headers = ['Métrica', 'Valor']
    ws1.append(headers)
    for cell in ws1[4]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center')
        cell.border = thin_border

    total_reservas = Reserva.objects.count()
    data_resumen = [
        ('Total Reservas', total_reservas),
        ('Confirmadas', Reserva.objects.filter(estado='confirmada').count()),
        ('Asistidas', Reserva.objects.filter(estado='asistida').count()),
        ('Canceladas', Reserva.objects.filter(estado='cancelada').count()),
        ('No Asistidas', Reserva.objects.filter(estado='no_asistida').count()),
        ('Total Usuarios', Usuario.objects.count()),
        ('Total Canchas', Cancha.objects.count()),
    ]
    for row_data in data_resumen:
        ws1.append(row_data)

    ws1.column_dimensions['A'].width = 25
    ws1.column_dimensions['B'].width = 15

    # Sheet 2: Reservas
    ws2 = wb.create_sheet('Reservas')
    headers2 = ['ID', 'Usuario', 'Correo', 'Cancha', 'Deporte', 'Fecha', 'Hora Inicio', 'Hora Fin', 'Estado', 'Invitados']
    ws2.append(headers2)
    for cell in ws2[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center')
        cell.border = thin_border

    reservas = Reserva.objects.select_related('usuario', 'cancha').order_by('-fecha_creacion')[:200]
    for r in reservas:
        ws2.append([
            r.id,
            r.usuario.nombre,
            r.usuario.correo,
            r.cancha.nombre,
            r.cancha.get_tipo_deporte_display(),
            r.fecha.strftime('%d/%m/%Y'),
            r.hora_inicio.strftime('%H:%M'),
            r.hora_fin.strftime('%H:%M'),
            r.get_estado_display(),
            r.lista_invitados or '',
        ])

    for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']:
        ws2.column_dimensions[col].width = 18

    # Sheet 3: Usuarios
    ws3 = wb.create_sheet('Usuarios')
    headers3 = ['ID', 'Nombre', 'Correo', 'Teléfono', 'Rol', 'Puntos', 'Estado', 'Fecha Registro']
    ws3.append(headers3)
    for cell in ws3[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center')
        cell.border = thin_border

    usuarios = Usuario.objects.all().order_by('-fecha_creacion')
    for u in usuarios:
        ws3.append([
            u.id,
            u.nombre,
            u.correo,
            u.telefono or '',
            u.get_rol_display(),
            u.puntos_acumulados,
            u.get_estado_display(),
            u.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
        ])

    for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
        ws3.column_dimensions[col].width = 18

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="reporte_polideportivo_{date.today().strftime("%Y%m%d")}.xlsx"'
    return response
