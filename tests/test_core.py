import pytest
import os
import pandas as pd
import numpy as np
from modules.database import (
    init_db, 
    registrar_usuario, 
    actualizar_usuario, 
    autenticar_usuario, 
    verificar_password,
    hash_password,
    get_connection
)
from modules.forecasting import calcular_metricas_error, calcular_mejora_vs_baseline

@pytest.fixture(autouse=True)
def setup_database():
    """Inicializa la base de datos relacional para pruebas."""
    init_db()

def test_hash_y_verificacion_password():
    password_plana = "PluriOneSegura2026!"
    hashed = hash_password(password_plana)
    
    assert hashed != password_plana
    assert verificar_password(password_plana, hashed) is True
    assert verificar_password("PasswordIncorrecta", hashed) is False

def test_actualizar_usuario_con_nueva_password():
    """Valida la edición de usuario con nueva contraseña y su posterior inicio de sesión."""
    email_test = "test_edit_pass@plurione.com"
    registrar_usuario(email_test, "PasswordVieja123", "Usuario Test Edit", "Analista de Tesorería", "Activo")
    
    # Obtener ID del usuario recién creado
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email_test,))
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    user_id = row[0]
    
    # Actualizar usuario cambiando contraseña y rol a Auditor
    ok, msg = actualizar_usuario(
        user_id=user_id, 
        email=email_test, 
        nombre="Usuario Test Editado", 
        rol="Auditor de Riesgo", 
        estatus="Activo", 
        nueva_password="PasswordNueva456"
    )
    assert ok is True
    
    # Verificar que NO se puede autenticar con la contraseña antigua
    assert autenticar_usuario(email_test, "PasswordVieja123") is None
    
    # Verificar inicio de sesión con la contraseña NUEVA y el rol actualizado
    user_auth = autenticar_usuario(email_test, "PasswordNueva456")
    assert user_auth is not None
    assert user_auth['nombre'] == "Usuario Test Editado"
    assert user_auth['rol'] == "Auditor de Riesgo"

def test_calculo_metricas_error_holdout():
    # Serie de tiempo sintética de 30 días
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
    # Serie sintética de 8 semanas (56 días) con un pico fuerte los lunes
    fechas = pd.date_range(start='2026-01-05', periods=56, freq='D')
    ingresos = [20000.0 if f.dayofweek == 0 else 5000.0 for f in fechas]
    df = pd.DataFrame({'ds': fechas, 'Ingresos': ingresos, 'Egresos': [3000.0] * 56})

    mejora = calcular_mejora_vs_baseline(df)
    assert mejora > 0