import streamlit as st
import os

def responder_localmente(prompt: str, contexto_financiero: str) -> str:
    """Generador de respuestas locales de respaldo en caso de desconexión."""
    p = prompt.lower()
    
    if any(w in p for w in ["cómo funciona", "como funciona", "que hace", "qué hace", "guia", "instrucciones", "ayuda"]):
        return (
            "**Guía de Navegación de PluriOne Liquidity System:**\n\n"
            "1. **🖼️ Cockpit Financiero:** Resume indicadores clave (Revenue, Flujo Neto, Cobertura) y permite cargar datos en CSV.\n"
            "2. **💳 Saldos & Tesorería:** Visualiza la evolución de los saldos acumulados de caja a lo largo del tiempo.\n"
            "3. **📋 Capital de Trabajo & Cartera:** Administra y registra Cuentas por Cobrar (CxC) y Cuentas por Pagar (CxP).\n"
            "4. **🎲 Modelado Estocástico & VaR:** Aplica simulaciones Monte Carlo para evaluar escenarios de riesgo financiero.\n"
            "5. **🎧 Centro de Inteligencia & IA:** Módulo de consulta asistida por IA para toma de decisiones ejecutivas.\n"
            "6. **👥 Gestión de Usuarios:** Creación y administración de accesos institucionales."
        )
    elif any(w in p for w in ["var", "monte carlo", "riesgo", "simulacion", "estocastico"]):
        return (
            "**Análisis de Riesgo Estocástico:**\n\n"
            f"Basado en tu contexto ({contexto_financiero}), el modelo Monte Carlo evalúa la probabilidad de caer en déficit "
            "simulando 1,000 itinerarios estocásticos con la volatilidad histórica de tu flujo."
        )
    else:
        return (
            f"**Diagnóstico Financiero de Copiloto CFO:**\n\n"
            f"Procesando consulta: *'{prompt}'*\n"
            f"• **Estatus Operativo:** {contexto_financiero}\n"
            "• **Recomendación:** Revisa el módulo de *Capital de Trabajo & Cartera* para priorizar cobros antes de comprometer nuevos gastos."
        )

def render_copilot(contexto_financiero=""):
    """Renderiza la interfaz del Copiloto CFO conectada a Google AI Studio (Gemini 1.5 Flash)."""
    st.subheader("Copiloto CFO - Asistente de Decisión Financiera (Google Gemini)")
    st.caption("Analiza escenarios de flujo de efectivo, riesgos de liquidez y estrategias de optimización.")

    api_key_env = os.getenv("OPENAI_API_KEY", "")
    api_key_user = st.session_state.get("custom_api_key", api_key_env)

    if not api_key_user:
        st.info("💡 **Conexión IA:** Ingresa tu API Key de Google AI Studio en la barra lateral en **CONFIGURACIÓN & IA**.")

    if "copilot_messages" not in st.session_state:
        st.session_state.copilot_messages = [
            {"role": "assistant", "content": "Hola, Valeria. Soy tu **Copiloto CFO** impulsado por Google Gemini. ¿En qué decisión financiera te puedo asesorar hoy?"}
        ]

    # Renderizar historial
    for msg in st.session_state.copilot_messages:
        role_label = "Valeria (CFO)" if msg["role"] == "user" else "Copiloto CFO"
        st.markdown(f"**{role_label}:** {msg['content']}")

    # Entrada de mensajes
    if prompt := st.chat_input("Escribe tu consulta financiera o sobre la aplicación...", key="cfo_chat_input"):
        st.session_state.copilot_messages.append({"role": "user", "content": prompt})

        if api_key_user:
            try:
                from openai import OpenAI
                # Conexión al endpoint OpenAI-compatible de Google AI Studio
                client = OpenAI(
                    api_key=api_key_user,
                    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
                )
                response = client.chat.completions.create(
                    model="gemini-1.5-flash",
                    messages=[
                        {"role": "system", "content": f"Eres un Copiloto CFO experto en tesorería y gestión de liquidez. Contexto actual de la empresa: {contexto_financiero}"},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=400
                )
                respuesta = response.choices[0].message.content
            except Exception as e:
                # Fallback suave en caso de error de red o clave inválida
                respuesta = f"⚠️ *Aviso de conexión con Google AI Studio:* {str(e)}\n\n" + responder_localmente(prompt, contexto_financiero)
        else:
            respuesta = responder_localmente(prompt, contexto_financiero)

        st.session_state.copilot_messages.append({"role": "assistant", "content": respuesta})
        st.rerun()