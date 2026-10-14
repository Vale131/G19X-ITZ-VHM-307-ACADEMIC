import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

SYSTEM_CFO_PROMPT = """
Eres el "Copiloto CFO", Director Financiero Virtual de alto nivel para PluriOne S.A. de C.V.
Tu objetivo es emitir diagnósticos prescriptivos y recomendaciones estratégicas de liquidez y capital de trabajo.
Responde utilizando viñetas estilizadas, tono formal, ejecutivo y enfocado en accionables financieros inmediatos.
"""

def generar_recomendacion_cfo_fallback(contexto_str):
    return (
        "📊 **Diagnóstico Prescriptivo del Copiloto CFO:**\n\n"
        "1. **Monitoreo de Mínimos:** Se sugiere mantener una cobertura mínima de 15 días de egresos operativos en caja principal.\n"
        "2. **Estrategia de Cobranza:** Active llamadas de seguimiento sobre las facturas de la Pestaña 3 con probabilidad menor a 0.8.\n"
        "3. **Mitigación de Riesgo:** Si la proyección stocástica indica déficit, evalúe esquemas de factoraje o líneas de crédito revolventes."
    )

def render_copilot(contexto_sistema):
    st.subheader("👔 Copiloto Financiero (CFO Virtual IA)")
    st.caption("Asesoría estratégica en tiempo real alineada con el saldo de tesorería y escenarios 'What-If'.")

    if "cfo_messages" not in st.session_state:
        st.session_state.cfo_messages = [
            {"role": "assistant", "content": "¡Hola! Soy tu **Copiloto CFO Virtual**. He analizado el estado de tesorería de PluriOne. ¿Qué escenario o decisión estratégica deseas evaluar hoy?"}
        ]

    for msg in st.session_state.cfo_messages:
        if msg["role"] == "assistant":
            st.markdown(f'<div class="chat-bot">👔 <b>CFO Copilot:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-user">👤 <b>Tú:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Plantea una pregunta sobre liquidez o capital de trabajo..."):
        st.session_state.cfo_messages.append({"role": "user", "content": prompt})
        
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and not api_key.startswith("sk-proj-tu_clave"):
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                prompt_completo = f"Contexto actual del sistema: {contexto_sistema}\n\nConsulta del usuario: {prompt}"
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_CFO_PROMPT},
                        {"role": "user", "content": prompt_completo}
                    ],
                    temperature=0.5
                )
                respuesta = response.choices[0].message.content
            except Exception:
                respuesta = generar_recomendacion_cfo_fallback(contexto_sistema)
        else:
            respuesta = generar_recomendacion_cfo_fallback(contexto_sistema)

        st.session_state.cfo_messages.append({"role": "assistant", "content": respuesta})
        st.rerun()