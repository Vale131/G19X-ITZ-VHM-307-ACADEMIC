import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

SYSTEM_CFO_PROMPT = """
Eres el "Copiloto CFO", Director Financiero Virtual para PluriOne S.A. de C.V.
Tu objetivo es brindar diagnósticos prescriptivos y recomendaciones estratégicas de liquidez y capital de trabajo.
"""

def generar_recomendacion_cfo_fallback(contexto_str):
    return (
        "📊 **Diagnóstico del Copiloto CFO (Análisis Prescriptivo):**\n\n"
        "1. **Monitoreo de Mínimos:** Vigile el saldo mínimo proyectado respecto al umbral de seguridad.\n"
        "2. **Gestión de CXC:** Negocie pronto pago en las facturas de mayor monto vencidas o por vencer.\n"
        "3. **Mitigación de Riesgo:** Evalúe líneas de crédito revolventes si la simulación reporta riesgo de iliquidez."
    )

def render_copilot(contexto_sistema):
    st.subheader("💬 Copiloto Financiero (CFO Virtual IA)")
    st.caption("Asesoría estratégica basada en las proyecciones y el motor Monte Carlo.")

    if "cfo_messages" not in st.session_state:
        st.session_state.cfo_messages = [
            {"role": "assistant", "content": "¡Hola! Soy tu Copiloto CFO. ¿En qué decisión estratégica de liquidez te puedo apoyar?"}
        ]

    for msg in st.session_state.cfo_messages:
        role_label = "👔 CFO Copilot" if msg["role"] == "assistant" else "👤 Tú"
        st.markdown(f"**{role_label}:** {msg['content']}")

    if prompt := st.chat_input("Plantea una consulta estratégica de liquidez..."):
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