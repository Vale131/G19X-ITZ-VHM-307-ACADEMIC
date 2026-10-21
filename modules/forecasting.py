import pandas as pd
import numpy as np
import plotly.graph_objects as go

def calcular_metricas_error(df_hist: pd.DataFrame):
    if df_hist.empty or len(df_hist) < 14:
        return {"mae": 0.0, "mape": 0.0, "status": "Insuficientes datos históricos"}

    df_clean = df_hist.sort_values('ds').copy()
    train = df_clean.iloc[:-14]
    test = df_clean.iloc[-14:].copy()

    train['dayofweek'] = train['ds'].dt.dayofweek
    avg_rev = train.groupby('dayofweek')['Ingresos'].mean().to_dict()
    avg_exp = train.groupby('dayofweek')['Egresos'].mean().to_dict()

    test['dayofweek'] = test['ds'].dt.dayofweek
    test['pred_neto'] = test['dayofweek'].map(avg_rev) - test['dayofweek'].map(avg_exp)
    test['real_neto'] = test['Ingresos'] - test['Egresos']

    mae = np.mean(np.abs(test['real_neto'] - test['pred_neto']))
    denom = np.where(np.abs(test['real_neto']) == 0, 1.0, np.abs(test['real_neto']))
    mape = np.mean(np.abs((test['real_neto'] - test['pred_neto']) / denom)) * 100

    return {
        "mae": float(mae),
        "mape": float(mape),
        "status": "Evaluación basada en Holdout (14 días)"
    }

def generar_pronostico_real(df_hist: pd.DataFrame, df_cartera: pd.DataFrame = None, dias_horizonte: int = 30, escenario: str = "Base", saldo_inicial: float = None):
    if df_hist.empty:
        fechas_base = pd.date_range(start=pd.Timestamp.today(), periods=dias_horizonte, freq='D')
        df_proy = pd.DataFrame({
            'ds': fechas_base,
            'Ingresos': [15000.0] * dias_horizonte,
            'Egresos': [9000.0] * dias_horizonte,
            'Flujo_Neto': [6000.0] * dias_horizonte,
            'Saldo_Acumulado': [6000.0 * (i + 1) for i in range(dias_horizonte)]
        })
        return df_proy, df_hist

    df_clean = df_hist.sort_values('ds').copy()
    
    if saldo_inicial is None:
        neto_hist = df_clean['Ingresos'] - df_clean['Egresos']
        saldo_base = neto_hist.sum()
    else:
        saldo_base = saldo_inicial

    df_clean['dayofweek'] = df_clean['ds'].dt.dayofweek
    avg_rev = df_clean.groupby('dayofweek')['Ingresos'].mean().to_dict()
    avg_exp = df_clean.groupby('dayofweek')['Egresos'].mean().to_dict()

    factores = {
        "Base": (1.00, 1.00),
        "Optimista": (1.15, 0.90),
        "Conservador": (0.85, 1.10)
    }
    f_rev, f_exp = factores.get(escenario, (1.0, 1.0))

    ultima_fecha = df_clean['ds'].max()
    fechas_futuras = pd.date_range(start=ultima_fecha + pd.Timedelta(days=1), periods=dias_horizonte, freq='D')

    proyecciones = []
    for f in fechas_futuras:
        dow = f.dayofweek
        ing_est = avg_rev.get(dow, 10000.0) * f_rev
        egr_est = avg_exp.get(dow, 7000.0) * f_exp
        proyecciones.append({
            'ds': f,
            'Ingresos': ing_est,
            'Egresos': egr_est
        })

    df_proy = pd.DataFrame(proyecciones)

    # INTEGRACIÓN DE CARTERA MULTIPLICADA POR SU PROBABILIDAD
    if df_cartera is not None and not df_cartera.empty and 'fecha_vencimiento' in df_cartera.columns:
        df_cartera_clean = df_cartera.copy()
        df_cartera_clean['fecha_vencimiento'] = pd.to_datetime(df_cartera_clean['fecha_vencimiento'], errors='coerce')
        
        for idx, row in df_proy.iterrows():
            f_curr = row['ds'].strftime('%Y-%m-%d')
            
            items_fecha = df_cartera_clean[
                (df_cartera_clean['fecha_vencimiento'].dt.strftime('%Y-%m-%d') == f_curr) &
                (df_cartera_clean['estatus'] != 'Pagado')
            ]
            
            if not items_fecha.empty:
                for _, item in items_fecha.iterrows():
                    p = float(item.get('probabilidad', 1.0))
                    if p > 1.0: p = p / 100.0
                    monto_ponderado = float(item.get('monto', 0.0)) * p
                    
                    t_item = str(item.get('tipo', '')).upper()
                    if 'CXC' in t_item or 'COBRO' in t_item:
                        df_proy.at[idx, 'Ingresos'] += monto_ponderado
                    elif 'CXP' in t_item or 'PAGO' in t_item:
                        df_proy.at[idx, 'Egresos'] += monto_ponderado

    df_proy['Flujo_Neto'] = df_proy['Ingresos'] - df_proy['Egresos']
    df_proy['Saldo_Acumulado'] = saldo_base + df_proy['Flujo_Neto'].cumsum()

    return df_proy, df_clean

def crear_grafica_escenarios(df_proy: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_proy['ds'], y=df_proy['Ingresos'], mode='lines+markers', name='Ingresos Proyectados', line=dict(color='#16A34A', width=2.5)))
    fig.add_trace(go.Scatter(x=df_proy['ds'], y=df_proy['Egresos'], mode='lines+markers', name='Egresos Proyectados', line=dict(color='#DC2626', width=2.5)))
    fig.update_layout(title="<b>Proyección Estocástica de Flujo de Efectivo</b>", xaxis_title="Fecha Proyectada", yaxis_title="Monto ($)", height=360)
    return fig

def crear_grafica_barras_categoria(df_proy: pd.DataFrame):
    tot_ing, tot_egr = df_proy['Ingresos'].sum(), df_proy['Egresos'].sum()
    fig = go.Figure(data=[go.Bar(x=['Ingresos Totales', 'Egresos Totales'], y=[tot_ing, tot_egr], marker_color=['#16A34A', '#70112F'], text=[f"${tot_ing:,.2f}", f"${tot_egr:,.2f}"], textposition='auto')])
    fig.update_layout(title="<b>Comparativa de Entradas vs Salidas</b>", yaxis_title="Monto Acumulado ($)", height=360)
    return fig

def crear_grafica_saldos_area(df_proy: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_proy['ds'], y=df_proy['Saldo_Acumulado'], mode='lines', fill='tozeroy', name='Saldo Acumulado', line=dict(color='#70112F', width=3), fillcolor='rgba(112, 17, 47, 0.15)'))
    fig.update_layout(title="<b>Evolución del Saldo de Caja Acumulado</b>", xaxis_title="Fecha", yaxis_title="Saldo Disponible ($)", height=400)
    return fig