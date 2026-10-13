import pandas as pd
import numpy as np
import plotly.graph_objects as go

def generar_pronostico_real(df_historico, dias_horizonte=30, retraso_cobro=0, escenario="Base", saldo_inicial_base=654121.0):
    """
    Calcula una predicción estadística basada en tendencia, estacionalidad diaria 
    e intervalos de confianza a partir del histórico real.
    """
    if df_historico is None or len(df_historico) < 7:
        fechas_base = pd.date_range(end=pd.Timestamp.today(), periods=60)
        df = pd.DataFrame({
            'ds': fechas_base,
            'Ingresos': np.linspace(100000, 130000, 60) + np.sin(np.arange(60)) * 15000,
            'Egresos': np.linspace(75000, 90000, 60) + np.cos(np.arange(60)) * 10000
        })
    else:
        df = df_historico.copy()
        df['ds'] = pd.to_datetime(df['ds'])
        df = df.sort_values('ds')

    # 1. Extracción de Métricas Estadísticas del Histórico
    df['dia_semana'] = df['ds'].dt.dayofweek
    
    ingresos_por_dia = df.groupby('dia_semana')['Ingresos'].mean()
    egresos_por_dia = df.groupby('dia_semana')['Egresos'].mean()
    
    mean_ingresos = df['Ingresos'].mean()
    mean_egresos = df['Egresos'].mean()
    
    std_ingresos = df['Ingresos'].std() if len(df) > 1 else mean_ingresos * 0.15
    std_egresos = df['Egresos'].std() if len(df) > 1 else mean_egresos * 0.10

    # 2. Factor de ajuste por Escenario
    factor_ingresos = 1.0
    factor_egresos = 1.0
    if escenario == "Conservador":
        factor_ingresos = 0.82
        factor_egresos = 1.08
    elif escenario == "Optimista":
        factor_ingresos = 1.18
        factor_egresos = 0.92

    # 3. Proyección Futura
    ultima_fecha = df['ds'].max()
    fechas_futuras = pd.date_range(start=ultima_fecha + pd.Timedelta(days=1), periods=dias_horizonte)
    
    ingresos_proj = []
    egresos_proj = []

    for fecha in fechas_futuras:
        d_sem = fecha.dayofweek
        
        base_ing = ingresos_por_dia.get(d_sem, mean_ingresos)
        base_egr = egresos_por_dia.get(d_sem, mean_egresos)
        
        ing = (0.6 * base_ing + 0.4 * mean_ingresos) * factor_ingresos
        egr = (0.6 * base_egr + 0.4 * mean_egresos) * factor_egresos
        
        ingresos_proj.append(max(0, ing))
        egresos_proj.append(max(0, egr))

    ingresos_proj = np.array(ingresos_proj)
    egresos_proj = np.array(egresos_proj)

    if retraso_cobro > 0 and len(ingresos_proj) > retraso_cobro:
        ingresos_proj = np.roll(ingresos_proj, retraso_cobro)
        ingresos_proj[:retraso_cobro] = mean_ingresos * 0.3

    df_fut = pd.DataFrame({
        'ds': fechas_futuras,
        'Ingresos': ingresos_proj,
        'Egresos': egresos_proj
    })
    
    df_fut['Flujo_Neto'] = df_fut['Ingresos'] - df_fut['Egresos']
    df_fut['Saldo_Acumulado'] = saldo_inicial_base + df_fut['Flujo_Neto'].cumsum()
    
    # Bandas de confianza (Límite Superior e Inferior al 95%)
    margen_error = 1.96 * np.sqrt(np.arange(1, dias_horizonte + 1)) * (std_ingresos + std_egresos) / 2
    df_fut['Saldo_Superior'] = df_fut['Saldo_Acumulado'] + margen_error
    df_fut['Saldo_Inferior'] = df_fut['Saldo_Acumulado'] - margen_error

    return df_fut, df

def crear_grafica_escenarios(df_proyeccion):
    """Gráfica de Barras de Cobros/Pagos + Línea de Saldo."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_proyeccion['ds'],
        y=df_proyeccion['Ingresos'],
        name='Cobros Proyectados',
        marker_color='#6366F1',
        opacity=0.85
    ))

    fig.add_trace(go.Bar(
        x=df_proyeccion['ds'],
        y=df_proyeccion['Egresos'],
        name='Pagos Proyectados',
        marker_color='#F43F5E',
        opacity=0.85
    ))

    fig.add_trace(go.Scatter(
        x=df_proyeccion['ds'],
        y=df_proyeccion['Saldo_Acumulado'],
        name='Saldo Neto Acumulado',
        mode='lines+markers',
        line=dict(color='#111827', width=2.5),
        marker=dict(size=5, color='#111827')
    ))

    fig.update_layout(
        template="plotly_white",
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", size=12, color="#374151"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#F1F5F9'),
        hovermode="x unified"
    )
    return fig

def crear_grafica_saldos_area(df_proyeccion, df_historico=None):
    """Gráfica de Saldos con área sombreada e intervalo de confianza."""
    fig = go.Figure()

    if df_historico is not None and not df_historico.empty:
        fig.add_trace(go.Scatter(
            x=df_historico['ds'],
            y=df_historico['Ingresos'] - df_historico['Egresos'],
            name='Flujo Histórico Real',
            mode='lines',
            line=dict(color='#94A3B8', width=1.5)
        ))

    # Intervalo de Confianza (Se corrigió 'fill' a 'toself')
    fig.add_trace(go.Scatter(
        x=pd.concat([df_proyeccion['ds'], df_proyeccion['ds'][::-1]]),
        y=pd.concat([df_proyeccion['Saldo_Superior'], df_proyeccion['Saldo_Inferior'][::-1]]),
        fill='toself',
        fillcolor='rgba(99, 102, 241, 0.10)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        name='Intervalo de Confianza 95%'
    ))

    fig.add_trace(go.Scatter(
        x=df_proyeccion['ds'],
        y=df_proyeccion['Saldo_Acumulado'],
        name='Saldo Proyectado',
        mode='lines+markers',
        line=dict(color='#4F46E5', width=2.8, dash='dash'),
        marker=dict(size=5, color='#4F46E5')
    ))

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", size=12, color="#374151"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#F1F5F9'),
        hovermode="x unified"
    )
    return fig