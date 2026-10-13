import numpy as np
import pandas as pd
import plotly.graph_objects as go

def ejecutar_simulacion_monte_carlo(df_historico, saldo_inicial=654121.0, dias_simulacion=30, num_simulaciones=1000, umbral_minimo=50000.0):
    """
    Ejecuta 1,000 iteraciones estocásticas de Monte Carlo utilizando la distribución 
    de retornos/flujos diarios del histórico real.
    """
    if df_historico is None or len(df_historico) < 5:
        mean_flujo = 25000.0
        std_flujo = 18000.0
    else:
        flujos_diarios = df_historico['Ingresos'] - df_historico['Egresos']
        mean_flujo = flujos_diarios.mean()
        std_flujo = flujos_diarios.std()

    np.random.seed(42)
    flujos_simulados = np.random.normal(loc=mean_flujo, scale=std_flujo, size=(num_simulaciones, dias_simulacion))
    
    trayectorias_saldo = saldo_inicial + np.cumsum(flujos_simulados, axis=1)
    saldos_finales = trayectorias_saldo[:, -1]

    deficit_esperado = saldo_inicial - saldos_finales
    var_95 = np.percentile(deficit_esperado, 95)
    var_99 = np.percentile(deficit_esperado, 99)
    
    casos_iliquidez = np.sum(np.min(trayectorias_saldo, axis=1) < umbral_minimo)
    prob_iliquidez = (casos_iliquidez / num_simulaciones) * 100

    return {
        "saldos_finales": saldos_finales,
        "trayectorias": trayectorias_saldo,
        "var_95": max(0, var_95),
        "var_99": max(0, var_99),
        "prob_iliquidez": prob_iliquidez,
        "media_saldo_final": np.mean(saldos_finales),
        "min_saldo_final": np.min(saldos_finales)
    }

def crear_grafica_monte_carlo(res_simulacion, umbral_minimo=50000.0):
    """Genera el histograma de distribución de saldos finales con líneas de VaR y Umbral."""
    saldos = res_simulacion["saldos_finales"]

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=saldos,
        nbinsx=40,
        name='Distribución de Saldos Finales',
        marker_color='#6366F1',
        opacity=0.75
    ))

    fig.add_vline(
        x=umbral_minimo,
        line_dash="dash",
        line_color="#DC2626",
        annotation_text=f"Umbral Mínimo (${umbral_minimo:,.0f})",
        annotation_position="top left"
    )

    fig.add_vline(
        x=res_simulacion["media_saldo_final"],
        line_dash="solid",
        line_color="#059669",
        annotation_text=f"Media Estimada (${res_simulacion['media_saldo_final']:,.0f})",
        annotation_position="top right"
    )

    fig.update_layout(
        template="plotly_white",
        title="Distribución Estocástica de Saldos a 30 Días (1,000 Simulaciónes)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", size=12, color="#374151"),
        xaxis_title="Saldo Final Simulado ($ MXN)",
        yaxis_title="Frecuencia (Escenarios)",
        margin=dict(l=10, r=10, t=40, b=10)
    )

    return fig