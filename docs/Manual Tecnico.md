# Manual Técnico de Módulos, Contratos y Mantenibilidad | PluriOne

**Sistema Predictivo de Flujo de Efectivo y Tesorería Ejecutiva**  
**Identificador de Proyecto:** `G19X-ITZ-VHM-307-ACADEMIC`  
**Repositorio Oficial:** `https://github.com/Vale131/G19X-ITZ-VHM-307-ACADEMIC.git`  
**Versión:** v4.2 Producción  

---

## 1. Propósito, Alcance y Estándares de Ingeniería

Este manual constituye la especificación técnica de referencia para el mantenimiento, auditoría de código, extensión funcional y escalamiento empresarial de **PluriOne**. Está dirigido a ingenieros de software, científicos de datos y auditores técnicos responsables de operar o evolucionar el sistema.

### 1.1. Principios de Diseño Implementados
1. **Separación Estricta de Responsabilidades (SRP):** La capa de presentación (`app.py`) no contiene sentencias SQL ni fórmulas estadísticas; delega toda persistencia a `modules/database.py` y todo cálculo cuantitativo a `modules/forecasting.py` y `modules/risk.py`.
2. **Seguridad por Defecto:** Parametrización obligatoria de consultas SQL (`?`), almacenamiento exclusivo de credenciales mediante `bcrypt` con sal aleatoria, aislamiento de secretos en `.env` y escape HTML (`html.escape`) en metadatos de sesión.
3. **Determinismo y Auditabilidad:** Uso de semilla fija (`np.random.seed(42)`) en simulaciones estocásticas y validación temporal estricta (*Holdout* de 14 días) sin fuga de datos entre entrenamiento y prueba.
4. **Aislamiento de Pruebas:** La suite `pytest` redirige dinámicamente el puntero de base de datos hacia un archivo temporal que se destruye tras cada caso de prueba, protegiendo los datos productivos.

---

## 2. Ciclo de Vida de Ejecución y Gestión de Estado

Cada interacción del usuario en Streamlit dispara un ciclo reactivo determinista gobernado por `app.py`:

```text
[1] Arranque / Rerun de Streamlit (app.py)
       |
       +--> load_dotenv()        : Carga ADMIN_INITIAL_PASSWORD y GEMINI_API_KEY desde .env
       +--> init_db()            : Garantiza esquema SQLite y aprovisiona admin@plurione.com
       +--> aplicar_estilos_css(): Inyecta hoja de estilos corporativa
       |
[2] Guardia de Autenticación (modules/auth.py)
       |
       +--> Si "user" not in st.session_state: render_login() y st.stop()
       |
[3] Sincronización de Datos y Precarga Inicial
       |
       +--> df_hist = obtener_historico_db()
       +--> Si df_hist.empty y existe data/sample_flujo.csv:
       |       ingesta automática -> guardar_historico_db()
       +--> df_cartera = obtener_cartera_db()
       |
[4] Pipeline Analítico Reactivo (según Escenario y Horizonte seleccionados)
       |
       +--> calcular_metricas_error(df_hist)          -> {mae, mape, status}
       +--> calcular_mejora_vs_baseline(df_hist)      -> float (% mejora)
       +--> generar_pronostico_real(df_hist, df_cartera, dias, escenario) -> (df_proy, df_clean)
       +--> ejecutar_simulacion_monte_carlo(df_proy, saldo_inicial)      -> res_mc
       +--> generar_reporte_excel(df_hist, df_proy, df_cartera, res_mc)  -> bytes (.xlsx)
       |
[5] Renderizado de Vista Activa y Control RBAC
```

### Variables Principales en `st.session_state`
* `st.session_state["user"]` (`dict`): Perfil autenticado con claves `id`, `email`, `nombre`, `rol`, `estatus`.
* `st.session_state["copilot_messages"]` (`list[dict]`): Historial conversacional del Copiloto CFO (`role`, `content`).
* `st.session_state["support_messages"]` (`list[dict]`): Historial conversacional del Agente de Soporte Técnico.
* `st.session_state["custom_api_key"]` (`str`, opcional): Llave de sesión de Google AI Studio en caso de sobreescribir `GEMINI_API_KEY`.

---

## 3. Especificación Detallada por Módulo

