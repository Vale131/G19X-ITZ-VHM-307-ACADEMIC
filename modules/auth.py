import streamlit as st
from modules.database import autenticar_usuario, registrar_usuario

def render_login():
    """Renderiza la pantalla ejecutiva con opciones de Inicio de Sesión y Registro de Usuarios."""
    
    col_left, col_center, col_right = st.columns([1, 1.8, 1])
    
    with col_center:
        st.markdown("""
        <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 28px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05); margin-top: 30px; margin-bottom: 20px;">
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="font-size: 1.6rem; font-weight: 800; color: #0F172A; margin-bottom: 6px;">💼 PluriOne Intelligence</h2>
                <p style="font-size: 0.88rem; color: #64748B;">Acceso Ejecutivo y Gestión de Usuarios</p>
            </div>
        """, unsafe_allow_html=True)
        
        tab_login, tab_register = st.tabs(["🔑 Iniciar Sesión", "📝 Crear Cuenta / Registrar Usuario"])
        
        # PESTAÑA 1: INICIAR SESIÓN
        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                email_input = st.text_input("Correo Electrónico Corporativo", placeholder="ejemplo@plurione.com")
                password_input = st.text_input("Contraseña de Acceso", type="password", placeholder="••••••••")
                
                submit_btn = st.form_submit_button("🔑 Iniciar Sesión Segura", use_container_width=True, type="primary")
                
                if submit_btn:
                    if not email_input or not password_input:
                        st.error("Por favor complete todos los campos.")
                    else:
                        user = autenticar_usuario(email_input, password_input)
                        if user:
                            st.session_state["authenticated"] = True
                            st.session_state["user"] = user
                            st.success(f"¡Bienvenido(a), {user['nombre']}!")
                            st.rerun()
                        else:
                            st.error("Credenciales incorrectas. Verifique su correo o contraseña.")

        # PESTAÑA 2: REGISTRO DE NUEVO USUARIO
        with tab_register:
            with st.form("register_form", clear_on_submit=True):
                reg_nombre = st.text_input("Nombre Completo", placeholder="Ej. Valeria ...")
                reg_email = st.text_input("Correo Electrónico", placeholder="ejemplo@plurione.com")
                reg_pass = st.text_input("Contraseña", type="password", placeholder="••••••••")
                reg_rol = st.selectbox("Rol en el Sistema", ["Director Financiero (CFO)", "Analista Financiero", "Tesorería", "Auditor Externo"])
                
                reg_btn = st.form_submit_button("📝 Registrar Usuario", use_container_width=True)
                
                if reg_btn:
                    if not reg_nombre or not reg_email or not reg_pass:
                        st.error("Por favor complete todos los campos obligatorios.")
                    else:
                        exito, msj = registrar_usuario(reg_email, reg_pass, reg_nombre, reg_rol)
                        if exito:
                            st.success(msj)
                        else:
                            st.error(msj)

        st.markdown("""
            <div style="text-align: center; margin-top: 20px; font-size: 0.75rem; color: #94A3B8;">
                Sistema de Evaluación Académica • Identificador: <b>G19X-ITZ-VHM-307-ACADEMIC</b>
            </div>
        </div>
        """, unsafe_allow_html=True)