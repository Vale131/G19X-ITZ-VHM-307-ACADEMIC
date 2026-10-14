import io
import pandas as pd

def generar_reporte_excel(df_historico, df_proyeccion, df_cartera, res_mc):
    """
    Genera un archivo Excel en memoria con múltiples pestañas ejecutivas.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Pestaña 1: Proyección de Flujo
        if df_proyeccion is not None and not df_proyeccion.empty:
            df_proyeccion.to_excel(writer, sheet_name='Proyección Flujo', index=False)
        
        # Pestaña 2: Cartera CxC / CxP
        if df_cartera is not None and not df_cartera.empty:
            df_cartera.to_excel(writer, sheet_name='Cartera CxC CxP', index=False)

        # Pestaña 3: Resumen de Riesgo Monte Carlo
        if res_mc:
            df_mc_summary = pd.DataFrame([{
                "Métrica": "Value at Risk (VaR 95%)", "Valor MXN": res_mc.get('var_95', 0)
            }, {
                "Métrica": "Value at Risk (VaR 99%)", "Valor MXN": res_mc.get('var_99', 0)
            }, {
                "Métrica": "Probabilidad de Iliquidez (%)", "Valor MXN": res_mc.get('prob_iliquidez', 0)
            }])
            df_mc_summary.to_excel(writer, sheet_name='Análisis Riesgo VaR', index=False)

        # Pestaña 4: Histórico Cargado
        if df_historico is not None and not df_historico.empty:
            df_historico.to_excel(writer, sheet_name='Histórico Creado', index=False)

    return output.getvalue()