import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

SYSTEM_SUPPORT_PROMPT = """
Eres "PluriBot", el Asistente Técnico y Guía de Onboarding para la plataforma 'Liquidity Intelligence' de PluriOne S.A. de C.V.
Tu rol es brindar soporte sobre el uso técnico del software, formatos CSV, conceptos de Meta Prophet, VaR y Monte Carlo.
"""

def responder_soporte_fallback(query):
    q = query.lower()
    if any(k in q for k in ["csv", "archivo", "formato"]):
        return ("📋 **Estructura Requerida de Archivos CSV:**\n\n"
                "- **Histórico:** Columnas `ds` (fecha AAAA-MM-DD), `Ingresos` y `Egresos`.\n"
                "- **Cartera:** Columnas `fecha`, `monto`, `tipo` (CXC o CXP) y `probabilidad` (0.0 a 1.0).")
    elif any(k in q for k in ["var", "monte carlo", "riesgo"]):
        return ("🎲 **Simulador Monte Carlo & VaR:**\n\n"
                "Ejecuta 1,000 iteraciones estocásticas para medir la volatilidad y calcular el Value at Risk al 95% y 99%.")
    else:
        return ("🤖 **PluriBot:** Puedo ayudarte con la carga de archivos, configuración de la barra lateral e interpretación de métricas de riesgo.")

def render_support_widget():
    st.sidebar.divider()
    st.sidebar.subheader("❓ ¿Dudas sobre el sistema?")
    
    with st.sidebar.expander("💬 PluriBot - Soporte Técnico", expanded=False):
        if "support_messages" not in st.session_state:
            st.session_state.support_messages = [
                {"role": "assistant", "content": "¡Hola! 👋 Soy **PluriBot**. ¿Tienes alguna duda sobre la plataforma?"}
            ]

        for msg in st.session_state.support_messages:
            role_label = "🤖 PluriBot" if msg["role"] == "assistant" else "👤 Tú"
            st.markdown(f"**{role_label}:** {msg['content']}")

        if user_query := st.text_input("Escribe tu pregunta sobre la app...", key="support_input"):
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