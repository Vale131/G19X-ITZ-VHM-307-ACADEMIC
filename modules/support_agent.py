import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

SYSTEM_SUPPORT_PROMPT = """
Eres "PluriBot", el Asistente Técnico y Guía de Onboarding para la plataforma 'Liquidity Intelligence' de PluriOne S.A. de C.V.
Tu rol es brindar soporte claro, amable y didáctico con emojis sobre la carga de CSVs, configuración de parámetros y uso del sistema.
"""

def responder_soporte_fallback(query):
    q = query.lower()
    if any(k in q for k in ["csv", "archivo", "formato", "cargar"]):
        return ("📋 **Formatos CSV Requeridos:**\n\n"
                "- **Histórico:** Debe contener `ds` (fecha AAAA-MM-DD), `Ingresos` y `Egresos`.\n"
                "- **Cartera:** Debe incluir `fecha`, `monto`, `tipo` (CXC/CXP) y `probabilidad` (0.0 a 1.0).")
    elif any(k in q for k in ["var", "monte carlo", "riesgo"]):
        return ("🎲 **Simulación Monte Carlo & VaR:**\n\n"
                "Ejecuta iteraciones estocásticas para determinar la volatilidad diaria y calcular el Value at Risk al 95% y 99%.")
    elif any(k in q for k in ["sqlite", "base de datos", "guardar"]):
        return ("💾 **Persistencia de Datos:**\n\n"
                "Todos los cambios realizados en la Pestaña 3 (Cartera) se almacenan automáticamente en la base local `flujo_efectivo.db`.")
    else:
        return ("🤖 **PluriBot:** Puedo ayudarte a navegar el sistema, estructurar tus archivos de carga o entender las métricas de riesgo de la plataforma.")

def render_support_widget():
    st.sidebar.divider()
    st.sidebar.markdown("### 🤖 PluriBot Assistant")
    
    with st.sidebar.expander("💬 Soporte Técnico Interactivo", expanded=False):
        if "support_messages" not in st.session_state:
            st.session_state.support_messages = [
                {"role": "assistant", "content": "¡Hola! 👋 Soy **PluriBot**. ¿Tienes dudas sobre cómo operar la plataforma?"}
            ]

        for msg in st.session_state.support_messages:
            if msg["role"] == "assistant":
                st.markdown(f'<div class="chat-bot">🤖 <b>PluriBot:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-user">👤 <b>Tú:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)

        if user_query := st.text_input("💬 Pregunta a PluriBot...", key="side_supp_input"):
            st.session_state.support_messages.append({"role": "user", "content": user_query})
            
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key and not api_key.startswith("sk-proj-tu_clave"):
                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=api_key)
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": SYSTEM_SUPPORT_PROMPT},
                            *st.session_state.support_messages
                        ],
                        temperature=0.4
                    )
                    bot_reply = response.choices[0].message.content
                except Exception:
                    bot_reply = responder_soporte_fallback(user_query)
            else:
                bot_reply = responder_soporte_fallback(user_query)

            st.session_state.support_messages.append({"role": "assistant", "content": bot_reply})
            st.rerun()