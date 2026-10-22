import streamlit as st
from modules.database import autenticar_usuario

def render_login():
    """Renderiza la pantalla de autenticación con un diseño ejecutivo y altamente estilizado."""
    
    # Inyección de estilos CSS exclusivos para la interfaz de acceso
    st.markdown("""
    <style>
    /* Ocultar barra lateral en pantalla de inicio de sesión */
    [data-testid="stSidebar"] {
        display: none;
    }

    /* Fondo de página de login */
    .stApp {
        background: linear-gradient(135deg, #FDFBFB 0%, #EBEDEE 100%);
    }

    /* Tarjeta Encabezado del Sistema */
    .login-header-card {
        background: linear-gradient(135deg, #23030D 0%, #6B1128 50%, #70112F 100%);
        padding: 32px 28px 26px 28px;
        border-radius: 16px 16px 0 0;
        text-align: center;
        box-shadow: 0 10px 30px rgba(35, 3, 13, 0.2);
    }

    .login-brand-title {
        font-size: 2.2rem;
        font-weight: 900;
        letter-spacing: 0.08em;
        color: #FCD34D;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);
    }

    .login-brand-sub {
        font-size: 0.78rem;
        font-weight: 700;
        color: #FFFFFF;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-top: 6px;
        opacity: 0.95;
    }

    .login-academic-badge {
        display: inline-block;
        background: rgba(252, 211, 77, 0.15);
        border: 1px solid rgba(252, 211, 77, 0.35);
        color: #FCD34D;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        margin-top: 14px;
        text-transform: uppercase;
    }

    .login-footer-info {
        text-align: center;
        font-size: 0.75rem;
        color: #6B7280;
        margin-top: 16px;
        padding-top: 12px;
        border-top: 1px dashed #E5E7EB;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1.2, 1.6, 1.2])

    with col2:
        # Encabezado Ejecutivo Principal
        st.markdown("""
        <div class="login-header-card">
            <div class="login-brand-title">// PLURIONE</div>
            <div class="login-brand-sub">Inteligencia de Liquidez & Tesorería Executive System</div>
            <div class="login-academic-badge">G19X-ITZ-VHM-307-ACADEMIC • BCRYPT ENCRYPTED</div>
        </div>
        """, unsafe_allow_html=True)

        # Formulario de Acceso Estilizado
        with st.container(border=True):
            st.markdown("""
            <div style="text-align: center; margin: 10px 0 16px 0;">
                <h4 style="color: #23030D; margin: 0; font-weight: 800; font-size: 1.15rem;">Acceso Institucional</h4>
                <p style="color: #6B1128; font-size: 0.8rem; margin-top: 3px; font-weight: 600;">Ingresa con tus credenciales corporativas autorizadas</p>
            </div>
            """, unsafe_allow_html=True)

            with st.form("form_login"):
                email_input = st.text_input("Correo Electrónico Institucional", placeholder="ejemplo@plurione.com")
                pass_input = st.text_input("Contraseña", type="password", placeholder="••••••••")
                
                st.markdown("<br>", unsafe_allow_html=True)
                btn_submit = st.form_submit_button("🔐 Iniciar Sesión de Tesorería", width="stretch")

                if btn_submit:
                    if email_input and pass_input:
                        user = autenticar_usuario(email_input.strip(), pass_input.strip())
                        if isinstance(user, dict) and "error" in user:
                            st.error(user["error"])
                        elif user:
                            st.session_state["authenticated"] = True
                            st.session_state["user"] = user
                            st.success("Acceso concedido. Sincronizando entorno...")
                            st.rerun()
                        else:
                            st.error("Credenciales incorrectas o usuario no registrado.")
                    else:
                        st.warning("Por favor ingresa tu correo y contraseña.")

            st.markdown("""
            <div class="login-footer-info">
                🔒 Conexión segura de alta confidencialidad • Cifrado de contraseña <b>bcrypt</b>
            </div>
            """, unsafe_allow_html=True)