### 3.1. `app.py` (Orquestador Principal)
* **Responsabilidad:** Control de flujo principal, barra lateral de navegación, validación de permisos administrativos (`es_admin = user.get("rol") == "Director Financiero (CFO)"`), despliegue de métricas KPI y panel CRUD de usuarios.
* **Seguridad de Interfaz:** Sanitiza `user["nombre"]` y `user["rol"]` mediante `html.escape()` antes de insertarlos en bloques `st.markdown(..., unsafe_allow_html=True)`.
* **Estándar Visual:** Utiliza `width="stretch"` en componentes `st.plotly_chart`, `st.dataframe` y `st.button` para compatibilidad con versiones modernas de Streamlit.

---

### 3.2. `modules/database.py` (Persistencia Relacional y Criptografía)
Gestiona todas las transacciones contra `DB_NAME = "flujo_efectivo.db"`.

#### Catálogo de Funciones
| Función y Firma | Descripción Técnica | Comportamiento Transaccional |
| :--- | :--- | :--- |
| `get_connection() -> sqlite3.Connection` | Abre conexión hacia `DB_NAME` con `check_same_thread=False`. | Retorna conexión activa para bloques `try...except...finally`. |
| `hash_password(password: str) -> str` | Codifica `password` a UTF-8 y aplica `bcrypt.hashpw(..., bcrypt.gensalt())`. | Genera sal criptográfica aleatoria por cada llamada. |
| `verificar_password(password_plain: str, password_hashed: str) -> bool` | Valida contraseña en texto plano contra hash almacenado mediante `bcrypt.checkpw`. | Captura excepciones de formato inválido y retorna `False` de forma segura. |
| `init_db() -> None` | Crea tablas `usuarios`, `historico_flujo` y `cartera`; audita columnas vía `PRAGMA table_info` y crea `admin@plurione.com` leyendo `ADMIN_INITIAL_PASSWORD`. | Si `ADMIN_INITIAL_PASSWORD` está ausente o vacía, emite `warnings.warn(...)` sin insertar contraseñas por defecto. |
| `autenticar_usuario(email: str, password_plain: str) -> dict \| None` | Consulta usuario por `email`, valida hash `bcrypt` y posteriormente verifica `estatus == "Activo"`. | Previene enumeración de cuentas verificando credencial antes de estatus. |
| `obtener_usuarios_db() -> pd.DataFrame` | Consulta `id, email, nombre, rol, estatus` ordenados por `id ASC`. | Excluye deliberadamente la columna `password` del resultado. |
| `crear_usuario_db(email, password_plain, nombre, rol, estatus="Activo") -> tuple[bool, str]` | Inserta nuevo registro con contraseña cifrada en `usuarios`. | Captura `sqlite3.IntegrityError` si el `email` ya existe. |
| `actualizar_usuario_db(user_id, email, nombre, rol, estatus, nueva_password=None) -> tuple[bool, str]` | Actualiza metadatos del usuario y, si `nueva_password` no está vacía, recalcula su hash `bcrypt`. | Ejecuta `UPDATE` parametrizado con `commit()`. |
| `eliminar_usuario_db(user_id: int) -> tuple[bool, str]` | Elimina registro por `id` tras verificar que no corresponda a `admin@plurione.com`. | Protege la cuenta maestra administrativa contra borrado. |
| `guardar_historico_db(df: pd.DataFrame) -> None` | Normaliza columnas (`ds`, `Ingresos`, `Egresos`), limpia registros previos e inserta la serie histórica validada. | Ejecuta dentro de transacción con `rollback()` ante fallo. |
| `obtener_historico_db() -> pd.DataFrame` | Recupera registros históricos ordenados cronológicamente por `ds ASC`. | Retorna `DataFrame` vacío con columnas estándar si no hay datos. |
| `guardar_cartera_db(df: pd.DataFrame) -> None` | Sincroniza registros de cartera mediante `INSERT INTO cartera ... ON CONFLICT(id) DO UPDATE SET ...`. | Preserva llaves primarias `id` existentes sin destruir la tabla. |
| `insertar_compromiso_cartera(tipo, cliente_proveedor, monto, fecha_vencimiento, probabilidad=1.0, estatus="Pendiente") -> int` | Ejecuta `INSERT INTO cartera` parametrizado para un nuevo compromiso. | Ejecuta `commit()` y retorna `cursor.lastrowid`. |
| `actualizar_compromiso_cartera(reg_id, tipo, cliente_proveedor, monto, fecha_vencimiento, probabilidad, estatus) -> bool` | Actualiza todos los campos de un compromiso existente por `id`. | Retorna `True` si `cursor.rowcount > 0`. |
| `actualizar_estatus_cartera(reg_id: int, nuevo_estatus: str) -> bool` | Actualiza únicamente la columna `estatus` (`Pendiente`, `Pagado`, `Cancelado`) para el `id` indicado. | Operación atómica con `commit()` y `rollback()`. |
| `eliminar_compromiso_cartera(reg_id: int) -> bool` | Elimina un compromiso específico por `id`. | Operación atómica parametrizada. |

