import sqlite3
import hashlib
import pandas as pd

DB_NAME = "flujo_efectivo.db"

def hash_password(password: str) -> str:
    """Encripta la contraseña utilizando SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def init_db():
    """Inicializa la base de datos SQLite con las tablas de histórico, cartera y usuarios."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabla de Histórico
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

    # Tabla de Usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password_hash TEXT,
            nombre TEXT,
            rol TEXT
        )
    """)
    
    # Insertar usuario administrador por defecto si no existen usuarios
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        default_user = "admin@plurione.com"
        default_pass = hash_password("PluriOne2026!")
        cursor.execute(
            "INSERT INTO usuarios (email, password_hash, nombre, rol) VALUES (?, ?, ?, ?)",
            (default_user, default_pass, "Director Financiero (CFO)", "Administrador")
        )

    conn.commit()
    conn.close()

def autenticar_usuario(email, password):
    """Verifica si las credenciales ingresadas coinciden con SQLite."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    pass_hash = hash_password(password)
    
    cursor.execute(
        "SELECT email, nombre, rol FROM usuarios WHERE email = ? AND password_hash = ?",
        (email.strip().lower(), pass_hash)
    )
    usuario = cursor.fetchone()
    conn.close()
    
    if usuario:
        return {"email": usuario[0], "nombre": usuario[1], "rol": usuario[2]}
    return None

def registrar_usuario(email, password, nombre, rol="Analista Financiero"):
    """Registra un nuevo usuario en la base de datos SQLite con contraseña cifrada."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    pass_hash = hash_password(password)
    try:
        cursor.execute(
            "INSERT INTO usuarios (email, password_hash, nombre, rol) VALUES (?, ?, ?, ?)",
            (email.strip().lower(), pass_hash, nombre.strip(), rol)
        )
        conn.commit()
        conn.close()
        return True, "¡Usuario registrado exitosamente! Ya puede iniciar sesión."
    except sqlite3.IntegrityError:
        conn.close()
        return False, "El correo electrónico ya se encuentra registrado."
    except Exception as e:
        conn.close()
        return False, f"Error al registrar el usuario: {e}"

def guardar_historico_db(df):
    if df is None or df.empty:
        return
    df_clean = df.copy()
    df_clean['ds'] = pd.to_datetime(df_clean['ds']).dt.strftime('%Y-%m-%d')
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
    if df is None or df.empty:
        return
    conn = sqlite3.connect(DB_NAME)
    df.to_sql("cartera", conn, if_exists="replace", index=False)
    conn.close()

def obtener_cartera_db():
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql("SELECT fecha, monto, tipo, probabilidad, descripcion FROM cartera", conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df