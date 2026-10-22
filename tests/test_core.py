import pytest
import pandas as pd
from modules.database import hash_password, verificar_password
from modules.forecasting import calcular_metricas_error

def test_cifrado_bcrypt():
    password_raw = "MiPasswordSeguro123"
    hash_gen = hash_password(password_raw)
    assert verificar_password(password_raw, hash_gen) is True
    assert verificar_password("PasswordIncorrecto", hash_gen) is False

def test_metricas_error_holdout():
    fechas = pd.date_range(start="2026-01-01", periods=30, freq="D")
    df_test = pd.DataFrame({
        "ds": fechas,
        "Ingresos": [1000.0] * 30,
        "Egresos": [500.0] * 30
    })
    metricas = calcular_metricas_error(df_test)
    assert "mae" in metricas
    assert "mape" in metricas
    assert metricas["mae"] >= 0.0