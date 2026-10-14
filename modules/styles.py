import streamlit as st

def aplicar_estilos_css():
    """Inyecta todos los estilos CSS del tema ejecutivo SaaS."""
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">

    <style>
        /* Estructura Global */
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }
        .stApp {
            background-color: #F8FAFC;
            color: #0F172A;
        }
        #MainMenu, footer, header { visibility: hidden; }
        
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 3rem !important;
            max-width: 96% !important;
        }

        /* Header Ejecutivo / Topbar */
        .executive-header {
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
            border-radius: 16px;
            padding: 20px 28px;
            color: #FFFFFF;
            box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.12);
            margin-bottom: 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .brand-title {
            font-size: 1.4rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: #FFFFFF;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .brand-subtitle {
            font-size: 0.8rem;
            color: #94A3B8;
            font-weight: 500;
            margin-top: 2px;
        }
        .user-badge {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            padding: 6px 14px;
            border-radius: 30px;
            font-size: 0.82rem;
            color: #E2E8F0;
            font-weight: 600;
        }

        /* Pestañas de Navegación */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: #EEF2F6;
            padding: 6px;
            border-radius: 14px;
            border: 1px solid #E2E8F0;
            margin-bottom: 1.5rem;
        }
        .stTabs [data-baseweb="tab"] {
            height: 44px;
            border-radius: 10px;
            padding: 0px 22px;
            color: #64748B;
            font-weight: 700;
            font-size: 0.88rem;
            border: none !important;
            transition: all 0.2s ease;
        }
        .stTabs [aria-selected="true"] {
            background-color: #FFFFFF !important;
            color: #4F46E5 !important;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.12) !important;
        }

        /* Tarjetas KPI Ejecutivas */
        .kpi-card-v2 {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            padding: 18px 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            margin-bottom: 12px;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }
        .kpi-card-v2:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 16px -4px rgba(0, 0, 0, 0.06);
        }
        .kpi-header-text {
            font-size: 0.72rem;
            font-weight: 800;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .kpi-amount-text {
            font-size: 1.45rem;
            font-weight: 800;
            color: #0F172A;
            margin-top: 4px;
            letter-spacing: -0.02em;
        }
        .kpi-amount-text.pos { color: #10B981; }
        .kpi-amount-text.neg { color: #EF4444; }
        
        .status-pill {
            display: inline-block;
            font-size: 0.7rem;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 12px;
            margin-top: 6px;
        }
        .pill-green { background-color: #D1FAE5; color: #065F46; }
        .pill-red { background-color: #FEE2E2; color: #991B1B; }
        .pill-blue { background-color: #E0E7FF; color: #3730A3; }

        /* Personalización de Botones de Acción */
        div.stButton > button {
            border-radius: 10px !important;
            font-weight: 700 !important;
            font-size: 0.88rem !important;
            padding: 0.5rem 1rem !important;
            transition: all 0.2s ease !important;
        }
        div.stDownloadButton > button {
            border-radius: 10px !important;
            font-weight: 700 !important;
            background-color: #4F46E5 !important;
            color: #FFFFFF !important;
            border: none !important;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25) !important;
        }
        div.stDownloadButton > button:hover {
            background-color: #4338CA !important;
            transform: translateY(-1px);
        }

        .stSelectbox label, .stMultiSelect label {
            font-weight: 700 !important;
            color: #334155 !important;
            font-size: 0.85rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

def aplicar_estilo_grafica(fig):
    """Aplica la paleta y tipografía limpia a cualquier gráfica Plotly."""
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#334155"),
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False)
    )
    return fig

def render_topbar_ejecutiva(nombre_usuario, rol_usuario):
    """Renderiza el banner superior de la aplicación."""
    st.markdown(f"""
    <div class="executive-header">
        <div>
            <div class="brand-title">💎 PluriOne Liquidity Intelligence</div>
            <div class="brand-subtitle">Plataforma Predictiva de Tesorería & Análisis Estocástico de Riesgo</div>
        </div>
        <div class="user-badge">
            👤 <b>{nombre_usuario}</b> &nbsp;|&nbsp; <span style="color:#A5B4FC;">{rol_usuario}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)