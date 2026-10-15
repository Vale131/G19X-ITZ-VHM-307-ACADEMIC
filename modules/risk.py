import numpy as np
import pandas as pd
import plotly.graph_objects as go

def ejecutar_simulacion_monte_carlo(df_hist: pd.DataFrame, saldo_inicial: float = 100000.0, dias_simulacion: int = 30, num_simulaciones: int = 1000):
    """
    Ejecuta simulaciones estocásticas de Monte Carlo para calcular el Value at Risk (VaR)
    y la probabilidad de caída en déficit financiero.
    """
    if df_hist.empty:
        # Valores por defecto si la base está vacía
        return {
            "simulaciones": np.zeros((num_simulaciones, dias_simulacion)),
            "var_95": 0.0,
            "var_99": 0.0,
            "prob_deficit": 0.0,
            "dias_simulacion": dias_simulacion
        }

    df_clean = df_hist.sort_values('ds').copy()
    flujo_diario = df_clean['Ingresos'] - df_clean['Egresos']
    
    mu = flujo_diario.mean()
    sigma = flujo_diario.std() if len(flujo_diario) > 1 else 1000.0

    np.random.seed(42)
    innovaciones = np.random.normal(loc=mu, scale=sigma, size=(num_simulaciones, dias_simulacion))
    
    # Trayectorias acumuladas
    trayectorias = saldo_inicial + np.cumsum(innovaciones, axis=1)

    saldos_finales = trayectorias[:, -1]
    
    # VaR al 95% y 99%
    var_95 = np.percentile(saldos_finales, 5)
    var_99 = np.percentile(saldos_finales, 1)
    
    # Probabilidad de saldo negativo en cualquier punto
    minimos_por_sim = np.min(trayectorias, axis=1)
    prob_deficit = (np.sum(minimos_por_sim < 0) / num_simulaciones) * 100

    return {
        "simulaciones": trayectorias,
        "var_95": var_95,
        "var_99": var_99,
        "prob_deficit": prob_deficit,
        "dias_simulacion": dias_simulacion
    }

def crear_grafica_monte_carlo(res_mc: dict):
    """Genera la visualización gráfica de trayectorias de Monte Carlo con título dinámico."""
    trayectorias = res_mc["simulaciones"]
    dias = res_mc.get("dias_simulacion", 30)
    
    fig = go.Figure()

    if trayectorias.size > 0:
        num_muestras = min(50, trayectorias.shape[0])
        for i in range(num_muestras):
            fig.add_trace(go.Scatter(
                y=trayectorias[i, :],
                mode='lines',
                line=dict(width=0.8, color='rgba(112, 17, 47, 0.15)'),
                showlegend=False,
                hoverinfo='none'
            ))

        mediana = np.median(trayectorias, axis=0)
        p5 = np.percentile(trayectorias, 5, axis=0)
        p95 = np.percentile(trayectorias, 95, axis=0)

        fig.add_trace(go.Scatter(
            y=mediana,
            mode='lines',
            name='Mediana Estocástica',
            line=dict(color='#23030D', width=3)
        ))

        fig.add_trace(go.Scatter(
            y=p5,
            mode='lines',
            name='Percentil 5% (Escenario Crítico)',
            line=dict(color='#DC2626', width=2, dash='dash')
        ))

        fig.add_trace(go.Scatter(
            y=p95,
            mode='lines',
            name='Percentil 95% (Escenario Favorable)',
            line=dict(color='#16A34A', width=2, dash='dash')
        ))

    fig.update_layout(
        title=f"<b>Simulación Monte Carlo de Liquidez ({dias} Días)</b>",
        xaxis_title="Días Proyectados",
        yaxis_title="Saldo Acumulado Proyectado ($)",
        height=380
    )
    
    return fig