---

### 3.3. `modules/forecasting.py` (Motor Predictivo y Validación Holdout)

#### Catálogo de Funciones
* `calcular_metricas_error(df_hist: pd.DataFrame) -> dict`:
  * Requiere al menos 14 registros históricos (`len(df_hist) >= 14`).
  * Divide cronológicamente en `train = df_clean.iloc[:-14]` y `test = df_clean.iloc[-14:]`.
  * Calcula medias de `Ingresos` y `Egresos` agrupadas por `dayofweek` ($0 = \text{Lunes}, \dots, 6 = \text{Domingo}$) únicamente sobre `train` para evitar fuga de información.
  * Evalúa sobre `test` el flujo neto predicho frente al real y retorna:
    ```python
    {
        "mae": float,
        "mape": float,
        "status": "Evaluación basada en Holdout (14 días)"
    }
    ```
* `calcular_mejora_vs_baseline(df_hist: pd.DataFrame, dias_holdout: int = 14) -> float`:
  * Requiere `len(df_hist) >= (dias_holdout + 7)`.
  * Calcula $\text{MAE}_{\text{baseline}}$ usando como predicción constante el promedio global simple de `Flujo_Neto` en `train`.
  * Calcula $\text{MAE}_{\text{modelo}}$ usando la media estacional por `dayofweek` en `train`.
  * Retorna como `float`:
    $$\text{mejora} = \frac{\text{MAE}_{\text{baseline}} - \text{MAE}_{\text{modelo}}}{\text{MAE}_{\text{baseline}}} \times 100.0$$
* `generar_pronostico_real(df_hist, df_cartera=None, dias_horizonte=30, escenario="Base", saldo_inicial=None) -> tuple[pd.DataFrame, pd.DataFrame]`:
  * Determina el saldo base inicial: si `saldo_inicial is None`, calcula `float((df_clean['Ingresos'] - df_clean['Egresos']).sum())`.
  * Aplica los multiplicadores estratégicos por escenario:
    * `"Base"`: `(1.00, 1.00)`
    * `"Optimista"`: `(1.15, 0.90)`
    * `"Conservador"`: `(0.85, 1.10)`
  * Recorre las fechas futuras $t \in [1, \text{dias\_horizonte}]$ posteriores a `df_clean['ds'].max()`.
  * Filtra `df_cartera` donde `fecha_vencimiento == fecha_actual` y `estatus not in ('Pagado', 'Cancelado')`. Normaliza `probabilidad` (si $> 1.0$, divide entre $100.0$) y suma `monto * probabilidad` a `Ingresos` (si `'CXC'` o `'COBRO'` en `tipo.upper()`) o a `Egresos` (si `'CXP'` o `'PAGO'` en `tipo.upper()`).
  * Calcula `Flujo_Neto = Ingresos - Egresos` y `Saldo_Acumulado = saldo_base + Flujo_Neto.cumsum()`.
* `crear_grafica_escenarios(df_proy)`, `crear_grafica_barras_categoria(df_proy)`, `crear_grafica_saldos_area(df_proy)`: Generan figuras interactivas `plotly.graph_objects.Figure`.

---

### 3.4. `modules/risk.py` (Simulación Estocástica Monte Carlo)
* `ejecutar_simulacion_monte_carlo(df_proyeccion, saldo_inicial=500000.0, num_simulaciones=1000, umbral_deficit=0.0) -> dict`:
  * Fija `np.random.seed(42)` para reproducibilidad determinista en auditorías y pruebas.
  * Estima la volatilidad diaria $\sigma = \text{std}(\text{Flujo\_Neto})$ (con piso de respaldo si $\sigma = 0$).
  * Genera matriz de choques aleatorios $\epsilon \sim \mathcal{N}(0, \sigma^2)$ de dimensión $(\text{num\_simulaciones}, T)$.
  * Construye las $1,000$ trayectorias acumuladas $S_t^{(m)} = \text{saldo\_inicial} + \sum_{k=1}^{t} (FN_k + \epsilon_k^{(m)})$.
  * Calcula y retorna el contrato unificado:
    ```python
    {
        "var_95": float,               # max(0.0, saldo_final_esperado - percentile(saldos_finales, 5))
        "var_99": float,               # max(0.0, saldo_final_esperado - percentile(saldos_finales, 1))
        "prob_deficit": float,         # % de trayectorias con min_t(S_t) < umbral_deficit
        "saldo_final_esperado": float, # mean(saldos_finales)
        "saldos_finales": list[float]  # Distribución completa para histograma
    }
    ```
