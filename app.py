"""
⚡ Sistema Predictivo & Prescriptivo de Flujo de Efectivo — PluriOne S.A. de C.V.
Versión 4.2 — Suite Empresarial (6 Pilares Técnicos)
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Importar módulos de los 6 Pilares
from modules.forecasting import (
    regresores_nominas, 
    entrenar_prophet, 
    calcular_metricas_backtesting, 
    simulacion_monte_carlo
)
from modules.ai_copilot import render_copilot
from modules.support_agent import render_support_widget

# =============================================================================
# CONFIGURACIÓN Y ESTILOS
# =============================================================================
st.set_page_config(page_title="Liquidity Intelligence | PluriOne", page_icon="⚡", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html, body, [data-testid="stAppViewContainer"] { font-family: 'Inter', sans-serif; background: #f4f6fb; }
.hero { background: linear-gradient(135deg, #0b1f4b 0%, #14337f 55%, #0068c9 100%); border-radius: 18px; padding: 25px 35px; color: white; margin-bottom: 20px; }
.hero h1 { font-size: 1.8rem; font-weight: 800; margin: 0; }
.kpi { background: white; border-radius: 14px; padding: 18px; box-shadow: 0 4px 14px rgba(11,31,75,.07); border-top: 4px solid #0068c9; }
.kpi .label { font-size: .75rem; color: #7a8699; text-transform: uppercase; font-weight: 600; }
.kpi .value { font-size: 1.4rem; font-weight: 800; color: #0b1f4b; margin: 4px 0; }
.section { background: white; border-radius: 16px; padding: 22px; box-shadow: 0 4px 14px rgba(11,31,75,.07); margin-top: 15px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>⚡ Liquidity Intelligence System</h1>
    <p>PluriOne S.A. de C.V. · Develop Talent & Technology · Suite Empresarial v4.2</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# BARRA LATERAL (CONTROLES GENERALES + PILAR 6: PLURIBOT)
# =============================================================================
st.sidebar.header("🎛️ Centro de Control")
horizonte = st.sidebar.slider("Horizonte de Pronóstico (Días)", 30, 180, 90, 10)
escenario = st.sidebar.radio("Escenario de Mercado", ["Conservador (Base)", "Optimista (+15% ventas)", "Pesimista (-20% ventas)"])
retraso_cxc = st.sidebar.slider("Retraso en Cobranza (Días)", 0, 30, 5)
variacion_egresos = st.sidebar.slider("Variación en Costos (%)", -10, 30, 0)
saldo_inicial = st.sidebar.number_input("Saldo Inicial en Caja ($ MXN)", value=120000.0, step=5000.0)
umbral_seguridad = st.sidebar.number_input("Umbral Mínimo de Seguridad ($ MXN)", value=50000.0, step=5000.0)

# Carga de datos base
@st.cache_data
def cargar_datos_base():
    fechas = pd.date_range(end=datetime.today() - timedelta(days=1), periods=365, freq="D")
    np.random.seed(101)
    base_i = 18000 + np.sin(np.arange(365)/10)*4000 + (np.arange(365) % 15 == 0)*12000
    base_e = 13000 + np.cos(np.arange(365)/10)*3000 + (np.arange(365) % 30 == 0)*15000
    ing = np.random.normal(base_i, 2500).clip(4000)
    egr = np.random.normal(base_e, 1800).clip(3000)
    return pd.DataFrame({"ds": fechas, "Ingresos": ing, "Egresos": egr, "y": ing - egr})

df_hist = cargar_datos_base()
reg_hist = regresores_nominas(df_hist["ds"])
modelo = entrenar_prophet(df_hist, reg_hist)

# Cálculo de Proyección
futuro = modelo.make_future_dataframe(periods=horizonte)
reg_fut = regresores_nominas(futuro["ds"])
forecast = modelo.predict(futuro.merge(reg_fut, on="ds"))

factor_ing = 1.15 if "Optimista" in escenario else (0.80 if "Pesimista" in escenario else 1.0)
factor_egr = 1.0 + variacion_egresos/100.0
mask_fut = forecast["ds"] > df_hist["ds"].max()

for col in ["yhat", "yhat_lower", "yhat_upper"]:
    forecast.loc[mask_fut, col] *= factor_ing * (2.0 - factor_egr)

def desplazar(arr, n):
    return arr if n == 0 else np.concatenate([np.zeros(n), arr])[:len(arr)]

yhat_fut = desplazar(forecast.loc[mask_fut, "yhat"].values, retraso_cxc)
yhat_low = desplazar(forecast.loc[mask_fut, "yhat_lower"].values, retraso_cxc)
yhat_upp = desplazar(forecast.loc[mask_fut, "yhat_upper"].values, retraso_cxc)

saldo_actual = saldo_inicial + df_hist["y"].cumsum().iloc[-1]
fechas_fut = forecast.loc[mask_fut, "ds"].values
saldo_proj = saldo_actual + np.cumsum(yhat_fut)
saldo_proj_low = saldo_actual + np.cumsum(yhat_low)
saldo_proj_upp = saldo_actual + np.cumsum(yhat_upp)

minimo_proyectado = saldo_proj.min()
dias_deficit = int((saldo_proj < 0).sum())

# Integración del Pilar 6 en la barra lateral
render_support_widget()

# =============================================================================
# ESTRUCTURA DE PESTAÑAS (TABS)
# =============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard & Simulador", 
    "📂 Gestión de Cartera (CxC/CxP)", 
    "🎲 Monte Carlo & Riesgo (VaR)", 
    "💬 Copiloto CFO (IA)", 
    "📑 Reportes & Exportación"
])

# -----------------------------------------------------------------------------
# TAB 1: DASHBOARD PRINCIPAL
# -----------------------------------------------------------------------------
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="kpi"><div class="label">Saldo Actual</div><div class="value">${saldo_actual:,.0f} MXN</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="kpi"><div class="label">Proyección ({horizonte}d)</div><div class="value">${saldo_proj[-1]:,.0f} MXN</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="kpi"><div class="label">Punto Mínimo</div><div class="value">${minimo_proyectado:,.0f} MXN</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="kpi"><div class="label">Días Déficit</div><div class="value">{dias_deficit} Días</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📈 Curva de Liquidez Proyectada (Prophet IA)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(fechas_fut) + list(fechas_fut)[::-1], y=list(saldo_proj_upp) + list(saldo_proj_low)[::-1], fill="toself", fillcolor="rgba(0,104,201,0.12)", line=dict(color="rgba(255,255,255,0)"), name="IC 95%"))
    fig.add_trace(go.Scatter(x=fechas_fut, y=saldo_proj, name="Proyección", line=dict(color="#0068c9", width=3)))
    fig.add_hline(y=umbral_seguridad, line_dash="dash", line_color="#f5a623", annotation_text="Umbral Mínimo")
    fig.update_layout(template="plotly_white", height=420)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 2: CARTERA DINÁMICA
# -----------------------------------------------------------------------------
with tab2:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📋 Cartera Documentada y Editor de Facturas")
    st.info("Sube un CSV o gestiona las facturas por cobrar (CXC) y por pagar (CXP) para incorporar cobros puntuales en el modelo.")
    archivo_cxc = st.file_uploader("Cargar Cartera (CSV: fecha, monto, tipo, probabilidad)", type=["csv"], key="cartera_tab")
    if archivo_cxc:
        df_c = pd.read_csv(archivo_cxc)
        st.dataframe(df_c, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 3: PILAR 2 (MONTE CARLO & VaR DE LIQUIDEZ) + QA
# -----------------------------------------------------------------------------
with tab3:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("🎲 Simulación Monte Carlo & Value at Risk (VaR)")
    st.caption("1,000 iteraciones estocásticas para evaluar la volatilidad del flujo y el riesgo de liquidez.")
    
    std_diaria = df_hist["y"].std()
    sims, var_95, var_99, p_iliquidez = simulacion_monte_carlo(saldo_actual, yhat_fut, std_diaria)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Probabilidad de Iliquidez", f"{p_iliquidez}%", "Crítico" if p_iliquidez > 10 else "Bajo Control", delta_color="inverse")
    m2.metric("VaR 95% (Mínimo Esperado)", f"${var_95:,.2f} MXN")
    m3.metric("VaR 99% (Escenario Extremo)", f"${var_99:,.2f} MXN")

    # Gráfica de abanico Monte Carlo
    fig_mc = go.Figure()
    for i in range(min(50, len(sims))):
        fig_mc.add_trace(go.Scatter(x=fechas_fut, y=sims[i], mode='lines', line=dict(width=0.5, color='rgba(0,104,201,0.1)'), showlegend=False))
    fig_mc.add_trace(go.Scatter(x=fechas_fut, y=saldo_proj, name="Mediana Proyectada", line=dict(color='#ff2b2b', width=2.5)))
    fig_mc.update_layout(title="Muestra de 50 Iteraciones Estocásticas", template="plotly_white", height=380)
    st.plotly_chart(fig_mc, use_container_width=True)

    st.divider()
    st.subheader("🎯 Métricas de Precisión QA (Backtesting)")
    mape, rmse = calcular_metricas_backtesting(df_hist)
    if mape:
        q1, q2 = st.columns(2)
        q1.metric("MAPE (Error Absoluto Medio)", f"{mape}%", "Excelente (<15%)" if mape < 15 else "Aceptable")
        q2.metric("RMSE (Error Cuadrático Medio)", f"${rmse:,.2f} MXN")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 4: PILAR 5 (COPILOTO CFO IA)
# -----------------------------------------------------------------------------
with tab4:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    contexto = f"Saldo actual: ${saldo_actual:,.0f}, mínimo proyectado: ${minimo_proyectado:,.0f}, días déficit: {dias_deficit}, p_iliquidez: {p_iliquidez}%, escenario: {escenario}."
    render_copilot(contexto)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 5: EXPORTACIÓN
# -----------------------------------------------------------------------------
with tab5:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("⬇️ Exportación de Pronósticos Estratégicos")
    df_out = pd.DataFrame({
        "fecha": fechas_fut,
        "flujo_neto_proyectado": yhat_fut,
        "saldo_proyectado": saldo_proj,
        "saldo_limite_inferior_ic95": saldo_proj_low,
        "saldo_limite_superior_ic95": saldo_proj_upp
    })
    st.dataframe(df_out.head(10), use_container_width=True)
    st.download_button("Descargar Informe Consolidado (CSV)", df_out.to_csv(index=False), "pronostico_flujo_efectivo_v4.csv", "text/csv")
    st.markdown('</div>', unsafe_allow_html=True)