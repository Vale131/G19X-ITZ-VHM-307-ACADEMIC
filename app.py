import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dotenv import load_dotenv

from modules.database import (
    init_db, guardar_historico_db, obtener_historico_db, 
    obtener_cartera_db, registrar_usuario, obtener_usuarios_db,
    actualizar_usuario, eliminar_usuario
)
from modules.forecasting import (
    generar_pronostico_real, calcular_metricas_error,
    crear_grafica_escenarios, crear_grafica_barras_categoria, 
    crear_grafica_saldos_area
)
from modules.cxc_cxp import render_modulo_cartera
from modules.risk import ejecutar_simulacion_monte_carlo, crear_grafica_monte_carlo
from modules.support_agent import render_support_agent
from modules.ai_copilot import render_copilot
from modules.auth import render_login
from modules.reports import generar_reporte_excel
from modules.styles import aplicar_estilos_css, aplicar_estilo_grafica

load_dotenv()
init_db()

st.set_page_config(
    page_title="PluriOne | Liquidity & Treasury Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar estilos globales
aplicar_estilos_css()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    render_login()
else:
    user_info = st.session_state.get("user", {"nombre": "Valeria (Administrador)", "rol": "Director Financiero (CFO)", "email": "admin@plurione.com"})
    df_historico_db = obtener_historico_db()
    df_cartera_db = obtener_cartera_db()

    # Determinar perfil administrador
    rol_actual = str(user_info.get('rol', '')).lower()
    email_actual = str(user_info.get('email', '')).lower()
    es_admin = ("administrador" in rol_actual) or ("cfo" in rol_actual) or (email_actual == "admin@plurione.com")

    # -------------------------------------------------------------------------
    # BARRA LATERAL DE NAVEGACIÓN
    # -------------------------------------------------------------------------
    with st.sidebar:
        st.markdown("""
        <div style="padding: 10px 0 15px 0; margin-bottom: 5px;">
            <h2 style="font-size: 1.6rem; font-weight: 800; color: #FCD34D; letter-spacing: -0.02em; margin:0;">// PLURIONE</h2>
            <p style="font-size: 0.72rem; color: #FFFFFF; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; margin: 4px 0 0 0;">INTELIGENCIA DE LIQUIDEZ</p>
        </div>
        """, unsafe_allow_html=True)

        nombre_user = user_info.get('nombre', 'Usuario')
        rol_user = user_info.get('rol', 'Usuario')
        inicial = nombre_user[0].upper() if nombre_user else 'U'

        st.markdown(f"""
        <div class="sidebar-user-card">
            <div class="sidebar-user-avatar">{inicial}</div>
            <div>
                <div class="sidebar-user-name">{nombre_user}</div>
                <div class="sidebar-user-role">{rol_user}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<p style='font-size:0.75rem; font-weight:800; color:#FCD34D; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:8px;'>NAVEGACIÓN</p>", unsafe_allow_html=True)

        opciones_menu = [
            "🖼️  Cockpit Financiero",
            "💳  Saldos & Tesorería",
            "📋  Capital de Trabajo & Cartera",
            "🎲  Modelado Estocástico & VaR",
            "🎧  Centro de Inteligencia & IA"
        ]

        if es_admin:
            opciones_menu.append("👥  Gestión de Usuarios")

        menu_opcion = st.radio(
            "Navegación",
            opciones_menu,
            key="navigation_radio",
            label_visibility="collapsed"
        )

        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 20px 0 14px 0;'>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.75rem; font-weight:800; color:#FCD34D; text-transform:uppercase; letter-spacing:0.06em;'>CONFIGURACIÓN</p>", unsafe_allow_html=True)

        escenario_sel = st.selectbox("Escenario de Estrategia", ["Base", "Optimista", "Conservador"], key="sb_esc_fix")
        horizonte_sel = st.selectbox(
            "Horizonte Temporal",
            [30, 60, 90, 180, 365],
            format_func=lambda x: f"{x // 30} Meses ({x}d)" if x >= 30 else f"{x} días",
            index=4,
            key="sb_horiz_fix"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Generar pronóstico pasando la cartera unificada
        df_proy_global, df_hist_actual = generar_pronostico_real(
            df_historico_db, df_cartera_db, dias_horizonte=horizonte_sel, escenario=escenario_sel
        )
        s_inicial_global = df_proy_global['Saldo_Acumulado'].iloc[0] if not df_proy_global.empty else 0
        res_mc_global = ejecutar_simulacion_monte_carlo(
            df_historico_db, saldo_inicial=s_inicial_global, dias_simulacion=horizonte_sel, num_simulaciones=1000
        )

        try:
            bytes_excel = generar_reporte_excel(df_historico_db, df_proy_global, df_cartera_db, res_mc_global)
            st.download_button(
                label="⬇ Exportar Reporte Excel",
                data=bytes_excel,
                file_name=f"PluriOne_Reporte_{horizonte_sel}D.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except Exception:
            st.button("⬇ Exportar Reporte Excel", disabled=True, use_container_width=True)

        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.rerun()

    # -------------------------------------------------------------------------
    # VISTAS PRINCIPALES DEL SISTEMA
    # -------------------------------------------------------------------------
    
    # 1. COCKPIT FINANCIERO
    if "Cockpit Financiero" in menu_opcion:
        col_t, col_s = st.columns([3, 1])
        with col_t:
            st.markdown('<div style="font-size: 1.6rem; font-weight: 800; color: #23030D;">Executive Financial Cockpit & Cash Performance</div>', unsafe_allow_html=True)
        with col_s:
            st.caption(f"Horizonte: **{horizonte_sel} días** • Escenario: **{escenario_sel}**")

        with st.expander("Sincronizar Archivo Histórico de Flujo (CSV)", expanded=False):
            uploaded_file = st.file_uploader("Seleccionar CSV", type=["csv"], label_visibility="collapsed")
            if uploaded_file is not None:
                try:
                    df_upload = pd.read_csv(uploaded_file)
                    if set(['ds', 'Ingresos', 'Egresos']).issubset(df_upload.columns):
                        guardar_historico_db(df_upload)
                        st.success("Sincronizado con SQLite correctamente")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error al procesar CSV: {e}")

        df_proy, _ = generar_pronostico_real(
            df_historico_db, df_cartera_db, dias_horizonte=horizonte_sel, escenario=escenario_sel
        )
        
        # Evaluación del modelo
        metricas_err = calcular_metricas_error(df_historico_db)

        tot_rev = df_proy['Ingresos'].sum()
        tot_exp = df_proy['Egresos'].sum()
        s_fin = df_proy['Saldo_Acumulado'].iloc[-1] if not df_proy.empty else 0
        net_margin = ((tot_rev - tot_exp) / tot_rev * 100) if tot_rev > 0 else 0

        # Tarjetas Principales de Desempeño
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f'<div class="kpi-card-ref"><div class="kpi-icon-badge">REV</div><div class="kpi-title-ref">Total Revenue</div><div class="kpi-value-ref">${tot_rev:,.2f}</div></div>', unsafe_allow_html=True)
        with k2:
            st.markdown(f'<div class="kpi-card-ref"><div class="kpi-icon-badge">FLOW</div><div class="kpi-title-ref">Net Cash Flow</div><div class="kpi-value-ref">${(tot_rev - tot_exp):,.2f}</div></div>', unsafe_allow_html=True)
        with k3:
            st.markdown(f'<div class="kpi-card-ref"><div class="kpi-icon-badge">MARG</div><div class="kpi-title-ref">Operating Margin</div><div class="kpi-value-ref">{net_margin:.1f}%</div></div>', unsafe_allow_html=True)
        with k4:
            st.markdown(f'<div class="kpi-card-ref"><div class="kpi-icon-badge">BAL</div><div class="kpi-title-ref">Closing Balance</div><div class="kpi-value-ref">${s_fin:,.2f}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # SECCIÓN DE PRECISIÓN Y EVALUACIÓN DEL MODELO
        c_acc1, c_acc2 = st.columns([1, 1])
        with c_acc1:
            with st.container(border=True):
                st.markdown("##### **Precisión del Modelo Predictivo (MAE / MAPE)**")
                st.caption(f"Validación mediante Holdout sobre datos históricos reales: *{metricas_err['status']}*")
                m_a, m_b = st.columns(2)
                with m_a:
                    st.metric(label="MAE (Error Absoluto Medio)", value=f"${metricas_err['mae']:,.2f}")
                with m_b:
                    st.metric(label="MAPE (Error Porcentual)", value=f"{metricas_err['mape']:.2f}%")
        
        with c_acc2:
            with st.container(border=True):
                st.markdown("##### **Integración de Cartera en Proyección**")
                cxc_activas = len(df_cartera_db[df_cartera_db['tipo'].str.contains('CxC|Cobro', case=False, na=False)]) if not df_cartera_db.empty else 0
                cxp_activas = len(df_cartera_db[df_cartera_db['tipo'].str.contains('CxP|Pago', case=False, na=False)]) if not df_cartera_db.empty else 0
                st.caption("Cuentas por cobrar y por pagar integradas automáticamente ponderadas por probabilidad.")
                p_a, p_b = st.columns(2)
                with p_a:
                    st.metric(label="Cobros Pendientes (CxC)", value=f"{cxc_activas} registros")
                with p_b:
                    st.metric(label="Pagos Pendientes (CxP)", value=f"{cxp_activas} registros")

        st.markdown("<br>", unsafe_allow_html=True)

        col_g1, col_g2 = st.columns([3.8, 2.2])
        with col_g1:
            with st.container(border=True):
                fig_esc = crear_grafica_escenarios(df_proy)
                fig_esc = aplicar_estilo_grafica(fig_esc)
                st.plotly_chart(fig_esc, use_container_width=True)

        with col_g2:
            with st.container(border=True):
                fig_bar = crear_grafica_barras_categoria(df_proy)
                fig_bar = aplicar_estilo_grafica(fig_bar)
                st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_t1, col_t2 = st.columns([4, 2])
        with col_t1:
            with st.container(border=True):
                st.markdown("##### **Transacciones Recientes & Proyección de Flujo**")
                df_tabla_demo = df_proy[['ds', 'Ingresos', 'Egresos', 'Saldo_Acumulado']].head(6).copy()
                df_tabla_demo['ds'] = df_tabla_demo['ds'].dt.strftime('%d %b, %Y')
                df_tabla_demo.columns = ['Fecha', 'Ingresos ($)', 'Egresos ($)', 'Saldo ($)']
                st.dataframe(df_tabla_demo, use_container_width=True, hide_index=True)

        with col_t2:
            with st.container(border=True):
                st.markdown("##### **Distribución de Cobertura**")
                fig_donut = go.Figure(data=[go.Pie(
                    labels=['Ingresos Proyectados', 'Egresos Estimados'],
                    values=[tot_rev, tot_exp],
                    hole=.65,
                    marker_colors=['#70112F', '#FCD34D']
                )])
                fig_donut.update_layout(height=210, margin=dict(l=10, r=10, t=10, b=10), showlegend=True, paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_donut, use_container_width=True)

    # 2. SALDOS & TESORERÍA
    elif "Saldos & Tesorería" in menu_opcion:
        st.subheader("Estrategia de Liquidez & Saldos Acumulados")
        df_proy_saldos, _ = generar_pronostico_real(
            df_historico_db, df_cartera_db, dias_horizonte=horizonte_sel, escenario=escenario_sel
        )
        with st.container(border=True):
            fig_area = crear_grafica_saldos_area(df_proy_saldos)
            fig_area = aplicar_estilo_grafica(fig_area)
            st.plotly_chart(fig_area, use_container_width=True)

    # 3. CAPITAL DE TRABAJO & CARTERA
    elif "Capital de Trabajo & Cartera" in menu_opcion:
        with st.container(border=True):
            render_modulo_cartera()

    # 4. MODELADO ESTOCÁSTICO & VAR
    elif "Modelado Estocástico & VaR" in menu_opcion:
        st.subheader(f"Simulación Estocástica de Riesgo Financiero (Monte Carlo a {horizonte_sel} días)")
        res_mc = ejecutar_simulacion_monte_carlo(
            df_historico_db, saldo_inicial=s_inicial_global, dias_simulacion=horizonte_sel
        )
        
        # Tarjetas de Riesgo VaR
        k_v1, k_v2, k_v3 = st.columns(3)
        with k_v1:
            st.metric("Value at Risk (VaR 95%)", f"${res_mc['var_95']:,.2f}")
        with k_v2:
            st.metric("Value at Risk (VaR 99%)", f"${res_mc['var_99']:,.2f}")
        with k_v3:
            st.metric("Probabilidad de Déficit", f"{res_mc['prob_deficit']:.2f}%")

        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            fig_mc = crear_grafica_monte_carlo(res_mc)
            fig_mc = aplicar_estilo_grafica(fig_mc)
            st.plotly_chart(fig_mc, use_container_width=True)

    # 5. CENTRO DE INTELIGENCIA & IA
    elif "Centro de Inteligencia & IA" in menu_opcion:
        col_cfo, col_supp = st.columns(2)
        with col_cfo:
            with st.container(border=True):
                contexto = f"Horizonte: {horizonte_sel} días, Saldo inicial: ${s_inicial_global:,.2f}"
                render_copilot(contexto)
        with col_supp:
            with st.container(border=True):
                render_support_agent()

    # 6. GESTIÓN DE USUARIOS
    elif "Gestión de Usuarios" in menu_opcion and es_admin:
        st.subheader("Administración de Accesos & Usuarios Institucionales")
        st.caption("Gestión directa de usuarios con buscador en tiempo real y edición interactiva.")

        tab_lista, tab_crear = st.tabs(["🔍 Buscador y Directorio de Usuarios", "➕ Dar de Alta Usuario"])

        with tab_lista:
            df_u = obtener_usuarios_db()
            if not df_u.empty:
                col_busc, col_filtro = st.columns([3, 1])
                with col_busc:
                    busqueda = st.text_input(
                        "🔍 Buscador de Usuarios",
                        placeholder="Escribe para buscar por Nombre, Correo, Rol o ID...",
                        key="input_direct_search_user"
                    )
                with col_filtro:
                    filtro_estatus = st.selectbox("Estatus", ["Todos", "Activo", "Inactivo"], key="sb_filtro_direct_status")

                df_filtrado = df_u.copy()
                if busqueda.strip():
                    b = busqueda.lower().strip()
                    df_filtrado = df_filtrado[
                        df_filtrado['nombre'].str.lower().str.contains(b) |
                        df_filtrado['email'].str.lower().str.contains(b) |
                        df_filtrado['id'].astype(str).str.contains(b) |
                        df_filtrado['rol'].str.lower().str.contains(b)
                    ]
                
                if filtro_estatus != "Todos":
                    df_filtrado = df_filtrado[df_filtrado['estatus'] == filtro_estatus]

                st.markdown(f"**Resultados encontrados ({len(df_filtrado)} usuarios):**")

                if not df_filtrado.empty:
                    for idx, row in df_filtrado.iterrows():
                        u_id = row['id']
                        u_nombre = row['nombre']
                        u_email = row['email']
                        u_rol = row['rol']
                        u_estatus = row['estatus']

                        badge_html = (
                            f'<span class="badge-activo">● Activo</span>'
                            if u_estatus == "Activo" 
                            else f'<span class="badge-inactivo">● Inactivo</span>'
                        )

                        with st.expander(f"{'🟢' if u_estatus=='Activo' else '🔴'} #{u_id} | {u_nombre} — {u_email} ({u_rol})", expanded=False):
                            c_edit, c_del = st.columns([2, 1])

                            with c_edit:
                                with st.form(f"form_direct_edit_user_{u_id}"):
                                    st.markdown(f"##### **Editar perfil de:** {u_nombre}")
                                    e_email = st.text_input("Correo Electrónico", value=u_email, key=f"e_mail_{u_id}")
                                    e_nombre = st.text_input("Nombre Completo", value=u_nombre, key=f"e_nom_{u_id}")
                                    
                                    # Selección dinámica de rol preservando la opción previa
                                    roles_opciones = ["Director Financiero (CFO)", "Analista de Tesorería", "Auditor de Riesgo"]
                                    if "CFO" in u_rol or "Director" in u_rol:
                                        idx_rol = 0
                                    elif "Auditor" in u_rol:
                                        idx_rol = 2
                                    else:
                                        idx_rol = 1

                                    e_rol = st.selectbox("Rol Asignado", roles_opciones, index=idx_rol, key=f"e_rol_{u_id}")
                                    
                                    e_estatus = st.radio(
                                        "Estatus de Acceso:",
                                        ["Activo", "Inactivo"],
                                        index=0 if u_estatus == "Activo" else 1,
                                        horizontal=True,
                                        key=f"e_est_{u_id}"
                                    )
                                    e_pass = st.text_input("Nueva Contraseña (dejar en blanco para conservar actual)", type="password", key=f"e_pass_{u_id}")

                                    btn_guardar = st.form_submit_button("💾 Guardar Cambios", use_container_width=True)

                                    if btn_guardar:
                                        ok, msg = actualizar_usuario(u_id, e_email, e_nombre, e_rol, e_estatus, e_pass)
                                        if ok:
                                            st.success(msg)
                                            st.rerun()
                                        else:
                                            st.error(msg)

                            with c_del:
                                st.markdown("##### **Acciones de Cuenta**")
                                st.markdown(f"**Estatus:** {badge_html}", unsafe_allow_html=True)
                                st.markdown("<br>", unsafe_allow_html=True)
                                
                                if u_id == user_info.get('id') or u_email == "admin@plurione.com":
                                    st.info("ℹ️ Cuenta principal protegida.")
                                else:
                                    if st.button("🗑️ Eliminar Usuario", key=f"btn_direct_del_{u_id}", use_container_width=True):
                                        ok, msg = eliminar_usuario(u_id)
                                        if ok:
                                            st.success(msg)
                                            st.rerun()
                                        else:
                                            st.error(msg)
                else:
                    st.warning("🔍 No se encontraron usuarios que coincidan con la búsqueda.")
            else:
                st.info("No hay usuarios registrados en el sistema.")

        with tab_crear:
            with st.form("form_alta_usuario_direct"):
                st.markdown("##### **Registrar Nuevo Usuario**")
                col_a, col_b = st.columns(2)
                with col_a:
                    u_email = st.text_input("Correo Electrónico Institucional")
                    u_nombre = st.text_input("Nombre Completo")
                with col_b:
                    u_pass = st.text_input("Contraseña de Acceso", type="password")
                    u_rol = st.selectbox("Rol Asignado", ["Director Financiero (CFO)", "Analista de Tesorería", "Auditor de Riesgo"])
                
                u_estatus = st.radio("Estatus Inicial", ["Activo", "Inactivo"], horizontal=True)

                btn_crear = st.form_submit_button("✨ Dar de Alta Usuario", use_container_width=True)

                if btn_crear:
                    if u_email and u_nombre and u_pass:
                        ok, msg = registrar_usuario(u_email, u_pass, u_nombre, u_rol, u_estatus)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("Por favor completa los campos requeridos (Correo, Nombre y Contraseña).")