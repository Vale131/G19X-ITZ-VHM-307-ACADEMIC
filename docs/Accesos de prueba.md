# Accesos de Prueba y Seguridad | PluriOne

**Sistema Predictivo de Flujo de Efectivo y Tesorería Ejecutiva**  
**Identificador de Proyecto:** `G19X-ITZ-VHM-307-ACADEMIC`  
**Repositorio Oficial:** `https://github.com/Vale131/G19X-ITZ-VHM-307-ACADEMIC.git`  
**Versión:** v4.2 Producción  

---

## 1. Arquitectura de Gobernanza y Control de Acceso (RBAC)

En plataformas de gestión de tesorería y liquidez corporativa, la segregación de funciones es un requisito crítico de control interno. Quien registra operaciones diarias no debe tener privilegios para alterar políticas de acceso, y quien audita indicadores financieros no debe poder modificar registros contables subyacentes.

PluriOne implementa un modelo de **Control de Acceso Basado en Roles (RBAC)** bajo el **Principio de Menor Privilegio (PoLP)**, validado en la capa de datos (`modules/database.py`) y en el enrutamiento de vistas (`app.py`):

* **Analista de Tesorería:** Alimenta los datos operativos (históricos bancarios en CSV y cartera de cuentas por cobrar y por pagar) y simula escenarios de flujo, sin acceso al panel administrativo de cuentas.
* **Auditor de Riesgo:** Supervisa en modo de consulta las métricas de precisión fuera de muestra (**MAE**, **MAPE**, **mejora vs. Baseline**) y la exposición estocástica (**VaR 95%**, **VaR 99%**, **Probabilidad de Déficit**), sin capacidad de alterar registros operativos ni usuarios.
* **Director Financiero (CFO):** Concentra las facultades administrativas completas, la exportación ejecutiva en Excel (`.xlsx`) y la gestión integral del directorio de usuarios.

---

## 2. Matriz de Perfiles y Credenciales de Referencia

| Rol en Sistema | Correo de Referencia | Aprovisionamiento de Credencial | Alcance Operativo y Permisos |
| :--- | :--- | :--- | :--- |
| **Director Financiero (CFO)** | `admin@plurione.com` | Definida en `.env` mediante `ADMIN_INITIAL_PASSWORD` | **Acceso Total.** Único perfil con acceso a **Gestión de Usuarios** (altas, edición de rol/estatus, restablecimiento de clave y bajas), consulta global y exportación de reportes `.xlsx`. |
| **Analista de Tesorería** | `analista@plurione.com` | Alta desde el panel *Gestión de Usuarios* por el CFO | **Operación Financiera.** Carga de históricos CSV (`ds`, `Ingresos`, `Egresos`), registro y actualización de estatus en cartera (CxC / CxP) y proyección de escenarios. |
| **Auditor de Riesgo** | `auditor@plurione.com` | Alta desde el panel *Gestión de Usuarios* por el CFO | **Supervisión y Riesgo.** Lectura del Cockpit Financiero, auditoría de error Holdout (MAE / MAPE / Baseline) y modelado estocástico Monte Carlo (VaR). |

> **Nota de seguridad:** Las cuentas `analista@plurione.com` y `auditor@plurione.com` son identificadores de referencia para pruebas de segregación; no existen previamente en la base de datos hasta que el administrador las da de alta desde la interfaz.

---

## 3. Mecanismos de Protección de Credenciales

### 3.1. Cifrado Unidireccional con `bcrypt`
Ninguna contraseña se almacena ni se compara en texto plano dentro del código fuente ni en la base de datos SQLite (`flujo_efectivo.db`). El módulo `modules/database.py` utiliza `bcrypt` con generación dinámica de sal (`bcrypt.gensalt()`):

1. **Resistencia a fuerza bruta:** A diferencia de funciones hash de propósito general como MD5 o SHA-256 (optimizadas para velocidad), `bcrypt` incorpora un factor de costo computacional configurable que encarece drásticamente los ataques por diccionario o GPU.
2. **Sal aleatoria por registro:** Cada alta o actualización de contraseña genera una sal única, neutralizando ataques mediante tablas de arcoíris (*Rainbow Tables*) y garantizando que dos usuarios con la misma clave produzcan hashes completamente distintos.

### 3.2. Autenticación Resistente a Enumeración de Cuentas
La función `autenticar_usuario(email, password_plain)` aplica una secuencia estricta de validación:

1. Consulta el hash asociado al correo electrónico en la tabla `usuarios`.
2. Ejecuta `verificar_password(password_plain, u_pass_hash)` mediante `bcrypt.checkpw(...)`.
3. Únicamente cuando la contraseña coincide, evalúa si `estatus == "Inactivo"`.
4. Si el correo no existe o la contraseña no coincide, retorna `None` y la interfaz despliega un mensaje genérico sin revelar si la cuenta está registrada.

### 3.3. Sanitización de Sesión
En `app.py`, los atributos del perfil autenticado (`nombre` y `rol`) se procesan mediante `html.escape()` antes de renderizarse en la tarjeta de usuario de la barra lateral, mitigando riesgos de inyección HTML/XSS.

---

## 4. Configuración del Entorno (`.env`) y Primer Arranque

Antes de iniciar la aplicación por primera vez, crea el archivo `.env` en la raíz del proyecto a partir de la plantilla `.env.example`:

```bash
cp .env.example .env
```

Configura las variables de entorno:

```env
# Obligatoria: Contraseña inicial para crear el administrador (admin@plurione.com) en el primer arranque
ADMIN_INITIAL_PASSWORD=TuPasswordSegura2026!

# Opcional: Llave de API de Google AI Studio (no utiliza OpenAI) para modules/ai_copilot.py
GEMINI_API_KEY=
```

### Flujo de Inicialización Automática (`init_db()`)
1. Al ejecutar `python -m streamlit run app.py`, `init_db()` verifica la existencia de la tabla `usuarios` y busca el registro `admin@plurione.com`.
2. Si la cuenta no existe y `ADMIN_INITIAL_PASSWORD` está definida en el entorno, genera el hash `bcrypt` y registra al usuario **Valeria (Administrador)** con el perfil `Director Financiero (CFO)` y estatus `Activo`.
3. Si `ADMIN_INITIAL_PASSWORD` no fue configurada antes del primer arranque, el sistema emite una advertencia en consola sin recurrir a contraseñas predeterminadas en código. Para inicializar la cuenta posteriormente, define la variable en `.env`, elimina el archivo `flujo_efectivo.db` vacío y reinicia Streamlit.

---

## 5. Protocolo de Validación de Segregación de Roles

Para verificar el cumplimiento de los controles RBAC en un entorno de evaluación:

1. **Acceso Administrativo:** Iniciar sesión con `admin@plurione.com` y la contraseña establecida en `ADMIN_INITIAL_PASSWORD`. Confirmar que `data/sample_flujo.csv` se precarga automáticamente si el histórico está vacío y que la opción **Gestión de Usuarios** es visible en el menú lateral.
2. **Aprovisionamiento de Perfiles:** Crear desde la pestaña *Dar de Alta Usuario* las cuentas `analista@plurione.com` (`Analista de Tesorería`) y `auditor@plurione.com` (`Auditor de Riesgo`).
3. **Verificación de Restricciones:** Cerrar sesión e ingresar con cada perfil creado para corroborar que:
   * Ambos perfiles operan sus respectivos tableros y simulaciones sin acceso al módulo **Gestión de Usuarios**.
   * Al cambiar el estatus de una cuenta a `Inactivo` desde el panel CFO, el inicio de sesión de dicho usuario queda bloqueado de inmediato.