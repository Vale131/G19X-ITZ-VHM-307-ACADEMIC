import streamlit as st
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

from modules.database import init_db, guardar_historico_db, obtener_historico_db, obtener_cartera_db
from modules.forecasting import generar_pronostico_real, crear_grafica_escenarios, crear_grafica_saldos_area
from modules.cxc_cxp import render_modulo_cartera
from modules.risk import ejecutar_simulacion_monte_carlo, crear_grafica_monte_carlo
from modules.support_agent import responder_soporte_fallback
from modules.ai_copilot import render_copilot
from modules.auth import render_login
from modules.reports import generar_reporte_excel

load_dotenv()
init_db()

st.set_page_config(
    page_title="Liquidity Intelligence System | PluriOne",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS
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

# -----------------------------------------------------------------------------
# CONTROL DE AUTENTICACIÓN Y SESIÓN
# -----------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    render_login()
else:
    # -------------------------------------------------------------------------
    # DASHBOARD PRINCIPAL (SÓLO USUARIOS AUTENTICADOS)
    # -------------------------------------------------------------------------
    user_info = st.session_state.get("user", {"nombre": "Usuario", "rol": "Ejecutivo"})
    df_historico_db = obtener_historico_db()
    df_cartera_db = obtener_cartera_db()

    # Topbar Ejecutiva
    col_tb1, col_tb2, col_tb3 = st.columns([2.5, 1.2, 0.8])
    with col_tb1:
        st.markdown(f"""
        <div class="topbar">
            <div class="brand-logo">💼 PluriOne Liquidity Intelligence <span style="font-size:0.75rem; color:#64748B; font-weight:500;">v7.5 (Horizonte 12 Meses)</span></div>
            <div>
                <span class="status-badge">● Sesión: <b>{user_info['nombre']}</b> ({user_info['rol']})</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Cálculo inicial para exportación en Excel a 12 meses
    df_proy_global, df_hist_actual = generar_pronostico_real(df_historico_db, dias_horizonte=365, escenario="Base")
    s_inicial_global = df_proy_global['Saldo_Acumulado'].iloc[0] if not df_proy_global.empty else 0
    res_mc_global = ejecutar_simulacion_monte_carlo(
        df_historico_db, saldo_inicial=s_inicial_global, dias_simulacion=365, num_simulaciones=1000
    )

    with col_tb2:
        try:
            bytes_excel = generar_reporte_excel(df_historico_db, df_proy_global, df_cartera_db, res_mc_global)
            st.download_button(
                label="📊 Exportar Excel",
                data=bytes_excel,
                file_name="PluriOne_Reporte_Anual_12Meses.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except Exception:
            st.button("📊 Exportar Excel", disabled=True, use_container_width=True)

    with col_tb3:
        if st.button("🚪 Salir", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.rerun()

    # Carga de Datos y Estado
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

    # Pestañas Principales
    tab_escenarios, tab_saldos, tab_cartera, tab_var, tab_ai = st.tabs([
        "📊 Escenarios", "💳 Saldos", "📋 Cartera CxC / CxP", "🎲 Monte Carlo & VaR", "🤖 Copiloto CFO & Soporte"
    ])

    # PESTAÑA 1: ESCENARIOS
    with tab_escenarios:
        col_sel1, col_sel2 = st.columns([2, 2])
        with col_sel1:
            escenario_sel = st.selectbox("Escenario Económico", ["Base", "Optimista", "Conservador"], key="sel_esc")
        with col_sel2:
            horizonte_sel = st.selectbox(
                "Horizonte de Proyección",
                [30, 60, 90, 180, 365],
                format_func=lambda x: f"{x // 30} Meses ({x} días)" if x >= 30 else f"{x} días",
                index=4,  # Seleccionado en 365 días (12 Meses) por defecto
                key="sel_horiz"
            )

        df_proy_esc, _ = generar_pronostico_real(
            df_historico_db, dias_horizonte=horizonte_sel, retraso_cobro=0, escenario=escenario_sel
        )
        
        s_inicial = df_proy_esc['Saldo_Acumulado'].iloc[0] if not df_proy_esc.empty else 0
        total_cobros = df_proy_esc['Ingresos'].sum() if not df_proy_esc.empty else 0
        total_pagos = df_proy_esc['Egresos'].sum() if not df_proy_esc.empty else 0
        s_final = df_proy_esc['Saldo_Acumulado'].iloc[-1] if not df_proy_esc.empty else 0

        col_kpi_side, col_chart_main = st.columns([1.2, 4.8])

        with col_kpi_side:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">💳 SALDO INICIAL</div>
                <div class="kpi-value">${s_inicial:,.2f}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">↗ COBROS PROYECTADOS ({horizonte_sel // 30 if horizonte_sel>=30 else horizonte_sel}M)</div>
                <div class="kpi-value positive">${total_cobros:,.2f}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">↘ PAGOS PROYECTADOS ({horizonte_sel // 30 if horizonte_sel>=30 else horizonte_sel}M)</div>
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
        df_proy_saldos, _ = generar_pronostico_real(df_historico_db, dias_horizonte=horizonte_sel, escenario="Base")
        s_ini = df_proy_saldos['Saldo_Acumulado'].iloc[0] if not df_proy_saldos.empty else 0
        s_fin = df_proy_saldos['Saldo_Acumulado'].iloc[-1] if not df_proy_saldos.empty else 0

        col_kpi_saldos, col_chart_saldos = st.columns([1.2, 4.8])

        with col_kpi_saldos:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">💳 SALDO INICIAL</div>
                <div class="kpi-value">${s_ini:,.2f}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">🏁 SALDO FINAL ({horizonte_sel // 30 if horizonte_sel>=30 else horizonte_sel}M)</div>
                <div class="kpi-value">${s_fin:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        with col_chart_saldos:
            fig_area = crear_grafica_saldos_area(df_proy_saldos, df_hist_actual)
            st.plotly_chart(fig_area, use_container_width=True)

    # PESTAÑA 3: CARTERA
    with tab_cartera:
        render_modulo_cartera()

    # PESTAÑA 4: MONTE CARLO & VAR
    with tab_var:
        st.subheader(f"🎲 Análisis Estocástico de Riesgo a {horizonte_sel // 30 if horizonte_sel>=30 else horizonte_sel} Meses (Monte Carlo & VaR)")
        st.caption(f"Ejecución de 1,000 simulaciones estocásticas proyectando {horizonte_sel} días sobre la volatilidad histórica de ingresos y egresos.")

        res_mc = ejecutar_simulacion_monte_carlo(
            df_historico_db, 
            saldo_inicial=s_inicial, 
            dias_simulacion=horizonte_sel, 
            num_simulaciones=1000, 
            umbral_minimo=50000.0
        )

        col_v1, col_v2, col_v3 = st.columns(3)
        col_v1.metric(f"Value at Risk (VaR 95% - {horizonte_sel} días)", f"${res_mc['var_95']:,.2f} MXN")
        col_v2.metric(f"Value at Risk (VaR 99% - {horizonte_sel} días)", f"${res_mc['var_99']:,.2f} MXN")
        col_v3.metric("Riesgo de Iliquidez", f"{res_mc['prob_iliquidez']:.1f}%")

        st.markdown("---")
        fig_mc = crear_grafica_monte_carlo(res_mc, umbral_minimo=50000.0)
        st.plotly_chart(fig_mc, use_container_width=True)

    # PESTAÑA 5: ASISTENTES IA
    with tab_ai:
        col_cfo, col_bot = st.columns(2)
        with col_cfo:
            contexto = f"Horizonte: {horizonte_sel} días (12 meses), Saldo inicial: ${s_inicial:,.2f}, Saldo Final Estimado:${s_final:,.2f}, Escenario: {escenario_sel}"
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