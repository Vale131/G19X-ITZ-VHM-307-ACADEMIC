import sqlite3
import pandas as pd
import bcrypt
import os

DB_NAME = "flujo_efectivo.db"

def hash_password(password: str) -> str:
    """Genera un hash seguro utilizando el algoritmo bcrypt con sal incorporada."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verificar_password(password_plain: str, password_hashed: str) -> bool:
    """Verifica si la contraseña ingresada coincide con el hash bcrypt almacenado."""
    try:
        return bcrypt.checkpw(password_plain.encode('utf-8'), password_hashed.encode('utf-8'))
    except Exception:
        # Respaldo para compatibilidad previa en caso de hashes antiguos
        return password_plain == password_hashed

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    """Inicializa la base de datos, aplica migraciones y crea al administrador mediante variables de entorno."""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla de Usuarios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        nombre TEXT NOT NULL,
        rol TEXT NOT NULL,
        estatus TEXT DEFAULT 'Activo'
    )
    """)

    cursor.execute("PRAGMA table_info(usuarios)")
    columnas = [row[1] for row in cursor.fetchall()]
    if "estatus" not in columnas:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN estatus TEXT DEFAULT 'Activo'")

    # Tabla de Histórico de Flujo
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historico_flujo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ds TEXT NOT NULL,
        Ingresos REAL NOT NULL,
        Egresos REAL NOT NULL
    )
    """)

    # Tabla de Cartera CxC / CxP
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cartera (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,
        cliente_proveedor TEXT NOT NULL,
        monto REAL NOT NULL,
        fecha_vencimiento TEXT NOT NULL,
        estatus TEXT NOT NULL
    )
    """)

    # Crear Administrador principal leyendo la contraseña desde variable de entorno .env
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = ?", ("admin@plurione.com",))
    if cursor.fetchone()[0] == 0:
        admin_email = "admin@plurione.com"
        admin_raw_pass = os.getenv("ADMIN_INITIAL_PASSWORD", "admin123")
        admin_pass = hash_password(admin_raw_pass)
        admin_nombre = "Valeria (Administrador)"
        admin_rol = "Director Financiero (CFO)"

        cursor.execute("""
            INSERT INTO usuarios (email, password, nombre, rol, estatus)
            VALUES (?, ?, ?, ?, ?)
        """, (admin_email, admin_pass, admin_nombre, admin_rol, "Activo"))

    conn.commit()
    conn.close()

def autenticar_usuario(email: str, password_plain: str):
    """Autentica a un usuario activo comparando la contraseña con hash bcrypt."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, email, password, nombre, rol, estatus FROM usuarios
        WHERE email = ?
    """, (email,))
    
    row = cursor.fetchone()
    conn.close()

    if row:
        user_id, u_email, u_pass_hash, u_nombre, u_rol, u_estatus = row
        if u_estatus == "Inactivo":
            return {"error": "El usuario se encuentra dado de baja (Inactivo). Contacte al administrador."}
        
        if verificar_password(password_plain, u_pass_hash):
            return {
                "id": user_id,
                "email": u_email,
                "nombre": u_nombre,
                "rol": u_rol,
                "estatus": u_estatus
            }
    return None

def registrar_usuario(email: str, password_plain: str, nombre: str, rol: str, estatus: str = "Activo"):
    """Registra un nuevo usuario aplicando cifrado bcrypt a la contraseña."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        pass_hashed = hash_password(password_plain)
        cursor.execute("""
            INSERT INTO usuarios (email, password, nombre, rol, estatus)
            VALUES (?, ?, ?, ?, ?)
        """, (email, pass_hashed, nombre, rol, estatus))
        conn.commit()
        conn.close()
        return True, "Usuario creado exitosamente."
    except sqlite3.IntegrityError:
        conn.close()
        return False, "El correo electrónico ya se encuentra registrado."

def actualizar_usuario(user_id: int, email: str, nombre: str, rol: str, estatus: str, nueva_password: str = None):
    """Actualiza la información de un usuario existente con hashing dinámico."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if nueva_password and nueva_password.strip():
            pass_hashed = hash_password(nueva_password)
            cursor.execute("""
                UPDATE usuarios
                SET email = ?, nombre = ?, rol = ?, estatus = ?, password = ?
                WHERE id = ?
            """, (email, nombre, rol, estatus, pass_hashed, user_id))
        else:
            cursor.execute("""
                UPDATE usuarios
                SET email = ?, nombre = ?, rol = ?, estatus = ?
                WHERE id = ?
            """, (email, nombre, rol, estatus, user_id))
        conn.commit()
        conn.close()
        return True, "Usuario actualizado correctamente."
    except Exception as e:
        conn.close()
        return False, f"Error al actualizar usuario: {e}"

def eliminar_usuario(user_id: int):
    """Elimina un usuario por su ID mediante consulta SQL parametrizada."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True, "Usuario eliminado correctamente."
    except Exception as e:
        conn.close()
        return False, f"Error al eliminar usuario: {e}"

def obtener_usuarios_db():
    conn = get_connection()
    try:
        df = pd.read_sql("SELECT id, email, nombre, rol, estatus FROM usuarios", conn)
    except Exception:
        df = pd.DataFrame(columns=['id', 'email', 'nombre', 'rol', 'estatus'])
    conn.close()
    return df

def guardar_historico_db(df):
    conn = get_connection()
    df.to_sql('historico_flujo', conn, if_exists='replace', index=False)
    conn.close()

def obtener_historico_db():
    conn = get_connection()
    try:
        df = pd.read_sql("SELECT ds, Ingresos, Egresos FROM historico_flujo", conn)
        df['ds'] = pd.to_datetime(df['ds'])
    except Exception:
        df = pd.DataFrame(columns=['ds', 'Ingresos', 'Egresos'])
    conn.close()
    return df

def obtener_cartera_db():
    conn = get_connection()
    try:
        df = pd.read_sql("SELECT * FROM cartera", conn)
    except Exception:
        df = pd.DataFrame(columns=['id', 'tipo', 'cliente_proveedor', 'monto', 'fecha_vencimiento', 'estatus'])
    conn.close()
    return df

def guardar_cartera_db(df):
    conn = get_connection()
    df.to_sql('cartera', conn, if_exists='replace', index=False)
    conn.close()