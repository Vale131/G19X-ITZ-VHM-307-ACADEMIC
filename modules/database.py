import sqlite3
import pandas as pd
import bcrypt
import os

DB_NAME = "flujo_efectivo.db"

def hash_password(password: str) -> str:
    """Genera un hash seguro utilizando bcrypt con sal incorporada."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verificar_password(password_plain: str, password_hashed: str) -> bool:
    """Verifica estrictamente la contraseña contra el hash bcrypt sin respaldos en texto plano."""
    if not password_hashed:
        return False
    try:
        return bcrypt.checkpw(password_plain.encode('utf-8'), password_hashed.encode('utf-8'))
    except Exception:
        return False

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    """Inicializa la base de datos relacional SQLite y asegura el esquema unificado."""
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
    cols = [row[1] for row in cursor.fetchall()]
    if "estatus" not in cols:
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

    # Tabla Unificada de Cartera (CxC / CxP)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cartera (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,
        cliente_proveedor TEXT NOT NULL,
        monto REAL NOT NULL,
        fecha_vencimiento TEXT NOT NULL,
        probabilidad REAL DEFAULT 1.0,
        estatus TEXT DEFAULT 'Pendiente'
    )
    """)

    cursor.execute("PRAGMA table_info(cartera)")
    cartera_cols = [row[1] for row in cursor.fetchall()]
    if "probabilidad" not in cartera_cols:
        cursor.execute("ALTER TABLE cartera ADD COLUMN probabilidad REAL DEFAULT 1.0")

    # Administrador inicial leyendo de .env sin clave por defecto hardcodeada
    admin_email = "admin@plurione.com"
    admin_raw_pass = os.getenv("ADMIN_INITIAL_PASSWORD")
    
    if not admin_raw_pass:
        print("ADVERTENCIA: La variable ADMIN_INITIAL_PASSWORD no está configurada en .env.")
    else:
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (admin_email,))
        if not cursor.fetchone():
            admin_pass = hash_password(admin_raw_pass)
            cursor.execute("""
                INSERT INTO usuarios (email, password, nombre, rol, estatus)
                VALUES (?, ?, ?, ?, ?)
            """, (admin_email, admin_pass, "Valeria (Administrador)", "Director Financiero (CFO)", "Activo"))

    conn.commit()
    conn.close()

def autenticar_usuario(email: str, password_plain: str):
    """Autentica a un usuario comparando el hash bcrypt y previniendo la enumeración de cuentas."""
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
        
        # Validación prioritaria de contraseña para evitar enumeración
        if verificar_password(password_plain, u_pass_hash):
            if u_estatus == "Inactivo":
                return {"error": "El usuario se encuentra inactivo. Contacte al administrador."}
            return {
                "id": user_id,
                "email": u_email,
                "nombre": u_nombre,
                "rol": u_rol,
                "estatus": u_estatus
            }
    return None

def registrar_usuario(email: str, password_plain: str, nombre: str, rol: str, estatus: str = "Activo"):
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
        return True, "Usuario registrado exitosamente."
    except sqlite3.IntegrityError:
        conn.close()
        return False, "El correo electrónico ya se encuentra registrado."

def actualizar_usuario(user_id: int, email: str, nombre: str, rol: str, estatus: str, nueva_password: str = None):
    """Actualiza la información del usuario en la base de datos."""
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
    """Guarda o actualiza el histórico de flujo manteniendo el esquema de la tabla."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM historico_flujo")
        conn.commit()
        df.to_sql('historico_flujo', conn, if_exists='append', index=False)
    except Exception as e:
        conn.rollback()
        raise e
    finally:
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
        df = pd.DataFrame(columns=['id', 'tipo', 'cliente_proveedor', 'monto', 'fecha_vencimiento', 'probabilidad', 'estatus'])
    conn.close()
    return df

def guardar_cartera_db(df):
    """Guarda o actualiza registros de cartera mediante INSERT / UPDATE directos (UPSERT) sin borrar la estructura."""
    if df.empty:
        return
    conn = get_connection()
    cursor = conn.cursor()
    try:
        for _, row in df.iterrows():
            reg_id = row.get('id')
            prob = row.get('probabilidad', 1.0)
            prob = 1.0 if pd.isna(prob) else float(prob)
            estatus = row.get('estatus', 'Pendiente')
            estatus = 'Pendiente' if pd.isna(estatus) else str(estatus)

            if pd.notna(reg_id) and reg_id:
                cursor.execute("""
                    INSERT INTO cartera (id, tipo, cliente_proveedor, monto, fecha_vencimiento, probabilidad, estatus)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        tipo = excluded.tipo,
                        cliente_proveedor = excluded.cliente_proveedor,
                        monto = excluded.monto,
                        fecha_vencimiento = excluded.fecha_vencimiento,
                        probabilidad = excluded.probabilidad,
                        estatus = excluded.estatus
                """, (int(reg_id), str(row['tipo']), str(row['cliente_proveedor']), float(row['monto']), str(row['fecha_vencimiento']), prob, estatus))
            else:
                cursor.execute("""
                    INSERT INTO cartera (tipo, cliente_proveedor, monto, fecha_vencimiento, probabilidad, estatus)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (str(row['tipo']), str(row['cliente_proveedor']), float(row['monto']), str(row['fecha_vencimiento']), prob, estatus))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def insertar_compromiso_cartera(tipo: str, cliente_proveedor: str, monto: float, fecha_vencimiento: str, probabilidad: float, estatus: str = 'Pendiente') -> bool:
    """Inserta un registro individual en la tabla cartera usando SQL directo."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO cartera (tipo, cliente_proveedor, monto, fecha_vencimiento, probabilidad, estatus)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (tipo, cliente_proveedor, monto, fecha_vencimiento, probabilidad, estatus))
        conn.commit()
        conn.close()
        return True
    except Exception:
        conn.close()
        return False

def actualizar_compromiso_cartera(reg_id: int, tipo: str, cliente_proveedor: str, monto: float, fecha_vencimiento: str, probabilidad: float, estatus: str) -> bool:
    """Actualiza todos los campos de un registro específico en la tabla cartera mediante UPDATE directo."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE cartera
            SET tipo = ?, cliente_proveedor = ?, monto = ?, fecha_vencimiento = ?, probabilidad = ?, estatus = ?
            WHERE id = ?
        """, (tipo, cliente_proveedor, monto, fecha_vencimiento, probabilidad, estatus, reg_id))
        conn.commit()
        conn.close()
        return True
    except Exception:
        conn.close()
        return False

def actualizar_estatus_cartera(reg_id: int, nuevo_estatus: str) -> bool:
    """Actualiza únicamente el estatus de una fila en la tabla cartera por su ID."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE cartera
            SET estatus = ?
            WHERE id = ?
        """, (nuevo_estatus, reg_id))
        conn.commit()
        conn.close()
        return True
    except Exception:
        conn.close()
        return False

def eliminar_compromiso_cartera(reg_id: int) -> bool:
    """Elimina un registro específico de la tabla cartera por su ID."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM cartera WHERE id = ?", (reg_id,))
        conn.commit()
        conn.close()
        return True
    except Exception:
        conn.close()
        return False