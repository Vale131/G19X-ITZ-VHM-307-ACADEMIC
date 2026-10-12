import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from prophet import Prophet

def regresores_nominas(fechas):
    df = pd.DataFrame({"ds": fechas})
    ultimo_dia = fechas + pd.offsets.MonthEnd(0)
    df["es_quincena"] = ((fechas.dt.day == 15) | (fechas == ultimo_dia)).astype(float)
    df["es_fecha_pago"] = ((fechas.dt.day.isin([15])) | (fechas == ultimo_dia)).astype(float)
    return df

def entrenar_prophet(df_input, reg):
    m = Prophet(
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=True,
        interval_width=0.95,
        holidays=pd.DataFrame({
            "holiday": "quincena",
            "ds": reg.loc[reg.es_quincena == 1, "ds"],
            "lower_window": -1,
            "upper_window": 1
        })
    )
    m.add_regressor("es_quincena")
    m.add_regressor("es_fecha_pago")
    m.fit(df_input[["ds", "y"]].merge(reg, on="ds"))
    return m

def calcular_metricas_backtesting(df_hist):
    """Calcula el error del modelo (MAPE y RMSE) usando los últimos 30 días."""
    if len(df_hist) < 90:
        return None, None
    
    train = df_hist.iloc[:-30]
    test = df_hist.iloc[-30:]
    
    reg_train = regresores_nominas(train["ds"])
    
    m = entrenar_prophet(train, reg_train)
    futuro = m.make_future_dataframe(periods=30)
    reg_fut = regresores_nominas(futuro["ds"])
    
    forecast = m.predict(futuro.merge(reg_fut, on="ds"))
    preds = forecast.tail(30)["yhat"].values
    reales = test["y"].values
    
    mape = np.mean(np.abs((reales - preds) / np.where(reales == 0, 1, reales))) * 100
    rmse = np.sqrt(np.mean((reales - preds) ** 2))
    return round(mape, 2), round(rmse, 2)

def simulacion_monte_carlo(saldo_inicial, yhat_futuro, std_diaria, num_simulaciones=1000):
    """Ejecuta 1,000 iteraciones estocásticas para calcular el riesgo de iliquidez y VaR."""
    dias = len(yhat_futuro)
    simulaciones = np.zeros((num_simulaciones, dias))
    
    for i in range(num_simulaciones):
        ruido = np.random.normal(0, std_diaria, dias)
        flujos_simulados = yhat_futuro + ruido
        simulaciones[i, :] = saldo_inicial + np.cumsum(flujos_simulados)
        
    saldos_finales = simulaciones[:, -1]
    
    # Value at Risk (VaR) al 95% y 99%
    var_95 = np.percentile(saldos_finales, 5)
    var_99 = np.percentile(saldos_finales, 1)
    
    # Probabilidad de caer por debajo de $0
    p_iliquidez = (np.min(simulaciones, axis=1) < 0).mean() * 100
    
    return simulaciones, round(var_95, 2), round(var_99, 2), round(p_iliquidez, 1)