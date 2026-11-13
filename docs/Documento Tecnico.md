# Documento Técnico y Arquitectura de Software | PluriOne

**Sistema Predictivo de Flujo de Efectivo y Tesorería Ejecutiva**  
**Identificador de Proyecto:** `G19X-ITZ-VHM-307-ACADEMIC`  
**Repositorio Oficial:** `https://github.com/Vale131/G19X-ITZ-VHM-307-ACADEMIC.git`  
**Versión:** v4.2 Producción  

---

## 1. Stack Tecnológico y Criterios de Selección

La selección tecnológica equilibra velocidad de despliegue, portabilidad multiplataforma y rigor estadístico para modelado financiero:

| Componente | Tecnología / Versión | Justificación Arquitectónica |
| :--- | :--- | :--- |
| **Lenguaje Base** | Python 3.10+ | Estándar de la industria para análisis cuantitativo, manipulación de series temporales y computación matricial. |
| **Interfaz Web** | Streamlit 1.30+ | Permite construir aplicaciones analíticas interactivas directamente en Python (`width="stretch"`), reduciendo la complejidad de mantener servicios frontend/backend separados. |
| **Motor de Persistencia** | SQLite3 (Nativo) | Base de datos relacional transaccional contenida en un único archivo (`flujo_efectivo.db`), portable sin servidores externos y preparada para escalar a PostgreSQL. |
| **Cálculo Numérico** | Pandas y NumPy | Procesamiento vectorizado de series históricas, agrupaciones por estacionalidad semanal y generación matricial de 1,000 trayectorias Monte Carlo. |
| **Visualización** | Plotly 5.x | Gráficos financieros interactivos con inspección puntual (*tooltips*), comparativa de escenarios y distribución de densidad de saldos finales. |
| **Seguridad** | `bcrypt` 4.x y `python-dotenv` | Hashing criptográfico adaptativo con sal aleatoria y aislamiento estricto de secretos mediante variables de entorno. |
| **Exportación Ejecutiva** | OpenPyXL 3.x | Generación en memoria (`io.BytesIO`) de reportes `.xlsx` multi-pestaña con estilos corporativos, formatos numéricos y autoajuste de columnas. |
| **Inteligencia Artificial** | Google AI Studio (`gemini-1.5-flash`) | Conexión opcional a través de endpoint compatible (`https://generativelanguage.googleapis.com/v1beta/openai/`) con respaldo local determinista en `modules/ai_copilot.py`. |

---

## 2. Topología del Repositorio y Flujo de Datos

El código sigue el **Principio de Responsabilidad Única (SRP)**: la persistencia, el cálculo estadístico, la simulación de riesgos, la gestión de cartera y la capa visual residen en módulos independientes.

```text
G19X-ITZ-VHM-307-ACADEMIC/
+-- .env.example                # Plantilla de variables (ADMIN_INITIAL_PASSWORD, GEMINI_API_KEY)
+-- .gitignore                  # Exclusión de entorno virtual, .env y bases de datos locales
+-- README.md                   # Guía principal de instalación, configuración y primer acceso
+-- PRD.md                      # Documento de Requerimientos del Producto (RF / RNF)
+-- MVP.md                      # Especificación del Producto Mínimo Viable
+-- requirements.txt            # Dependencias fijadas del entorno Python
+-- app.py                      # Orquestador principal Streamlit, control RBAC y vistas
+-- data/
|   +-- sample_flujo.csv        # Dataset histórico de referencia con precarga automática
+-- docs/
|   +-- 01_Accesos_de_Prueba.md
|   +-- 02_Bitacora_de_Desarrollo.md
|   +-- 03_Documento_Tecnico.md
|   +-- 05_Guia_de_Instalacion.md
|   +-- 06_Manual_de_Usuario.md
|   +-- 07_Manual_Tecnico.md
+-- modules/
|   +-- ai_copilot.py           # Copiloto financiero CFO (Google AI Studio + respaldo local)
|   +-- auth.py                 # Pantalla de autenticación y control de sesión
|   +-- cxc_cxp.py              # Gestión operativa y CRUD directo de cartera CxC/CxP
|   +-- database.py             # Persistencia relacional SQLite (INSERT/UPDATE) y bcrypt
|   +-- forecasting.py          # Motor predictivo, Holdout MAE/MAPE y cálculo Baseline
|   +-- reports.py              # Exportación de reportes ejecutivos en Excel (.xlsx)
|   +-- risk.py                 # Simulación estocástica Monte Carlo y métricas VaR
|   +-- styles.py               # Estilos CSS corporativos y personalización de gráficas
|   +-- support_agent.py        # Agente de soporte operativo integrado
+-- tests/
    +-- test_core.py            # Suite de 7 pruebas unitarias aisladas con pytest
```

