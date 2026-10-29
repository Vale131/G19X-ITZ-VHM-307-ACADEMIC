import numpy as np
import pandas as pd
import plotly.graph_objects as go

def ejecutar_simulacion_monte_carlo(df_proyeccion: pd.DataFrame, saldo_inicial: float = 500000.0, num_simulaciones: int = 1000, umbral_deficit: float = 0.0) -> dict:
    """
    Ejecuta una simulación estocástica de Monte Carlo conectada dinámicamente con
    la proyección determinista (escenario seleccionado + cartera ponderada).
    
    Unificación del VaR (95% y 99%): Representa la pérdida máxima esperada con un
    95% / 99% de confianza en comparación con el saldo final esperado.
    """
    if df_proyeccion is None or df_proyeccion.empty:
        return {
            "var_95": 0.0,
            "var_99": 0.0,
            "prob_deficit": 0.0,
            "saldo_final_esperado": 0.0,
            "saldos_finales": []
        }

    # Extraer el flujo neto proyectado diario
    if "Flujo_Neto" in df_proyeccion.columns:
        flujos_base = df_proyeccion["Flujo_Neto"].values
    elif "Ingresos" in df_proyeccion.columns and "Egresos" in df_proyeccion.columns:
        flujos_base = (df_proyeccion["Ingresos"] - df_proyeccion["Egresos"]).values
    else:
        flujos_base = np.zeros(len(df_proyeccion))

    dias = len(flujos_base)
    volatilidad = np.std(flujos_base) if len(flujos_base) > 1 and np.std(flujos_base) > 0 else 1000.0

    np.random.seed(42)  # Semilla fija para reproducibilidad técnica
    ruido_estocastico = np.random.normal(0, volatilidad, (num_simulaciones, dias))
    
    # Trayectorias = Flujo Neto proyectado + Perturbaciones estocásticas
    trayectorias_flujo = flujos_base + ruido_estocastico
    saldos_acumulados = saldo_inicial + np.cumsum(trayectorias_flujo, axis=1)
    saldos_finales = saldos_acumulados[:, -1]

    saldo_final_esperado = float(np.mean(saldos_finales))
    
    # Cálculo unificado de VaR
    percentil_5 = float(np.percentile(saldos_finales, 5))
    percentil_1 = float(np.percentile(saldos_finales, 1))

    var_95 = max(0.0, saldo_final_esperado - percentil_5)
    var_99 = max(0.0, saldo_final_esperado - percentil_1)

    # Probabilidad de caer por debajo del umbral de déficit
    deficits = np.any(saldos_acumulados < umbral_deficit, axis=1)
    prob_deficit = float(np.mean(deficits) * 100.0)

    return {
        "var_95": var_95,
        "var_99": var_99,
        "prob_deficit": prob_deficit,
        "saldo_final_esperado": saldo_final_esperado,
        "saldos_finales": saldos_finales.tolist()
    }

def crear_grafica_monte_carlo(res_mc: dict):
    """Genera el histograma de distribución de saldos finales con las líneas de corte VaR."""
    saldos = res_mc.get("saldos_finales", [])
    if not saldos:
        fig = go.Figure()
        fig.update_layout(title="Sin datos de simulación")
        return fig

    s_esperado = res_mc.get("saldo_final_esperado", 0.0)
    var_95 = res_mc.get("var_95", 0.0)
    var_99 = res_mc.get("var_99", 0.0)

    cutoff_95 = s_esperado - var_95
    cutoff_99 = s_esperado - var_99

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=saldos,
        nbinsx=40,
        name="Saldos Simulado",
        marker_color="#70112F",
        opacity=0.75
    ))

    fig.add_vline(x=s_esperado, line_dash="dash", line_color="#16A34A", annotation_text="Esperado")
    fig.add_vline(x=cutoff_95, line_dash="dot", line_color="#F59E0B", annotation_text="VaR 95%")
    fig.add_vline(x=cutoff_99, line_dash="solid", line_color="#DC2626", annotation_text="VaR 99%")

    fig.update_layout(
        title="<b>Distribución Estocástica de Saldos Finales & Indicadores VaR</b>",
        xaxis_title="Saldo Final ($)",
        yaxis_title="Frecuencia / Simulaciones",
        height=380
    )
    return fig