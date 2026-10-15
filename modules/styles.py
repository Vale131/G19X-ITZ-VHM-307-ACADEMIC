import streamlit as st

def aplicar_estilos_css():
    """Aplica el diseño ejecutivo con indicador dorado lateral e interfaz de cristal oscuro."""
    st.markdown(r"""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">

    <style>
        /* ESTRUCTURA GLOBAL */
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }
        .stApp {
            background-color: #FAF6EE !important;
            color: #23030D !important;
        }
        
        #MainMenu, footer { visibility: hidden; }
        header { background-color: transparent !important; }

        .block-container {
            padding-top: 1.2rem !important;
            padding-bottom: 2.5rem !important;
            max-width: 98% !important;
        }

        /* BARRA LATERAL (BORGOÑA PROFUNDO #23030D) */
        section[data-testid="stSidebar"] {
            background-color: #23030D !important;
            border-right: 1px solid rgba(253, 211, 77, 0.12) !important;
            box-shadow: 6px 0 25px rgba(0, 0, 0, 0.4) !important;
        }

        section[data-testid="stSidebar"] .stMarkdown, 
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] p {
            color: #FDF6E2 !important;
        }

        /* BOTÓN SUPERIOR DE CONTRAER / DESPLEGAR */
        [data-testid="stSidebarHeader"] button {
            color: #FCD34D !important;
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(253, 211, 77, 0.2) !important;
            border-radius: 8px !important;
        }

        /* CARD DE USUARIO EN CRISTAL */
        .sidebar-user-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 18px;
            padding: 14px 16px;
            margin-bottom: 22px;
            display: flex;
            align-items: center;
            gap: 14px;
            box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.08);
        }
        .sidebar-user-avatar {
            width: 44px;
            height: 44px;
            border-radius: 12px;
            background: #FCD34D;
            color: #23030D;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 1.25rem;
            box-shadow: 0 2px 10px rgba(252, 211, 77, 0.25);
        }
        .sidebar-user-name {
            font-size: 1.02rem;
            font-weight: 800;
            color: #FFFFFF;
            line-height: 1.2;
        }
        .sidebar-user-role {
            font-size: 0.82rem;
            color: #A89269;
            font-weight: 600;
            margin-top: 2px;
        }

        /* OPCIONES DE NAVEGACIÓN */
        section[data-testid="stSidebar"] div[role="radiogroup"] {
            gap: 6px !important;
        }

        /* OCULTAR COMPLETAMENTE LOS CÍRCULOS DE RADIO */
        section[data-testid="stSidebar"] div[role="radiogroup"] label input[type="radio"],
        section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
            display: none !important;
        }

        /* BOTÓN DE OPCIÓN INACTIVO */
        section[data-testid="stSidebar"] div[role="radiogroup"] label {
            background: transparent !important;
            border: 1px solid transparent !important;
            border-radius: 16px !important;
            padding: 12px 16px !important;
            transition: all 0.25s ease !important;
            font-weight: 600 !important;
            font-size: 0.94rem !important;
            color: #FDF6E2 !important;
            cursor: pointer !important;
            margin: 0 !important;
            width: 100% !important;
            display: flex !important;
            align-items: center !important;
            position: relative !important;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
            background: rgba(255, 255, 255, 0.04) !important;
            color: #FCD34D !important;
        }

        /* OPCIÓN SELECCIONADA: TARJETA DE CRISTAL OSCURO CON BORDE FINO DORADO */
        section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(252, 211, 77, 0.35) !important;
            border-radius: 16px !important;
            box-shadow: 0 4px 18px rgba(0, 0, 0, 0.35) !important;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) span,
        section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p,
        section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) div {
            color: #FCD34D !important;
            font-weight: 700 !important;
        }

        /* INDICADOR LATERAL VERTICAL DORADO */
        section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked)::before {
            content: '';
            position: absolute;
            left: -12px;
            top: 50%;
            transform: translateY(-50%);
            width: 5px;
            height: 26px;
            background-color: #FCD34D;
            border-radius: 4px;
            box-shadow: 0 0 10px rgba(252, 211, 77, 0.85);
        }

        /* TARJETAS KPI */
        .kpi-card-ref {
            background: #FFFFFF;
            border: 1px solid #F3EAD3;
            border-radius: 16px;
            padding: 20px 22px;
            box-shadow: 0 4px 18px rgba(35, 3, 13, 0.04);
            position: relative;
        }
        .kpi-title-ref {
            font-size: 0.78rem;
            font-weight: 700;
            color: #6B1128;
            margin-bottom: 4px;
            text-transform: uppercase;
        }
        .kpi-value-ref {
            font-size: 1.65rem;
            font-weight: 800;
            color: #23030D;
        }
        .kpi-icon-badge {
            position: absolute;
            top: 18px;
            right: 18px;
            background: #FFFBEB;
            border-radius: 8px;
            padding: 4px 8px;
            font-size: 0.72rem;
            color: #B45309;
            font-weight: 800;
        }

        /* INSIGNIAS DE ESTATUS DE USUARIO */
        .badge-activo {
            background-color: #DEF7EC;
            color: #03543F;
            font-weight: 800;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.78rem;
            display: inline-block;
            border: 1px solid #84E1BC;
        }
        .badge-inactivo {
            background-color: #FDE8E8;
            color: #9B1C1C;
            font-weight: 800;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.78rem;
            display: inline-block;
            border: 1px solid #F8B4B4;
        }

        /* BOTONES DE ACCIÓN */
        div.stButton > button {
            background-color: #EAB308 !important;
            color: #23030D !important;
            border-radius: 12px !important;
            font-weight: 800 !important;
            border: none !important;
        }
        div.stDownloadButton > button {
            background: linear-gradient(135deg, #FCD34D 0%, #EAB308 100%) !important;
            color: #23030D !important;
            border-radius: 12px !important;
            font-weight: 800 !important;
            border: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

def aplicar_estilo_grafica(fig):
    """Estiliza las gráficas Plotly con fondo transparente."""
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#4A081A"),
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(
            bgcolor="#23030D",
            font_size=12,
            font_family="Plus Jakarta Sans",
            font_color="#FFFFFF"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color="#6B1128")
        ),
        xaxis=dict(showgrid=True, gridcolor="#F3EAD3", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#F3EAD3", zeroline=False)
    )
    return fig