### Arquitectura de Integración entre Módulos

```text
[ .env ] ---> [ database.py ] <---> [ app.py (Orquestador & RBAC) ]
                    |                         |
                    v                         +---> [ cxc_cxp.py ] (CRUD directo CxC/CxP)
           [ historico_flujo ]                |
           [     cartera     ] ---------------+---> [ forecasting.py ] (Estacionalidad + Holdout)
                                              |            |
                                              |            v
                                              +---> [   risk.py   ] (Monte Carlo VaR 95/99)
                                              |            |
                                              |            v
                                              +---> [  reports.py ] (Excel Consolidado .xlsx)
```

---

## 3. Modelo Relacional de Datos (`flujo_efectivo.db`)

La función `init_db()` crea las tablas requeridas y verifica la compatibilidad de columnas mediante `PRAGMA table_info(...)`:

### 3.1. Tabla `usuarios`
* `id` (`INTEGER PRIMARY KEY AUTOINCREMENT`): Identificador único de cuenta.
* `email` (`TEXT UNIQUE NOT NULL`): Correo institucional del usuario.
* `password` (`TEXT NOT NULL`): Hash `bcrypt` codificado en UTF-8.
* `nombre` (`TEXT NOT NULL`): Nombre completo desplegado en interfaz.
* `rol` (`TEXT NOT NULL`): `Director Financiero (CFO)`, `Analista de Tesorería` o `Auditor de Riesgo`.
* `estatus` (`TEXT DEFAULT 'Activo'`): Control de vigencia (`Activo` o `Inactivo`).

### 3.2. Tabla `historico_flujo`
* `id` (`INTEGER PRIMARY KEY AUTOINCREMENT`): Identificador secuencial.
* `ds` (`TEXT NOT NULL`): Fecha del movimiento diario en formato ISO (`YYYY-MM-DD`).
* `Ingresos` (`REAL NOT NULL`): Entradas brutas de efectivo del día.
* `Egresos` (`REAL NOT NULL`): Salidas brutas de efectivo del día.

### 3.3. Tabla `cartera`
* `id` (`INTEGER PRIMARY KEY AUTOINCREMENT`): Identificador único del compromiso operativo.
* `tipo` (`TEXT NOT NULL`): Clasificación de flujo (`CxC` para cobros, `CxP` para pagos).
* `cliente_proveedor` (`TEXT NOT NULL`): Nombre de la contraparte o concepto de factura.
* `monto` (`REAL NOT NULL`): Importe nominal del documento.
* `fecha_vencimiento` (`TEXT NOT NULL`): Fecha esperada de liquidación (`YYYY-MM-DD`).
* `probabilidad` (`REAL DEFAULT 1.0`): Probabilidad estimada de realización en el rango $[0.0, 1.0]$.
* `estatus` (`TEXT DEFAULT 'Pendiente'`): Estado del compromiso (`Pendiente`, `Pagado`, `Cancelado`).

> Las operaciones sobre `cartera` utilizan sentencias SQL directas `INSERT` y `UPDATE` (`ON CONFLICT(id) DO UPDATE`), preservando las llaves primarias y evitando la reconstrucción destructiva de tablas.

---

## 4. Fundamentos Matemáticos y Estadísticos

### 4.1. Proyección Estacional Modulada e Integración de Cartera
Sea $d(t) \in \{0, \dots, 6\}$ el día de la semana correspondiente a la fecha proyectada $t$, y sean $(\alpha_{\text{ing}}, \alpha_{\text{egr}})$ los factores estratégicos del escenario seleccionado:

