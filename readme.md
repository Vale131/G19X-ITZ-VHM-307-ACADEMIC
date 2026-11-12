# PluriOne — Sistema Predictivo de Flujo de Efectivo y Tesorería

**Estándar Académico:** `G19X-ITZ-VHM-307-ACADEMIC`  
**Repositorio Oficial:** https://github.com/Vale131/G19X-ITZ-VHM-307-ACADEMIC.git  
**Plataforma:** Python 3.10+ | Streamlit | SQLite | Bcrypt | Plotly  

---

## Visión General del Proyecto
PluriOne es una suite modular de inteligencia financiera diseñada para proyectar liquidez a corto y mediano plazo, integrando compromisos operativos (CxC / CxP) ponderados por su probabilidad de cobro/pago y evaluando riesgos estocásticos con simulaciones Monte Carlo (VaR).

---

## Estructura del Repositorio

```text
G19X-ITZ-VHM-307-ACADEMIC/
├── .env.example            # Plantilla de variables de entorno
├── .gitignore              # Exclusión de archivos sensibles
├── README.md               # Documentación principal
├── PRD.md                  # Product Requirement Document
├── MVP.md                  # Especificación del Producto Mínimo Viable
├── requirements.txt        # Dependencias del proyecto
├── app.py                  # Orquestador principal Streamlit
├── modules/                # Módulos del núcleo del sistema
│   ├── ai_copilot.py       # Copiloto financiero con Google AI Studio
│   ├── auth.py             # Control de acceso y autenticación
│   ├── cxc_cxp.py          # Gestión de cartera operativa
│   ├── database.py         # Persistencia relacional SQLite
│   ├── forecasting.py      # Motor de pronóstico y evaluación Baseline
│   ├── reports.py          # Exportación ejecutiva a Excel
│   └── risk.py             # Simulación Monte Carlo y cálculo VaR
├── data/                   # Datos de prueba
│   └── sample_flujo.csv
└── tests/                  # Pruebas unitarias
    └── test_core.py
```

---

## Instalación y Configuración

```bash
# 1. Clonar el repositorio
git clone https://github.com/Vale131/G19X-ITZ-VHM-307-ACADEMIC.git
cd G19X-ITZ-VHM-307-ACADEMIC

# 2. Configurar entorno virtual
python -m venv .venv
# En Windows:
.venv\Scripts\activate
# En macOS/Linux:
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env

# 5. Ejecutar suite de pruebas unitarias
python -m pytest tests/

# 6. Iniciar la aplicación
python -m streamlit run app.py
```

---

## Variables de Entorno (`.env.example`)

Antes de iniciar la aplicación por primera vez, copia `.env.example` a `.env` y configura sus variables:

| Variable | Requerida | Descripción |
| :--- | :---: | :--- |
| **`ADMIN_INITIAL_PASSWORD`** | **Sí** | Define la contraseña inicial para crear la cuenta del administrador principal (`admin@plurione.com`) durante el primer arranque de la aplicación. No existen contraseñas hardcodeadas en el código fuente. |
| **`GEMINI_API_KEY`** | **Opcional** | Llave de API obtenida desde **Google AI Studio** (no utiliza OpenAI), empleada por el copiloto financiero en `modules/ai_copilot.py` (línea 63). Si se deja vacía o no se define, el asistente conversacional mostrará un aviso de configuración, pero todos los módulos financieros, pronósticos, cartera y reportes Excel operarán con normalidad. |

---

## Primer Acceso

1. **Arranque inicial:** Al ejecutar `python -m streamlit run app.py` por primera vez, la función `init_db()` inicializa la base de datos SQLite (`flujo_efectivo.db`) y crea automáticamente la cuenta de administrador utilizando la contraseña definida en `ADMIN_INITIAL_PASSWORD`.
2. **Credenciales de inicio de sesión:**
   * **Correo electrónico:** `admin@plurione.com`
   * **Contraseña:** El valor configurado en `ADMIN_INITIAL_PASSWORD` dentro de tu archivo `.env`.
3. **Carga automática de datos de prueba:** No es necesario cargar ningún archivo manual para explorar el sistema. Si la tabla histórica de flujo está vacía al iniciar sesión, la aplicación ingesta automáticamente `data/sample_flujo.csv` y habilita de inmediato todos los tableros, métricas de precisión y simulaciones VaR.

---

## Formato Requerido para Ingesta CSV

Si deseas reemplazar los datos de prueba con un histórico propio, el archivo CSV debe contener la siguiente estructura:

| Columna | Tipo de Dato | Descripción | Ejemplo |
| :--- | :--- | :--- | :--- |
| **ds** | Fecha (`YYYY-MM-DD`) | Fecha del registro de caja | `2026-01-15` |
| **Ingresos** | Decimal (`100.00`) | Entradas brutas de efectivo | `15000.00` |
| **Egresos** | Decimal (`100.00`) | Salidas brutas de efectivo | `8500.00` |

---

## Seguridad y Autenticación

- **Hashing seguro:** Contraseñas protegidas mediante hash dinámico Bcrypt con generación de sal aleatoria (`gensalt`).
- **Control de Acceso Basado en Roles (RBAC):** Director Financiero (CFO), Analista de Tesorería y Auditor de Riesgo.
- **Credenciales iniciales:** Configuración aislada mediante la variable de entorno `ADMIN_INITIAL_PASSWORD`.

---

## Uso de IA

Se utilizaron asistentes de IA para el diseño de componentes visuales en Streamlit, optimización de consultas SQL parametrizadas y estructuración de pruebas automatizadas con `pytest`. Todos los módulos fueron revisados, probados y adaptados técnicamente. Mayor detalle disponible en `PRD.md`.