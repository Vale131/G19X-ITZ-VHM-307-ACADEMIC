import streamlit as st
from modules.database import autenticar_usuario

def render_login():
    """Renderiza la pantalla de autenticación exclusivamente para inicio de sesión."""
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.container(border=True):
            st.markdown("""
            <div style="text-align: center; padding: 15px 0 10px 0;">
                <h1 style="color: #23030D; margin-bottom: 2px; font-weight: 800;">PLURIONE</h1>
                <p style="color: #6B1128; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">
                    Inteligencia de Liquidez & Tesorería
                </p>
            </div>
            """, unsafe_allow_html=True)

            with st.form("form_login"):
                st.markdown("##### **Acceso al Sistema**")
                email_input = st.text_input("Correo Electrónico Institucional", placeholder="ejemplo@plurione.com")
                pass_input = st.text_input("Contraseña", type="password", placeholder="••••••••")
                btn_submit = st.form_submit_button("🚪 Iniciar Sesión", use_container_width=True)

                if btn_submit:
                    if email_input and pass_input:
                        user = autenticar_usuario(email_input.strip(), pass_input.strip())
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