* `crear_grafica_monte_carlo(res_mc: dict) -> go.Figure`: Construye histograma de saldos finales con líneas verticales marcando el saldo esperado, $\text{VaR}_{95\%}$ y $\text{VaR}_{99\%}$.

---

### 3.5. `modules/reports.py` (Generador de Reportes Ejecutivos Excel)
* `generar_reporte_excel(df_historico, df_forecast, df_cartera, res_mc) -> bytes`:
  * Instancia un libro `openpyxl.Workbook()` en memoria (`io.BytesIO`).
  * Construye cuatro hojas estructuradas:
    1. **Resumen & VaR:** Métricas consolidadas de proyección y simulación estocástica, leyendo explícitamente `res_mc.get('prob_deficit', 0.0)`.
    2. **Proyección de Flujo:** Tabla diaria con formato monetario `"$"#,##0.00`.
    3. **Cartera CxC y CxP:** Listado de compromisos con formato porcentual `0.00%` en probabilidad.
    4. **Histórico de Caja:** Serie histórica base utilizada para el modelado.
  * Aplica encabezados corporativos (`#6D1B2A`, texto blanco en negrita), bordes delgados y autoajuste de ancho de columnas basado en la longitud máxima de celda.

---

### 3.6. Módulos de Interfaz, IA y Soporte
* `modules/cxc_cxp.py`: Renderiza las pestañas de consulta y alta de cartera conectadas directamente a `insertar_compromiso_cartera()` y `actualizar_estatus_cartera()` mediante el `id` real de SQLite.
* `modules/auth.py`: Gestiona el formulario de acceso y almacena el diccionario de sesión en `st.session_state["user"]`.
* `modules/ai_copilot.py`: Lee `os.getenv("GEMINI_API_KEY")` (con respaldo `OPENAI_API_KEY`). Si existe llave, instancia el cliente apuntando a `https://generativelanguage.googleapis.com/v1beta/openai/` con `model="gemini-1.5-flash"`; en caso contrario, o ante excepción de red, ejecuta `responder_localmente(prompt, contexto_financiero)`.
* `modules/support_agent.py`: Proveedor de ayuda contextual sobre navegación y requisitos de datos.
* `modules/styles.py`: Define variables CSS, tarjetas KPI y temas visuales de Plotly.

---

## 4. Esquema Relacional SQLite (`flujo_efectivo.db`)

```sql
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    nombre TEXT NOT NULL,
    rol TEXT NOT NULL,
    estatus TEXT DEFAULT 'Activo'
);

CREATE TABLE IF NOT EXISTS historico_flujo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ds TEXT NOT NULL,
    Ingresos REAL NOT NULL,
    Egresos REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS cartera (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    cliente_proveedor TEXT NOT NULL,
    monto REAL NOT NULL,
    fecha_vencimiento TEXT NOT NULL,
    probabilidad REAL DEFAULT 1.0,
    estatus TEXT DEFAULT 'Pendiente'
);
```

### Respaldo y Recuperación de Datos
* Dado que SQLite consolida el estado completo en el archivo `flujo_efectivo.db` (excluido del control de versiones en `.gitignore`), el respaldo operativo consiste en copiar dicho archivo mientras no existan escrituras activas o ejecutar `.backup` desde la CLI de `sqlite3`.
* En caso de corrupción o reinicio limpio de entorno, basta detener Streamlit, respaldar o eliminar `flujo_efectivo.db` y reiniciar la aplicación con `.env` configurado para regenerar el esquema y recargar `data/sample_flujo.csv`.

---

## 5. Contratos de Datos entre Módulos

Cualquier modificación futura en los motores de cálculo debe respetar estrictamente las siguientes interfaces de intercambio para evitar regresiones en vistas o exportaciones:

