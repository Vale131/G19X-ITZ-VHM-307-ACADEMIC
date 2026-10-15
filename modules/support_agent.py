import streamlit as st

def responder_soporte_fallback(query: str) -> str:
    """Genera respuestas técnicas y operativas según la consulta del usuario."""
    q = query.lower().strip()
    
    if any(w in q for w in ["como funciona", "cómo funciona", "ayuda", "guia", "que hace", "qué hace"]):
        return (
            "**Navegación general en PluriOne:**\n\n"
            "• **Cockpit Financiero:** Resumen de KPIs y carga de archivos CSV.\n"
            "• **Saldos & Tesorería:** Gráfica de evolución de liquidez acumulada.\n"
            "• **Capital de Trabajo & Cartera:** Gestión de CxC y CxP.\n"
            "• **Modelado Estocástico & VaR:** Análisis de riesgo con Monte Carlo.\n"
            "• **Gestión de Usuarios:** Alta de accesos y administración de roles."
        )
    elif any(w in q for w in ["csv", "carga", "archivo", "sincronizar", "excel"]):
        return "Para cargar datos, ve a **Cockpit Financiero** y abre 'Sincronizar Archivo Histórico (CSV)'. Las columnas requeridas son: `ds`, `Ingresos`, `Egresos`."
    elif any(w in q for w in ["usuario", "contraseña", "acceso", "login"]):
        return "Puedes crear nuevos usuarios institucionales desde la opción **Gestión de Usuarios** en la barra lateral."
    else:
        return f"He recibido tu consulta sobre *'{query}'*. Si tienes dudas sobre la carga de datos o configuración de escenarios, indícamelo para ayudarte."

def render_support_agent():
    """Renderiza el chat de PluriBot utilizando st.chat_input para evitar bucles de recarga."""
    st.subheader("PluriBot - Soporte Operativo & Asistencia")
    st.caption("Asistente técnico para dudas sobre la plataforma, formato de datos y navegación.")

    if "support_messages" not in st.session_state:
        st.session_state.support_messages = [
            {"role": "assistant", "content": "Hola, Valeria. Soy **PluriBot**. ¿En qué puedo asistirte con la plataforma?"}
        ]

    # Mostrar el historial de mensajes
    for msg in st.session_state.support_messages:
        role_label = "Usuario" if msg["role"] == "user" else "PluriBot"
        st.markdown(f"**{role_label}:** {msg['content']}")

    # Entrada de texto usando st.chat_input (limpia el valor automáticamente al enviar)
    if supp_query := st.chat_input("Escribe tu consulta técnica o sobre la plataforma...", key="pluribot_chat_input"):
        st.session_state.support_messages.append({"role": "user", "content": supp_query})
        respuesta = responder_soporte_fallback(supp_query)
        st.session_state.support_messages.append({"role": "assistant", "content": respuesta})
        st.rerun()