| Escenario | Multiplicador de Ingresos ($\alpha_{\text{ing}}$) | Multiplicador de Egresos ($\alpha_{\text{egr}}$) |
| :--- | :---: | :---: |
| **Base** | $1.00$ | $1.00$ |
| **Optimista** | $1.15$ | $0.90$ |
| **Conservador** | $0.85$ | $1.10$ |

Los ingresos $I_t$ y egresos $E_t$ proyectados para cada día $t \in \{1, \dots, T\}$ combinan la media estacional histórica con los compromisos activos (`estatus != 'Pagado'` y `!= 'Cancelado'`) cuya fecha de vencimiento coincide con $t$:

$$I_t = \bar{I}_{d(t)} \cdot \alpha_{\text{ing}} + \sum_{i \in \text{CxC}(t)} \left( M_i \cdot p_i \right)$$

$$E_t = \bar{E}_{d(t)} \cdot \alpha_{\text{egr}} + \sum_{j \in \text{CxP}(t)} \left( M_j \cdot p_j \right)$$

El flujo neto diario $FN_t$ y el saldo acumulado $S_t$ a partir del saldo inicial dinámico $S_0$ se calculan como:

$$FN_t = I_t - E_t, \qquad S_t = S_0 + \sum_{k=1}^{t} FN_k$$

### 4.2. Validación Holdout y Comparación contra Baseline
Para auditar la capacidad predictiva sin fuga de datos (*data leakage*), el motor reserva los últimos $H = 14$ días históricos como ventana de prueba y evalúa el **Error Absoluto Medio (MAE)** y el **Error Porcentual Absoluto Medio (MAPE)**:

$$\text{MAE} = \frac{1}{H} \sum_{t=1}^{H} \left| y_t - \hat{y}_t \right|, \qquad \text{MAPE} = \frac{100}{H} \sum_{t=1}^{H} \left| \frac{y_t - \hat{y}_t}{\max(|y_t|, 1)} \right|$$

Asimismo, se mide la reducción porcentual de error frente a un modelo *Baseline* de promedio simple global del flujo neto ($\bar{y}_{\text{train}}$):

$$\text{Mejora vs. Baseline (\%)} = \left( \frac{\text{MAE}_{\text{baseline}} - \text{MAE}_{\text{modelo}}}{\text{MAE}_{\text{baseline}}} \right) \times 100$$

### 4.3. Simulación Estocástica de Monte Carlo y Value at Risk (VaR)
A partir de la desviación estándar $\sigma$ del flujo neto proyectado, `modules/risk.py` genera $N = 1,000$ trayectorias estocásticas reproducibles (`np.random.seed(42)`):

$$FN_t^{(m)} = FN_t + \epsilon_t^{(m)}, \qquad \epsilon_t^{(m)} \sim \mathcal{N}(0, \sigma^2), \qquad m = 1, \dots, N$$

Sobre la distribución empírica de saldos finales $S_T^{(m)} = S_0 + \sum_{t=1}^{T} FN_t^{(m)}$, se extraen el saldo final esperado $\mathbb{E}[S_T]$, los percentiles $P_5$ y $P_1$, y la probabilidad de déficit intrahorizonte (`prob_deficit`):

$$\text{VaR}_{95\%} = \max\left(0, \; \mathbb{E}[S_T] - P_5(S_T)\right), \qquad \text{VaR}_{99\%} = \max\left(0, \; \mathbb{E}[S_T] - P_1(S_T)\right)$$

$$\text{prob\_deficit} = \frac{100}{N} \sum_{m=1}^{N} \mathbb{I}\left( \min_{1 \le t \le T} S_t^{(m)} < 0 \right)$$

> **Supuestos del modelo estocástico:** Las perturbaciones diarias siguen una distribución normal independiente con varianza constante $\sigma^2$ estimada a partir de la serie proyectada, y la probabilidad de déficit evalúa si la trayectoria cae por debajo de $\$0.00$ en cualquier día $t$ del horizonte seleccionado.