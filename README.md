#  PluriOne | Executive Liquidity & Treasury Intelligence System

> **Estándar Académico & Evaluación:** `G19X-ITZ-VHM-307-ACADEMIC`  
> **Plataforma:** Sistema Predictivo de Flujo de Efectivo, Tesorería y Gestión de Riesgo Financiero.

---

##  1. Visión General & Problema que Resuelve

Las pequeñas y medianas empresas con frecuencia enfrentan problemas de liquidez por falta de visibilidad sobre sus flujos de caja futuros, la falta de integración entre sus cuentas por cobrar/pagar y la incapacidad de simular escenarios de riesgo operativo.

**PluriOne** resuelve esta problemática al concentrar en una suite modular:
* **Predicción de Flujo de Efectivo:** Proyecciones dinámicas ajustadas por estacionalidad semanal y escenarios estratégicos (*Base, Optimista, Conservador*).
* **Integración de Cartera CxC / CxP:** Ajuste automático de flujos según la antigüedad de saldos y vencimientos.
* **Simulación Estocástica Monte Carlo & VaR:** Cuantificación del *Value at Risk* (95% y 99%) y probabilidad estocástica de insolvencia.
* **Métricas de Precisión de Modelo:** Evaluación continua del error predictivo mediante métricas MAE (*Mean Absolute Error*) y MAPE (*Mean Absolute Percentage Error*).
* **Copiloto Financiero con IA:** Consultas ejecutivas asistidas por modelos LLM de Google AI Studio / OpenAI.

---

##  2. Arquitectura del Sistema

El proyecto sigue un patrón de diseño modular limpio donde la interfaz de usuario (`app.py`) orquesta la ejecución, separando la lógica en módulos independientes:

├── app.py                     # Controlador principal y orquestador Streamlit
├── modules/
│   ├── ai_copilot.py          # Asistente CFO con integración LLM (Gemini / OpenAI)
│   ├── auth.py                # Sistema de autenticación con seguridad bcrypt
│   ├── cxc_cxp.py             # Módulo de Cartera, Cuentas por Cobrar y Pagar
│   ├── database.py            # Capa de persistencia SQLite auto-sanable y parametrizada
│   ├── forecasting.py         # Motor predictivo de flujo con integración de cartera
│   ├── reports.py             # Generador de reportes ejecutivos en Excel (openpyxl)
│   ├── risk.py                # Simulación de Monte Carlo y métricas de riesgo VaR
│   ├── styles.py              # Hoja de estilos CSS y temas visuales
│   └── support_agent.py       # Asistente técnico PluriBot
├── data/
│   └── sample_flujo.csv       # Archivo CSV de datos históricos de muestra
├── .env.example               # Plantilla de variables de entorno
├── requirements.txt           # Dependencias del proyecto
└── README.md                  # Documentación del sistema

## 3 Guía de Instalación y Despliegue

Python versión 3.9 o superior.

Gestor de paquetes pip.

Entorno de control de versiones git.

Paso 1: Clonación del Repositorio
Bash
git clone [https://github.com/Valeria-HM/G19X-ITZ-VHM-307-ACADEMIC.git](https://github.com/Valeria-HM/G19X-ITZ-VHM-307-ACADEMIC.git)
cd G19X-ITZ-VHM-307-ACADEMIC

Paso 2: Configuración del Entorno Virtual
En sistemas Windows:

PowerShell
python -m venv venv
venv\Scripts\activate

En sistemas macOS / Linux:

Bash
python3 -m venv venv
source venv/bin/activate

Bash
pip install -r requirements.txt

Paso 4: Configuración de Variables de Entorno
Copie la plantilla de variables de entorno e ingrese los parámetros requeridos:

Bash
cp .env.example .env

Paso 5: Ejecución de la Aplicación
Bash
streamlit run app.py

4. Inicialización y Autenticación de Usuarios

Al iniciar por primera vez, el sistema genera de forma automática la base de datos de almacenamiento SQLite (flujo_efectivo.db) e inicializa la cuenta administradora predeterminada:
Correo de acceso: admin@plurione.com
Contraseña predeterminada: admin123 

(Configurable mediante la variable ADMIN_INITIAL_PASSWORD en el archivo .env)
El sistema utiliza hashing digestivo con algoritmo bcrypt para garantizar el almacenamiento seguro de credenciales.

5. Especificación del Formato de Datos (CSV)
La ingesta de datos de flujo histórico requiere archivos en formato CSV codificados en UTF-8 con la estructura de columnas especificada a continuación:
Columna   Tipo de Dato   Formato     Descripción  
ds        Fecha          YYYY-MM-DD  Fecha correspondiente al registro de caja
Ingresos  Decimal        0.00        Monto total de entradas operacionales
Egresos   Decima         l0.00       Monto total de salidas operacionales
Se incluye un archivo de prueba estandarizado en la ruta data/sample_flujo.csv.

6. Alcance del PRD / MVP y Entregables Garantizados

Módulo de Persistencia: Estructura SQL con consultas totalmente parametrizadas y prevención de inyecciones.Proyección Estratégica: Algoritmo predictivo parametrizable por escenarios y horizontes de 30 a 365 días.
Gestión de Cartera: Control integral de CxC/CxP e impacto directo en la proyección de disponibilidad financiera.Análisis de Riesgo: Motor de simulación estocástica Monte Carlo (1,000 iteraciones) y cálculo de Value at Risk (VaR).
Control de Accesos: Roles diferenciados para perfiles directivos y analistas, con panel CRUD exclusivo para administradores.
Generación de Reportes: Exportación de estados analíticos en formato hojas de cálculo Excel (.xlsx).
