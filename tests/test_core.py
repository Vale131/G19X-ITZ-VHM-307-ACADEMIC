import pytest
import os
import pandas as pd
import numpy as np

# Aislamiento: Redirigir las operaciones de BD durante los tests a un archivo temporal
TEST_DB_NAME = "flujo_efectivo_test.db"

import modules.database as db
db.DB_NAME = TEST_DB_NAME

from modules.database import (
    init_db,
    registrar_usuario,
    actualizar_usuario,
    autenticar_usuario,
    verificar_password,
    hash_password,
    insertar_compromiso_cartera,
    actualizar_estatus_cartera,
    obtener_cartera_db,
    get_connection
)
from modules.forecasting import (
    calcular_metricas_error,
    calcular_mejora_vs_baseline,
    generar_pronostico_real
)

@pytest.fixture(autouse=True)
def setup_and_teardown_test_db():
    """Crea la base de datos temporal antes de cada test y la elimina al finalizar."""
    if os.path.exists(TEST_DB_NAME):
        os.remove(TEST_DB_NAME)
    init_db()
    yield
    if os.path.exists(TEST_DB_NAME):
        os.remove(TEST_DB_NAME)

def test_hash_y_verificacion_password():
    password_plana = "PluriOneSegura2026!"
    hashed = hash_password(password_plana)
    
    assert hashed != password_plana
    assert verificar_password(password_plana, hashed) is True
    assert verificar_password("PasswordIncorrecta", hashed) is False

def test_actualizar_usuario_con_nueva_password():
    email_test = "test_edit_pass@plurione.com"
    registrar_usuario(email_test, "PasswordVieja123", "Usuario Test Edit", "Analista de Tesorería", "Activo")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email_test,))
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    user_id = row[0]
    
    ok, msg = actualizar_usuario(
        user_id=user_id, 
        email=email_test, 
        nombre="Usuario Test Editado", 
        rol="Auditor de Riesgo", 
        estatus="Activo", 
        nueva_password="PasswordNueva456"
    )
    assert ok is True
    assert autenticar_usuario(email_test, "PasswordVieja123") is None
    
    user_auth = autenticar_usuario(email_test, "PasswordNueva456")
    assert user_auth is not None
    assert user_auth['nombre'] == "Usuario Test Editado"
    assert user_auth['rol'] == "Auditor de Riesgo"

def test_calculo_metricas_error_holdout():
    fechas = pd.date_range(start="2026-01-01", periods=30, freq="D")
    df_test = pd.DataFrame({
        "ds": fechas,
        "Ingresos": np.random.uniform(1000, 5000, size=30),
        "Egresos": np.random.uniform(500, 2000, size=30)
    })
    
    metricas = calcular_metricas_error(df_test)
    assert isinstance(metricas, dict)
    assert "mae" in metricas
    assert "mape" in metricas
    assert metricas["mae"] >= 0
    assert metricas["mape"] >= 0

def test_modelo_le_gana_al_promedio_con_estacionalidad():
    fechas = pd.date_range(start='2026-01-05', periods=56, freq='D')
    ingresos = [20000.0 if f.dayofweek == 0 else 5000.0 for f in fechas]
    df = pd.DataFrame({'ds': fechas, 'Ingresos': ingresos, 'Egresos': [3000.0] * 56})

    mejora = calcular_mejora_vs_baseline(df)
    assert mejora > 0

def test_cartera_crud_operaciones_directas():
    """Verifica la inserción y actualización directa en SQL de la cartera."""
    res_insert = insertar_compromiso_cartera("CxC", "Cliente Pruebas", 15000.0, "2026-03-01", 0.85, "Pendiente")
    assert res_insert is True

    df_cartera = obtener_cartera_db()
    assert not df_cartera.empty
    assert "id" in df_cartera.columns
    
    reg_id = int(df_cartera.iloc[0]["id"])
    res_update = actualizar_estatus_cartera(reg_id, "Pagado")
    assert res_update is True

    df_actualizado = obtener_cartera_db()
    assert df_actualizado.iloc[0]["estatus"] == "Pagado"

def test_cartera_ponderada_en_pronostico():
    """Verifica que los montos de cartera afecten la proyección ponderados por su probabilidad."""
    fechas = pd.date_range(start='2026-01-01', periods=30, freq='D')
    df_hist = pd.DataFrame({'ds': fechas, 'Ingresos': [10000.0] * 30, 'Egresos': [5000.0] * 30})
    
    fecha_compromiso = (fechas.max() + pd.Timedelta(days=5)).strftime('%Y-%m-%d')
    insertar_compromiso_cartera("CxC", "Cliente Especial", 20000.0, fecha_compromiso, 0.50, "Pendiente")
    
    df_cartera = obtener_cartera_db()
    df_proy, _ = generar_pronostico_real(df_hist, df_cartera, dias_horizonte=30, escenario="Base")
    
    fila_compromiso = df_proy[df_proy['ds'].dt.strftime('%Y-%m-%d') == fecha_compromiso]
    assert not fila_compromiso.empty
    # Ingreso base estacional (10000) + monto ponderado CxC (20000 * 0.50 = 10000) = 20000
    assert float(fila_compromiso['Ingresos'].iloc[0]) == 20000.0