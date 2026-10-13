import sqlite3
import pandas as pd

DB_NAME = "flujo_efectivo.db"

def init_db():
    """Inicializa la base de datos SQLite con las tablas de histórico y cartera."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabla de Histórico de Ingresos y Egresos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ds TEXT UNIQUE,
            ingresos REAL,
            egresos REAL
        )
    """)
    
    # Tabla de Cartera CxC / CxP
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cartera (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            monto REAL,
            tipo TEXT,
            probabilidad REAL,
            descripcion TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def guardar_historico_db(df):
    """Guarda o reemplaza los datos históricos en la base de datos SQLite."""
    if df is None or df.empty:
        return
    
    df_clean = df.copy()
    df_clean['ds'] = pd.to_datetime(df_clean['ds']).dt.strftime('%Y-%m-%d')
    
    # Renombrar columnas si vienen en mayúsculas/minúsculas
    col_map = {col: col.capitalize() for col in df_clean.columns}
    df_clean = df_clean.rename(columns=col_map)
    
    if set(['Ds', 'Ingresos', 'Egresos']).issubset(df_clean.columns):
        df_save = pd.DataFrame({
            'ds': df_clean['Ds'],
            'ingresos': df_clean['Ingresos'],
            'egresos': df_clean['Egresos']
        })
        conn = sqlite3.connect(DB_NAME)
        df_save.to_sql("historico", conn, if_exists="replace", index=False)
        conn.close()

def obtener_historico_db():
    """Recupera el histórico financiero almacenado en SQLite."""
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql("SELECT ds, ingresos AS Ingresos, egresos AS Egresos FROM historico ORDER BY ds ASC", conn)
        if not df.empty:
            df['ds'] = pd.to_datetime(df['ds'])
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df

def guardar_cartera_db(df):
    """Guarda la cartera CxC/CxP en SQLite."""
    if df is None or df.empty:
        return
    conn = sqlite3.connect(DB_NAME)
    df.to_sql("cartera", conn, if_exists="replace", index=False)
    conn.close()

def obtener_cartera_db():
    """Recupera la cartera desde SQLite."""
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql("SELECT fecha, monto, tipo, probabilidad, descripcion FROM cartera", conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df