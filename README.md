# PluriOne — Sistema Predictivo de Flujo de Efectivo y Tesorería

**Estándar Académico:** `G19X-ITZ-VHM-307-ACADEMIC`  
**Repositorio Oficial:** `https://github.com/Vale131/G19X-ITZ-VHM-307-ACADEMIC`  
**Plataforma:** Python 3.10+ | Streamlit | SQLite | Bcrypt | Plotly  

---

##  Visión General del Proyecto
PluriOne es una suite modular de inteligencia financiera diseñada para proyectar liquidez a corto y mediano plazo, integrando compromisos operativos (CxC / CxP) ponderados por su probabilidad de cobro/pago y evaluando riesgos estocásticos con simulaciones Monte Carlo (VaR).

---

##  Estructura del Repositorio

```text
G19X-ITZ-VHM-307-ACADEMIC/
├── .env.example            # Plantilla de variables de entorno sin secretos
├── .gitignore              # Exclusión de archivos sensibles
├── README.md               # Documentación principal
├── requirements.txt        # Dependencias del proyecto (incluye pytest)
├── app.py                  # Orquestador principal Streamlit
├── docs/                   # Documentación técnica
│   ├── PRD.md              # Product Requirement Document
│   └── MVP.md              # Especificación del Producto Mínimo Viable
├── modules/                # Módulos del núcleo del sistema
│   ├── ai_copilot.py
│   ├── auth.py
│   ├── cxc_cxp.py
│   ├── database.py
│   ├── forecasting.py
│   ├── reports.py
│   ├── risk.py
│   ├── styles.py
│   └── support_agent.py
├── data/                   # Datos de prueba
│   └── sample_flujo.csv
└── tests/                  # Pruebas unitarias
    └── test_core.py

Instalación y Configuración
Clonar el repositorio oficial:

Bash
git clone [https://github.com/Vale131/G19X-ITZ-VHM-307-ACADEMIC.git](https://github.com/Vale131/G19X-ITZ-VHM-307-ACADEMIC.git)
cd G19X-ITZ-VHM-307-ACADEMIC
Crear y activar entorno virtual:

Bash
python -m venv .venv
# En Windows:
.venv\Scripts\activate
# En macOS/Linux:
source .venv/bin/activate
Instalar dependencias del proyecto:

Bash
pip install -r requirements.txt
Configurar variables de entorno (.env):
Copia .env.example a .env y asigna la contraseña inicial del administrador:

Bash
cp .env.example .env
Dentro de tu archivo .env:

Fragmento de código
ADMIN_INITIAL_PASSWORD=TuPasswordSeguro123
OPENAI_API_KEY=tu-api-key-de-openai
Ejecutar suite de pruebas unitarias (pytest):

Bash
python -m pytest tests/
Iniciar la aplicación:

Bash
python -m streamlit run app.py


Columna,Tipo de Dato,Descripción,Ejemplo
ds,Fecha (YYYY-MM-DD),Fecha del registro de caja,2026-01-15
Ingresos,Decimal (100.00),Entradas brutas de efectivo,15000.00
Egresos,Decimal (100.00),Salidas brutas de efectivo,8500.00