| Contrato | Productor | Consumidores | Esquema / Claves Obligatorias |
| :--- | :--- | :--- | :--- |
| **Diccionario de Riesgo (`res_mc`)** | `modules/risk.py` | `app.py`, `modules/reports.py` | `var_95` (`float`), `var_99` (`float`), `prob_deficit` (`float`), `saldo_final_esperado` (`float`), `saldos_finales` (`list`) |
| **DataFrame de Pronóstico (`df_proy`)** | `modules/forecasting.py` | `app.py`, `modules/risk.py`, `modules/reports.py` | `ds` (`datetime64`), `Ingresos` (`float`), `Egresos` (`float`), `Flujo_Neto` (`float`), `Saldo_Acumulado` (`float`) |
| **DataFrame de Cartera (`df_cartera`)** | `modules/database.py` | `app.py`, `modules/cxc_cxp.py`, `modules/forecasting.py`, `modules/reports.py` | `id` (`int`), `tipo` (`str`), `cliente_proveedor` (`str`), `monto` (`float`), `fecha_vencimiento` (`str`), `probabilidad` (`float`), `estatus` (`str`) |
| **Diccionario Holdout** | `modules/forecasting.py` | `app.py` | `mae` (`float`), `mape` (`float`), `status` (`str`) |

---

## 6. Suite de Pruebas Automatizadas (`tests/test_core.py`)

La calidad del núcleo matemático y de persistencia se valida mediante `pytest` sin alterar la base de datos operativa:

### 6.1. Aislamiento mediante Fixture (`setup_and_teardown_test_db`)
* Decorada con `@pytest.fixture(autouse=True)`.
* Antes de cada prueba, sustituye `database.DB_NAME = "flujo_efectivo_test.db"`, elimina residuos previos e invoca `database.init_db()`.
* Al finalizar cada prueba (`yield`), elimina `"flujo_efectivo_test.db"` y restaura el nombre original de la base de datos.

### 6.2. Cobertura de Casos de Prueba (7 Pruebas)
1. `test_hash_y_verificacion_password`: Verifica que `hash_password` genere cadenas distintas al texto plano y que `verificar_password` discrimine claves válidas e inválidas.
2. `test_actualizar_usuario_con_nueva_password`: Valida la actualización integral de atributos y re-cifrado `bcrypt` en SQLite.
3. `test_calculo_metricas_error_holdout`: Verifica el cálculo no negativo de `mae` y `mape` sobre series con ventana Holdout de 14 días.
4. `test_modelo_le_gana_al_promedio_con_estacionalidad`: Comprueba que `calcular_mejora_vs_baseline` retorne un `float` positivo cuando existen patrones semanales marcados.
5. `test_cartera_crud_operaciones_directas`: Verifica inserción (`insertar_compromiso_cartera`) y actualización (`actualizar_estatus_cartera`) directa en SQLite preservando identificadores.
6. `test_cartera_ponderada_en_pronostico`: Audita matemáticamente que un compromiso CxC de $\$100,000$ con probabilidad $0.75$ incremente exactamente en $\$75,000$ los ingresos proyectados en su fecha de vencimiento.
7. `test_simulacion_monte_carlo_var_unificado`: Confirma la presencia y consistencia estadística de `var_95`, `var_99` ($\text{VaR}_{99\%} \ge \text{VaR}_{95\%}$) y `prob_deficit` ($\in [0, 100]$).

### 6.3. Ejecución de Pruebas
```bash
python -m pytest tests/ -v
```

---

## 7. Guía de Seguridad y Escalamiento Empresarial

### 7.1. Lista de Verificación de Seguridad en Despliegue
* Confirmar que `.env` y `flujo_efectivo.db` permanezcan listados en `.gitignore` y nunca se suban al repositorio remoto.
* Establecer `ADMIN_INITIAL_PASSWORD` con una longitud mínima de 12 caracteres combinando mayúsculas, minúsculas, números y símbolos.
* En despliegues expuestos en red corporativa o nube, colocar Streamlit detrás de un proxy inverso (Nginx o Caddy) con certificado **TLS/HTTPS** obligatorio.

### 7.2. Ruta de Evolución Arquitectónica
1. **Migración a PostgreSQL:** Sustituir el conector `sqlite3` en `modules/database.py` por `psycopg2` o `SQLAlchemy` apuntando a una base de datos gestionada (AWS RDS, Google Cloud SQL o Azure Database for PostgreSQL) para soportar concurrencia multi-usuario de escritura.
2. **Contenerización con Docker:** Empaquetar la aplicación sobre `python:3.11-slim`, instalando `requirements.txt`, exponiendo el puerto `8501` e inyectando `ADMIN_INITIAL_PASSWORD` y `GEMINI_API_KEY` mediante variables de entorno del orquestador.
3. **Automatización de Ingesta (ERP / Open Banking):** Conectar `guardar_historico_db` y `guardar_cartera_db` con tareas programadas (Airflow, cron o webhooks) que extraigan saldos bancarios y pólizas contables desde ERPs (SAP, NetSuite, Odoo) sin intervención manual de archivos CSV.