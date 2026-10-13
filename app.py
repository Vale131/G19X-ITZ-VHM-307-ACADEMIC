import streamlit as st
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

from modules.risk import ejecutar_simulacion_monte_carlo, crear_grafica_monte_carlo
from modules.database import init_db, guardar_historico_db, obtener_historico_db
from modules.forecasting import generar_pronostico_real, crear_grafica_escenarios, crear_grafica_saldos_area
from modules.cxc_cxp import render_modulo_cartera
from modules.support_agent import responder_soporte_fallback
from modules.ai_copilot import render_copilot

load_dotenv()
init_db()

st.set_page_config(
    page_title="Liquidity Intelligence System | PluriOne",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS Executivos
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; color: #0F172A; font-family: 'Inter', sans-serif; }
    #MainMenu, footer, header {visibility: hidden;}

    .topbar {
        background: #FFFFFF; border-bottom: 1px solid #E2E8F0;
        padding: 12px 24px; margin: -1rem -1rem 1.5rem -1rem;
        display: flex; justify-content: space-between; align-items: center;
    }
    .brand-logo { font-size: 1.25rem; font-weight: 800; color: #1E293B; }
    .status-badge {
        background-color: #DCFCE7; color: #166534; font-size: 0.75rem;
        font-weight: 700; padding: 4px 10px; border-radius: 20px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px; background-color: #F1F5F9; padding: 6px;
        border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 1.2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px; border-radius: 8px; padding: 0px 18px;
        color: #64748B; font-weight: 600; font-size: 0.88rem; border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important; color: #4F46E5 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06) !important;
    }

    .kpi-card {
        background-color: #FFFFFF; border: 1px solid #E2E8F0;
        border-radius: 12px; padding: 14px 18px; margin-bottom: 10px;
    }
    .kpi-label { font-size: 0.72rem; font-weight: 700; color: #64748B; text-transform: uppercase; }
    .kpi-value { font-size: 1.3rem; font-weight: 800; color: #0F172A; margin-top: 2px; }
    .kpi-value.positive { color: #059669; }
    .kpi-value.negative { color: #DC2626; }

    .chat-user { background-color: #4F46E5; color: #FFF; padding: 10px 14px; border-radius: 12px 12px 2px 12px; margin-bottom: 8px; font-size: 0.88rem; }
    .chat-bot { background-color: #F1F5F9; color: #1E293B; border-left: 3px solid #4F46E5; padding: 10px 14px; border-radius: 2px 12px 12px 12px; margin-bottom: 8px; font-size: 0.88rem; }
</style>
""", unsafe_allow_html=True)

# Topbar Header
st.markdown("""
<div class="topbar">
    <div class="brand-logo">💼 PluriOne Liquidity Intelligence <span style="font-size:0.75rem; color:#64748B; font-weight:500;">v5.5 Motor Predictivo Real</span></div>
    <div><span class="status-badge">● Engine SQLite & Stat-Model Activo</span></div>
</div>
""", unsafe_allow_html=True)

# Carga de Datos y Estado
df_historico_db = obtener_historico_db()

with st.expander("📂 **Carga de Archivo Histórico (CSV de Flujo Real)**", expanded=False):
    st.markdown("Suba un archivo CSV con las columnas: `ds` (Fecha AAAA-MM-DD), `Ingresos` y `Egresos`.")
    uploaded_file = st.file_uploader("Seleccionar archivo CSV", type=["csv"])
    
    if uploaded_file is not None:
        try:
            df_upload = pd.read_csv(uploaded_file)
            if set(['ds', 'Ingresos', 'Egresos']).issubset(df_upload.columns):
                guardar_historico_db(df_upload)
                st.success("¡Datos históricos cargados y guardados en SQLite con éxito!")
                st.rerun()
            else:
                st.error("El archivo CSV debe contener exactamente las columnas: 'ds', 'Ingresos' y 'Egresos'.")
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")

st.divider()

# Navigation Tabs
tab_escenarios, tab_saldos, tab_cartera, tab_var, tab_ai = st.tabs([
    "📊 Escenarios", "💳 Saldos", "📋 Cartera CxC / CxP", "🎲 Monte Carlo & VaR", "🤖 Copiloto CFO & Soporte"
])

# PESTAÑA 1: ESCENARIOS
with tab_escenarios:
    col_sel, col_blank = st.columns([2, 4])
    with col_sel:
        escenario_sel = st.selectbox("Escenario Económico", ["Base", "Optimista", "Conservador"], key="sel_esc")

    df_proy_esc, df_hist_actual = generar_pronostico_real(
        df_historico_db, dias_horizonte=30, retraso_cobro=0, escenario=escenario_sel
    )
    
    s_inicial = df_proy_esc['Saldo_Acumulado'].iloc[0]
    total_cobros = df_proy_esc['Ingresos'].sum()
    total_pagos = df_proy_esc['Egresos'].sum()
    s_final = df_proy_esc['Saldo_Acumulado'].iloc[-1]

    col_kpi_side, col_chart_main = st.columns([1.2, 4.8])

    with col_kpi_side:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">💳 SALDO INICIAL</div>
            <div class="kpi-value">${s_inicial:,.2f}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">↗ COBROS PROYECTADOS</div>
            <div class="kpi-value positive">${total_cobros:,.2f}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">↘ PAGOS PROYECTADOS</div>
            <div class="kpi-value negative">-${total_pagos:,.2f}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">🏁 SALDO FINAL ESTIMADO</div>
            <div class="kpi-value">${s_final:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_chart_main:
        fig_esc = crear_grafica_escenarios(df_proy_esc)
        st.plotly_chart(fig_esc, use_container_width=True)

# PESTAÑA 2: SALDOS
with tab_saldos:
    df_proy_saldos, _ = generar_pronostico_real(df_historico_db, dias_horizonte=30, escenario="Base")
    s_ini = df_proy_saldos['Saldo_Acumulado'].iloc[0]
    s_fin = df_proy_saldos['Saldo_Acumulado'].iloc[-1]

    col_kpi_saldos, col_chart_saldos = st.columns([1.2, 4.8])

    with col_kpi_saldos:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">💳 SALDO INICIAL</div>
            <div class="kpi-value">${s_ini:,.2f}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">🏁 SALDO FINAL</div>
            <div class="kpi-value">${s_fin:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_chart_saldos:
        fig_area = crear_grafica_saldos_area(df_proy_saldos, df_hist_actual)
        st.plotly_chart(fig_area, use_container_width=True)

# PESTAÑA 3: CARTERA
with tab_cartera:
    render_modulo_cartera()


# PESTAÑA 4: MONTE CARLO & VAR (REAL)
with tab_var:
    st.subheader("🎲 Análisis Estocástico de Riesgo (Monte Carlo & VaR)")
    st.caption("Ejecución de 1,000 simulaciónes stocásticas sobre la volatilidad histórica de ingresos y egresos.")

    # Ejecución de la simulación con datos reales
    res_mc = ejecutar_simulacion_monte_carlo(
        df_historico_db, 
        saldo_inicial=s_inicial, 
        dias_simulacion=30, 
        num_simulaciones=1000, 
        umbral_minimo=50000.0
    )

    col_v1, col_v2, col_v3 = st.columns(3)
    col_v1.metric(
        "Value at Risk (VaR 95%)", 
        f"${res_mc['var_95']:,.2f} MXN", 
        help="Máxima pérdida o déficit esperado con un 95% de nivel de confianza."
    )
    col_v2.metric(
        "Value at Risk (VaR 99%)", 
        f"${res_mc['var_99']:,.2f} MXN", 
        help="Déficit máximo en escenario de estrés severo al 99% de confianza."
    )
    col_v3.metric(
        "Riesgo de Iliquidez", 
        f"{res_mc['prob_iliquidez']:.1f}%", 
        delta="Bajo Riesgo" if res_mc['prob_iliquidez'] < 5 else "Atención Requerida",
        delta_color="normal" if res_mc['prob_iliquidez'] < 5 else "inverse"
    )

    st.markdown("---")
    fig_mc = crear_grafica_monte_carlo(res_mc, umbral_minimo=50000.0)
    st.plotly_chart(fig_mc, use_container_width=True)

# PESTAÑA 5: ASISTENTES IA
with tab_ai:
    col_cfo, col_bot = st.columns(2)
    with col_cfo:
        contexto = f"Saldo inicial: ${s_inicial:,.2f}, Saldo Final Estimado:${s_final:,.2f}, Escenario: {escenario_sel}"
        render_copilot(contexto)
    with col_bot:
        st.subheader("🤖 PluriBot - Soporte Técnico")
        if "support_messages" not in st.session_state:
            st.session_state.support_messages = [{"role": "assistant", "content": "¡Hola! 👋 Soy **PluriBot**."}]
        for msg in st.session_state.support_messages:
            role = "🤖 PluriBot" if msg["role"] == "assistant" else "👤 Tú"
            st.markdown(f"**{role}:** {msg['content']}")
        if user_query := st.text_input("Escribe tu duda...", key="tab_supp"):
            st.session_state.support_messages.append({"role": "user", "content": user_query})
            bot_reply = responder_soporte_fallback(user_query)
            st.session_state.support_messages.append({"role": "assistant", "content": bot_reply})
            st.rerun()