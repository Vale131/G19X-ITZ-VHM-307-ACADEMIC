import streamlit as st
from modules.database import autenticar_usuario, registrar_usuario

def render_login():
    """Renderiza la pantalla de autenticación y registro seguro."""
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.container(border=True):
            st.markdown("""
            <div style="text-align: center; padding: 10px 0;">
                <h1 style="color: #23030D; margin-bottom: 0;">PLURIONE</h1>
                <p style="color: #6B1128; font-weight: 700; font-size: 0.85rem; text-transform: uppercase;">
                    Plataforma de Inteligencia de Liquidez & Tesorería
                </p>
            </div>
            """, unsafe_allow_html=True)

            tab_ingreso, tab_registro = st.tabs(["🔐 Iniciar Sesión", "📝 Solicitar Registro"])

            with tab_ingreso:
                with st.form("form_login"):
                    email_input = st.text_input("Correo Institucional", placeholder="ejemplo@plurione.com")
                    pass_input = st.text_input("Contraseña", type="password")
                    btn_submit = st.form_submit_button("Ingresar al Sistema", use_container_width=True)

                    if btn_submit:
                        if email_input and pass_input:
                            user = autenticar_usuario(email_input, pass_input)
                            if isinstance(user, dict) and "error" in user:
                                st.error(user["error"])
                            elif user:
                                st.session_state["authenticated"] = True
                                st.session_state["user"] = user
                                st.success("Acceso concedido.")
                                st.rerun()
                            else:
                                st.error("Credenciales incorrectas o usuario no registrado.")
                        else:
                            st.warning("Por favor ingresa tu correo y contraseña.")

            with tab_registro:
                with st.form("form_registro_publico"):
                    reg_email = st.text_input("Correo Institucional")
                    reg_nombre = st.text_input("Nombre Completo")
                    reg_pass = st.text_input("Contraseña", type="password")
                    # Restricción: El registro público NO permite auto-asignarse el rol de CFO/Administrador
                    reg_rol = st.selectbox("Rol Operativo", ["Analista de Tesorería", "Auditor de Riesgo"])

                    btn_reg = st.form_submit_button("Enviar Solicitud", use_container_width=True)

                    if btn_reg:
                        if reg_email and reg_nombre and reg_pass:
                            ok, msg = registrar_usuario(reg_email, reg_pass, reg_nombre, reg_rol, estatus="Activo")
                            if ok:
                                st.success("Registro completado con éxito. Ahora puedes iniciar sesión.")
                            else:
                                st.error(msg)
                        else:
                            st.warning("Completa todos los campos obligatorios.")