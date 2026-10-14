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
from modules.styles import aplicar_estilos_css, aplicar_estilo_grafica, render_topbar_ejecutiva

load_dotenv()
init_db()

st.set_page_config(
    page_title="PluriOne | Liquidity Intelligence System",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Cargar diseño y temas visuales desde el módulo externo
aplicar_estilos_css()

# -----------------------------------------------------------------------------
# CONTROL DE AUTENTICACIÓN Y SESIÓN
# -----------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    render_login()
else:
    # -------------------------------------------------------------------------
    # DASHBOARD PRINCIPAL
    # -------------------------------------------------------------------------
    user_info = st.session_state.get("user", {"nombre": "Usuario", "rol": "Ejecutivo"})
    df_historico_db = obtener_historico_db()
    df_cartera_db = obtener_cartera_db()

    # TOPBAR EJECUTIVA (LLAMADA AL MÓDULO DE ESTILOS)
    col_hdr1, col_hdr2, col_hdr3 = st.columns([2.8, 1.2, 0.8])
    with col_hdr1:
        render_topbar_ejecutiva(user_info['nombre'], user_info['rol'])

    # Cálculo inicial para exportación en Excel a 12 meses
    df_proy_global, df_hist_actual = generar_pronostico_real(df_historico_db, dias_horizonte=365, escenario="Base")
    s_inicial_global = df_proy_global['Saldo_Acumulado'].iloc[0] if not df_proy_global.empty else 0
    res_mc_global = ejecutar_simulacion_monte_carlo(
        df_historico_db, saldo_inicial=s_inicial_global, dias_simulacion=365, num_simulaciones=1000
    )

    with col_hdr2:
        st.write("")
        try:
            bytes_excel = generar_reporte_excel(df_historico_db, df_proy_global, df_cartera_db, res_mc_global)
            st.download_button(
                label="📊 Exportar Excel",
                data=bytes_excel,
                file_name="PluriOne_Reporte_Ejecutivo_12M.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except Exception:
            st.button("📊 Exportar Excel", disabled=True, use_container_width=True)

    with col_hdr3:
        st.write("")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.rerun()

    # BANNER EXPANDIBLE DE CARGA DE DATOS
    with st.expander("📂 **Gestión de Datos: Cargar Archivo Histórico de Flujo de Caja (CSV)**", expanded=False):
        st.markdown("Suba un archivo CSV estructurado con las columnas obligatorias: `ds` (Fecha AAAA-MM-DD), `Ingresos` y `Egresos`.")
        uploaded_file = st.file_uploader("Seleccionar archivo CSV local", type=["csv"], label_visibility="collapsed")
        
        if uploaded_file is not None:
            try:
                df_upload = pd.read_csv(uploaded_file)
                if set(['ds', 'Ingresos', 'Egresos']).issubset(df_upload.columns):
                    guardar_historico_db(df_upload)
                    st.success("✅ ¡Datos históricos sincronizados con SQLite con éxito!")
                    st.rerun()
                else:
                    st.error("⚠️ El archivo CSV debe contener exactamente las columnas: 'ds', 'Ingresos' y 'Egresos'.")
            except Exception as e:
                st.error(f"Error al procesar el archivo: {e}")

    # PESTAÑAS PRINCIPALES
    tab_escenarios, tab_saldos, tab_cartera, tab_var, tab_ai = st.tabs([
        "📊 Escenarios Predictivos", "💳 Balance & Saldos", "📋 Cartera CxC / CxP", "🎲 Monte Carlo & VaR", "🤖 Asistentes IA & Soporte"
    ])

    # 1. ESCENARIOS
    with tab_escenarios:
        with st.container(border=True):
            col_ctrl1, col_ctrl2 = st.columns([2, 2])
            with col_ctrl1:
                escenario_sel = st.selectbox("Escenario Macroeconómico", ["Base", "Optimista", "Conservador"], key="sel_esc")
            with col_ctrl2:
                horizonte_sel = st.selectbox(
                    "Horizonte Temporal de Proyección",
                    [30, 60, 90, 180, 365],
                    format_func=lambda x: f"{x // 30} Meses ({x} días)" if x >= 30 else f"{x} días",
                    index=4,
                    key="sel_horiz"
                )

        df_proy_esc, _ = generar_pronostico_real(
            df_historico_db, dias_horizonte=horizonte_sel, retraso_cobro=0, escenario=escenario_sel
        )
        
        s_inicial = df_proy_esc['Saldo_Acumulado'].iloc[0] if not df_proy_esc.empty else 0
        total_cobros = df_proy_esc['Ingresos'].sum() if not df_proy_esc.empty else 0
        total_pagos = df_proy_esc['Egresos'].sum() if not df_proy_esc.empty else 0
        s_final = df_proy_esc['Saldo_Acumulado'].iloc[-1] if not df_proy_esc.empty else 0

        col_kpis, col_chart = st.columns([1.3, 4.7])

        with col_kpis:
            st.markdown(f"""
            <div class="kpi-card-v2">
                <div class="kpi-header-text">💳 SALDO INICIAL</div>
                <div class="kpi-amount-text">${s_inicial:,.2f}</div>
                <span class="status-pill pill-blue">Cierre de Caja Actual</span>
            </div>
            <div class="kpi-card-v2">
                <div class="kpi-header-text">↗ COBROS ESTIMADOS</div>
                <div class="kpi-amount-text pos">+${total_cobros:,.2f}</div>
                <span class="status-pill pill-green">Flujo Entrante ({horizonte_sel // 30 if horizonte_sel>=30 else horizonte_sel}M)</span>
            </div>
            <div class="kpi-card-v2">
                <div class="kpi-header-text">↘ PAGOS ESTIMADOS</div>
                <div class="kpi-amount-text neg">-${total_pagos:,.2f}</div>
                <span class="status-pill pill-red">Compromisos Salientes</span>
            </div>
            <div class="kpi-card-v2">
                <div class="kpi-header-text">🏁 SALDO PROYECTADO</div>
                <div class="kpi-amount-text">${s_final:,.2f}</div>
                <span class="status-pill pill-blue">Horizonte a {horizonte_sel} Días</span>
            </div>
            """, unsafe_allow_html=True)

        with col_chart:
            with st.container(border=True):
                fig_esc = crear_grafica_escenarios(df_proy_esc)
                fig_esc = aplicar_estilo_grafica(fig_esc)
                st.plotly_chart(fig_esc, use_container_width=True)

    # 2. SALDOS
    with tab_saldos:
        df_proy_saldos, _ = generar_pronostico_real(df_historico_db, dias_horizonte=horizonte_sel, escenario="Base")
        s_ini = df_proy_saldos['Saldo_Acumulado'].iloc[0] if not df_proy_saldos.empty else 0
        s_fin = df_proy_saldos['Saldo_Acumulado'].iloc[-1] if not df_proy_saldos.empty else 0

        col_kpis_s, col_chart_s = st.columns([1.3, 4.7])

        with col_kpis_s:
            st.markdown(f"""
            <div class="kpi-card-v2">
                <div class="kpi-header-text">💳 SALDO INICIAL DE APERTURA</div>
                <div class="kpi-amount-text">${s_ini:,.2f}</div>
                <span class="status-pill pill-blue">Disponible Inicial</span>
            </div>
            <div class="kpi-card-v2">
                <div class="kpi-header-text">🏁 SALDO ACUMULADO FINAL</div>
                <div class="kpi-amount-text">${s_fin:,.2f}</div>
                <span class="status-pill pill-green">Horizonte {horizonte_sel} Días</span>
            </div>
            """, unsafe_allow_html=True)

        with col_chart_s:
            with st.container(border=True):
                fig_area = crear_grafica_saldos_area(df_proy_saldos, df_hist_actual)
                fig_area = aplicar_estilo_grafica(fig_area)
                st.plotly_chart(fig_area, use_container_width=True)

    # 3. CARTERA
    with tab_cartera:
        with st.container(border=True):
            render_modulo_cartera()

    # 4. MONTE CARLO & VAR
    with tab_var:
        st.subheader(f"🎲 Simulación Estocástica de Riesgo a {horizonte_sel // 30 if horizonte_sel>=30 else horizonte_sel} Meses (Monte Carlo)")
        st.caption("Cálculo cuantitativo de volatilidad mediante 1,000 trayectorias aleatorias sobre distribuciones históricas.")

        res_mc = ejecutar_simulacion_monte_carlo(
            df_historico_db, 
            saldo_inicial=s_inicial, 
            dias_simulacion=horizonte_sel, 
            num_simulaciones=1000, 
            umbral_minimo=50000.0
        )

        col_mc1, col_mc2, col_mc3 = st.columns(3)
        with col_mc1:
            st.markdown(f"""
            <div class="kpi-card-v2">
                <div class="kpi-header-text">Value at Risk (VaR 95%)</div>
                <div class="kpi-amount-text neg">${res_mc['var_95']:,.2f} MXN</div>
                <span class="status-pill pill-red">Pérdida máxima esperada al 95% de confianza</span>
            </div>
            """, unsafe_allow_html=True)
        with col_mc2:
            st.markdown(f"""
            <div class="kpi-card-v2">
                <div class="kpi-header-text">Value at Risk (VaR 99%)</div>
                <div class="kpi-amount-text neg">${res_mc['var_99']:,.2f} MXN</div>
                <span class="status-pill pill-red">Escenario extremo (P99 de severidad)</span>
            </div>
            """, unsafe_allow_html=True)
        with col_mc3:
            pill_class = "pill-red" if res_mc['prob_iliquidez'] > 10 else "pill-green"
            st.markdown(f"""
            <div class="kpi-card-v2">
                <div class="kpi-header-text">Probabilidad de Iliquidez</div>
                <div class="kpi-amount-text">{res_mc['prob_iliquidez']:.1f}%</div>
                <span class="status-pill {pill_class}">Riesgo de saldo &lt; $50,000 MXN</span>
            </div>
            """, unsafe_allow_html=True)

        with st.container(border=True):
            fig_mc = crear_grafica_monte_carlo(res_mc, umbral_minimo=50000.0)
            fig_mc = aplicar_estilo_grafica(fig_mc)
            st.plotly_chart(fig_mc, use_container_width=True)

    # 5. IA & SOPORTE
    with tab_ai:
        col_cfo_ui, col_supp_ui = st.columns(2)
        
        with col_cfo_ui:
            with st.container(border=True):
                contexto = f"Horizonte: {horizonte_sel} días (12 meses), Saldo inicial: ${s_inicial:,.2f}, Saldo Final Estimado:${s_final:,.2f}, Escenario: {escenario_sel}"
                render_copilot(contexto)
                
        with col_supp_ui:
            with st.container(border=True):
                st.subheader("🤖 PluriBot - Soporte Técnico Virtual")
                st.caption("Asistente técnico capacitado en la arquitectura del sistema.")
                
                if "support_messages" not in st.session_state:
                    st.session_state.support_messages = [{"role": "assistant", "content": "¡Hola! 👋 Soy **PluriBot**. ¿En qué puedo ayudarte con la plataforma?"}]
                
                for msg in st.session_state.support_messages:
                    css_class = "chat-user" if msg["role"] == "user" else "chat-bot"
                    prefix = "👤 **Tú:** " if msg["role"] == "user" else "🤖 **PluriBot:** "
                    st.markdown(f'<div class="{css_class}">{prefix}{msg["content"]}</div>', unsafe_allow_html=True)
                
                if user_query := st.text_input("Consulta de soporte...", key="tab_supp_input"):
                    st.session_state.support_messages.append({"role": "user", "content": user_query})
                    bot_reply = responder_soporte_fallback(user_query)
                    st.session_state.support_messages.append({"role": "assistant", "content": bot_reply})
                    st.rerun()