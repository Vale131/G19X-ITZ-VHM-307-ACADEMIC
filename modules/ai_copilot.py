import streamlit as st
from openai import OpenAI

def render_copilot(contexto_financiero):
    st.subheader("💬 Copiloto Financiero IA")
    st.caption("Realiza consultas en texto libre sobre el flujo de caja, riesgos y recomendaciones de ajuste.")

    # Inicializar historial de chat
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "¡Hola! Soy tu asistente de tesorería. ¿En qué puedo ayudarte a optimizar la liquidez hoy?"}
        ]

    # Mostrar mensajes anteriores
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input del usuario
    if prompt := st.chat_input("Ej: ¿Qué medidas tomar para evitar el déficit en el punto mínimo?"):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            client = OpenAI()
            system_prompt = f"""
            Eres un CFO experto y consultor financiero.
            Contexto actual de la empresa: {contexto_financiero}.
            Responde de forma clara, ejecutiva, directa y con números específicos en MXN.
            """
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.chat_messages
                ]
            )
            answer = response.choices[0].message.content
        except Exception:
            answer = "⚠️ No se pudo conectar con la API de OpenAI. Por favor verifica que tu `OPENAI_API_KEY` esté bien configurada en el archivo `.env`."

        st.session_state.chat_messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)