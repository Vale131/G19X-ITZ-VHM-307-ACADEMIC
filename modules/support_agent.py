import streamlit as st
from openai import OpenAI

SYSTEM_SUPPORT_PROMPT = """
Eres "PluriBot", el Asistente Técnico y Guía de Onboarding para la plataforma 'Liquidity Intelligence' de PluriOne S.A. de C.V.

Tu rol exclusivo es brindar soporte sobre el funcionamiento técnico de la aplicación:
1. Explicar cómo usar la barra lateral (sliders de retraso de cobranza, escenarios, umbral de seguridad).
2. Guiar en la estructura de archivos CSV (Histórico: ds, Ingresos, Egresos | Cartera: fecha, monto, tipo, probabilidad).
3. Explicar conceptos técnicos: Intervalo de confianza de Prophet, MAPE/RMSE, VaR de liquidez, Simulación Monte Carlo y Semáforo de riesgo.
4. Redirigir al usuario al "Copiloto CFO (Pestaña 4)" si realiza preguntas de estrategia financiera pura.

Responde de forma amable, clara, concisa, usando viñetas y emojis.
"""

def render_support_widget():
    st.sidebar.divider()
    st.sidebar.subheader("❓ ¿Dudas sobre el sistema?")
    
    with st.sidebar.expander("💬 PluriBot - Soporte y Guía", expanded=False):
        if "support_messages" not in st.session_state:
            st.session_state.support_messages = [
                {"role": "assistant", "content": "¡Hola! 👋 Soy **PluriBot**. Te puedo ayudar a entender cómo cargar tus archivos, ajustar parámetros o interpretar las métricas."}
            ]

        for msg in st.session_state.support_messages:
            role_label = "🤖 PluriBot" if msg["role"] == "assistant" else "👤 Tú"
            st.markdown(f"**{role_label}:** {msg['content']}")

        if user_query := st.text_input("Escribe tu pregunta sobre la app...", key="support_input"):
            st.session_state.support_messages.append({"role": "user", "content": user_query})
            
            try:
                client = OpenAI()
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_SUPPORT_PROMPT},
                        *st.session_state.support_messages
                    ]
                )
                bot_reply = response.choices[0].message.content
            except Exception:
                bot_reply = "⚠️ Configura la variable `OPENAI_API_KEY` en tu archivo `.env` para activar la respuesta en tiempo real de PluriBot."

            st.session_state.support_messages.append({"role": "assistant", "content": bot_reply})
            st.rerun()