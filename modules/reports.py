import pandas as pd
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
import io

def generar_reporte_excel(df_historico, df_forecast, df_cartera, res_mc):
    """Genera un libro de Excel profesional consolidado en memoria con openpyxl."""
    wb = Workbook()
    
    # Estilos Corporativos PluriOne
    header_fill = PatternFill(start_color="6D1B2A", end_color="6D1B2A", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    data_font = Font(name="Calibri", size=10)
    bold_font = Font(name="Calibri", size=10, bold=True)
    
    border_thin = Border(
        left=Side(style='thin', color='D3D3D3'),
        right=Side(style='thin', color='D3D3D3'),
        top=Side(style='thin', color='D3D3D3'),
        bottom=Side(style='thin', color='D3D3D3')
    )

    # 1. Hoja de Resumen Ejecutivo y Riesgo VaR
    ws_resumen = wb.active
    ws_resumen.title = "Resumen & VaR"
    ws_resumen.views.sheetView[0].showGridLines = True
    
    ws_resumen.append(["Métrica de Riesgo / Indicador", "Valor Calculado"])
    
    val_var95 = float(res_mc.get('var_95', 0.0))
    val_var99 = float(res_mc.get('var_99', 0.0))
    val_prob_def = float(res_mc.get('prob_deficit', 0.0))
    val_saldo_esp = float(res_mc.get('saldo_final_esperado', 0.0))

    ws_resumen.append(["Value at Risk 95% (VaR 95%) ($)", val_var95])
    ws_resumen.append(["Value at Risk 99% (VaR 99%) ($)", val_var99])
    ws_resumen.append(["Probabilidad de Déficit de Caja (%)", val_prob_def / 100.0])  # En decimal para formato %
    ws_resumen.append(["Saldo Final Esperado ($)", val_saldo_esp])

    # Estilizado y formato numérico para la Hoja de Resumen
    for row_idx, row in enumerate(ws_resumen.iter_rows(min_row=1, max_row=5, min_col=1, max_col=2), start=1):
        for col_idx, cell in enumerate(row, start=1):
            cell.font = data_font
            cell.border = border_thin
            if col_idx == 2 and row_idx > 1:
                cell.alignment = Alignment(horizontal="right")
                if row_idx in [2, 3, 5]:
                    cell.number_format = '"$"#,##0.00'
                elif row_idx == 4:
                    cell.number_format = '0.00%'

    for cell in ws_resumen[1]:
        cell.fill = header_fill
        cell.font = header_font

    # 2. Hoja de Proyección de Flujo
    ws_proj = wb.create_sheet(title="Proyección de Flujo")
    ws_proj.views.sheetView[0].showGridLines = True
    if df_forecast is not None and not df_forecast.empty:
        df_export_proj = df_forecast.copy()
        if 'ds' in df_export_proj.columns:
            df_export_proj['ds'] = pd.to_datetime(df_export_proj['ds']).dt.strftime('%Y-%m-%d')
            
        cols_deseadas = ['ds', 'Ingresos', 'Egresos', 'Flujo_Neto', 'Saldo_Acumulado', 'flujo_proyectado', 'saldo_proyectado']
        cols_existentes = [c for c in cols_deseadas if c in df_export_proj.columns]
        if cols_existentes:
            df_export_proj = df_export_proj[cols_existentes]
        
        for r in dataframe_to_rows(df_export_proj, index=False, header=True):
            ws_proj.append(r)

        for cell in ws_proj[1]:
            cell.fill = header_fill
            cell.font = header_font

        # Formatos de celda en Proyección
        for row in ws_proj.iter_rows(min_row=2, max_row=ws_proj.max_row, min_col=1, max_col=ws_proj.max_column):
            for col_idx, cell in enumerate(row, start=1):
                cell.font = data_font
                cell.border = border_thin
                if col_idx > 1 and isinstance(cell.value, (int, float)):
                    cell.number_format = '"$"#,##0.00'

    # 3. Hoja de Cartera CxC / CxP
    ws_cart = wb.create_sheet(title="Cartera CxC y CxP")
    ws_cart.views.sheetView[0].showGridLines = True
    if df_cartera is not None and not df_cartera.empty:
        df_export_cart = df_cartera.copy()
        if 'fecha_vencimiento' in df_export_cart.columns:
            df_export_cart['fecha_vencimiento'] = pd.to_datetime(df_export_cart['fecha_vencimiento'], errors='coerce').dt.strftime('%Y-%m-%d')

        for r in dataframe_to_rows(df_export_cart, index=False, header=True):
            ws_cart.append(r)

        for cell in ws_cart[1]:
            cell.fill = header_fill
            cell.font = header_font

        for row in ws_cart.iter_rows(min_row=2, max_row=ws_cart.max_row, min_col=1, max_col=ws_cart.max_column):
            for cell in row:
                cell.font = data_font
                cell.border = border_thin

    # 4. Hoja de Datos Históricos
    if df_historico is not None and not df_historico.empty:
        ws_hist = wb.create_sheet(title="Histórico de Caja")
        ws_hist.views.sheetView[0].showGridLines = True
        
        df_export_hist = df_historico.copy()
        if 'ds' in df_export_hist.columns:
            df_export_hist['ds'] = pd.to_datetime(df_export_hist['ds']).dt.strftime('%Y-%m-%d')

        for r in dataframe_to_rows(df_export_hist, index=False, header=True):
            ws_hist.append(r)

        for cell in ws_hist[1]:
            cell.fill = header_fill
            cell.font = header_font

        for row in ws_hist.iter_rows(min_row=2, max_row=ws_hist.max_row, min_col=1, max_col=ws_hist.max_column):
            for col_idx, cell in enumerate(row, start=1):
                cell.font = data_font
                cell.border = border_thin
                if col_idx > 1 and isinstance(cell.value, (int, float)):
                    cell.number_format = '"$"#,##0.00'

    # Auto-ajuste de ancho de columnas para todas las pestañas
    for sheet in wb.worksheets:
        for col in sheet.columns:
            max_len = 0
            col_letter = col[0].column_letter
            for cell in col:
                val_str = str(cell.value or '')
                if len(val_str) > max_len:
                    max_len = len(val_str)
            sheet.column_dimensions[col_letter].width = max(max_len + 4, 14)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()