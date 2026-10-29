# PluriOne — Sistema Predictivo de Flujo de Efectivo y Tesorería

**Estándar Académico:** `G19X-ITZ-VHM-307-ACADEMIC`  
**Repositorio Oficial:** `https://github.com/Vale131/G19X-ITZ-VHM-307-ACADEMIC.git`  
**Plataforma:** Python 3.10+ | Streamlit | SQLite | Bcrypt | Plotly  

---

## 📋 Visión General del Proyecto
PluriOne es una suite modular de inteligencia financiera diseñada para proyectar liquidez a corto y mediano plazo, integrando compromisos operativos (CxC / CxP) ponderados por su probabilidad de cobro/pago y evaluando riesgos estocásticos con simulaciones Monte Carlo (VaR).

---

## 📁 Estructura del Repositorio

```text
G19X-ITZ-VHM-307-ACADEMIC/
├── .env.example            # Plantilla de variables de entorno
├── .gitignore              # Exclusión de archivos sensibles
├── README.md               # Documentación principal
├── requirements.txt        # Dependencias del proyecto
├── app.py                  # Orquestador principal Streamlit
├── docs/                   # Documentación técnica
│   ├── PRD.md              # Product Requirement Document
│   └── MVP.md              # Especificación del Producto Mínimo Viable
├── modules/                # Módulos del núcleo del sistema
│   ├── cxc_cxp.py
│   ├── database.py
│   ├── forecasting.py
│   ├── reports.py
│   └── risk.py
├── data/                   # Datos de prueba
│   └── sample_flujo.csv
└── tests/                  # Pruebas unitarias
    └── test_core.py
```

---

## 🚀 Instalación y Configuración

```bash
# 1. Clonar el repositorio
git clone [https://github.com/Vale131/G19X-ITZ-VHM-307-ACADEMIC.git](https://github.com/Vale131/G19X-ITZ-VHM-307-ACADEMIC.git)
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

## 📊 Formato Requerido para Ingesta CSV

El archivo de histórico bancario debe contener la siguiente estructura:

| Columna | Tipo de Dato | Descripción | Ejemplo |
| :--- | :--- | :--- | :--- |
| `ds` | Fecha (`YYYY-MM-DD`) | Fecha del registro de caja | `2026-01-15` |
| `Ingresos` | Decimal (`100.00`) | Entradas brutas de efectivo | `15000.00` |
| `Egresos` | Decimal (`100.00`) | Salidas brutas de efectivo | `8500.00` |

---

## 🛡️ Seguridad y Autenticación
* Contraseñas protegidas mediante hash dinámico **Bcrypt** con generación de sal aleatoria (`gensalt`).
* Control de Acceso Basado en Roles (RBAC): *Director Financiero (CFO)*, *Analista de Tesorería* y *Auditor de Riesgo*.
* Configuración de credenciales de acceso inicial vía variable de entorno `ADMIN_INITIAL_PASSWORD`.