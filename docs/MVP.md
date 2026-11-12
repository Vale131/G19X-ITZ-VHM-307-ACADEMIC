# Especificación del Producto Mínimo Viable (MVP) | PluriOne

**Sistema Predictivo de Flujo de Efectivo & Tesorería Ejecutiva**  
**Estándar Académico:** `G19X-ITZ-VHM-307-ACADEMIC`  
**Repositorio Oficial:** `Vale131/G19X-ITZ-VHM-307-ACADEMIC`  
**Versión de Producción:** v4.2 · Noviembre 2026  

---

## 1. Alcance del MVP

El Producto Mínimo Viable (MVP) de **PluriOne** entrega una aplicación web operativa en Python y Streamlit capaz de proyectar la liquidez empresarial, integrar compromisos de cuentas por cobrar y por pagar (CxC/CxP) ponderados por probabilidad, cuantificar el riesgo de déficit de caja mediante Monte Carlo (VaR) y generar reportes ejecutivos en Excel.

---

## 2. Objetivos del MVP e Indicadores de Logro

| Código | Objetivo Específico | Mecanismo de Verificación en el Sistema |
| :--- | :--- | :--- |
| **OE-1** | **Pronóstico de Liquidez** | Proyección diaria de 30 a 365 días por estacionalidad semanal y escenarios (*Base*, *Optimista*, *Conservador*), con auto-carga de `data/sample_flujo.csv` si la BD está vacía. |
| **OE-2** | **Validación Holdout & Baseline** | Evaluación automática sobre los últimos 14 días reales desplegando **MAE**, **MAPE** y **% de mejora vs. Baseline** en el Cockpit Financiero. |
| **OE-3** | **Análisis de Riesgo VaR** | Simulación de 1,000 trayectorias Monte Carlo mostrando tarjetas KPI de **VaR 95%**, **VaR 99%** y **Probabilidad de Déficit (`prob_deficit`)**. |
| **OE-4** | **Persistencia Atómica de Cartera** | Gestión de CxC/CxP en SQLite mediante operaciones directas `INSERT` y `UPDATE` (`UPSERT`), conservando IDs reales y ponderando $\text{Monto} \times \text{Probabilidad}$. |
| **OE-5** | **Seguridad & Control RBAC** | Hashing con `bcrypt`, inicialización vía `ADMIN_INITIAL_PASSWORD` en `.env` y administración de usuarios por rol (CFO, Analista, Auditor). |
| **OE-6** | **Exportación Ejecutiva Excel** | Descarga de libro `.xlsx` consolidado con formato monetario/porcentual, pestañas de resumen VaR (`prob_deficit`), proyección, cartera e histórico. |

---

## 3. Arquitectura Modular y Estructura del Repositorio

### 3.1 Estructura de Archivos (Raíz Consolidada)

```text
G19X-ITZ-VHM-307-ACADEMIC/
├── .env.example            # Plantilla de variables (ADMIN_INITIAL_PASSWORD, GEMINI_API_KEY)
├── .gitignore              # Exclusión de entorno virtual, .env y base de datos local
├── README.md               # Guía de instalación, variables de entorno y primer acceso
├── PRD.md                  # Product Requirement Document (Requerimientos y métricas)
├── MVP.md                  # Especificación del Producto Mínimo Viable
├── requirements.txt        # Dependencias del proyecto
├── app.py                  # Orquestador principal Streamlit y vistas ejecutivas
├── modules/                # Módulos desacoplados del núcleo
│   ├── ai_copilot.py       # Copiloto CFO con Google AI Studio (opcional)
│   ├── auth.py             # Autenticación y gestión de sesión
│   ├── cxc_cxp.py          # Interfaz y operaciones directas de cartera CxC/CxP
│   ├── database.py         # Persistencia SQLite (INSERT/UPDATE directos) y bcrypt
│   ├── forecasting.py      # Motor de pronóstico, Holdout MAE/MAPE y Baseline
│   ├── reports.py          # Generador de libros Excel con openpyxl
│   ├── risk.py             # Simulación Monte Carlo (VaR 95%, VaR 99%, prob_deficit)
│   ├── styles.py           # Estilos CSS corporativos y formato de gráficas
│   └── support_agent.py    # Agente de soporte técnico integrado
├── data/                   # Datos históricos iniciales
│   └── sample_flujo.csv
└── tests/                  # Suite de pruebas automatizadas
    └── test_core.py
```

### 3.2 Responsabilidad por Módulo

| Módulo | Responsabilidad Técnica | Dependencias Clave |
| :--- | :--- | :--- |
| `app.py` | Navegación multi-vista, Cockpit ejecutivo, precarga automática de datos y panel de administración de usuarios. | `streamlit`, `plotly`, `html` |
| `modules/database.py` | Esquema SQLite (`usuarios`, `historico_flujo`, `cartera`), hashing `bcrypt` y operaciones SQL directas (`INSERT`/`UPDATE`). | `sqlite3`, `bcrypt`, `pandas` |
| `modules/forecasting.py` | Cálculo de estacionalidad semanal, integración ponderada de cartera, validación Holdout (14d) y comparación vs. Baseline. | `pandas`, `numpy`, `plotly` |
| `modules/cxc_cxp.py` | Alta y actualización de estatus de compromisos CxC/CxP conectada directamente a las funciones atómicas de BD. | `streamlit`, `pandas` |
| `modules/risk.py` | Motor Monte Carlo con semilla reproducible (`seed=42`) y cálculo unificado de `var_95`, `var_99` y `prob_deficit`. | `numpy`, `plotly` |
| `modules/reports.py` | Construcción en memoria de reportes `.xlsx` multi-pestaña con auto-ajuste de columnas y formatos numéricos. | `openpyxl`, `pandas` |
| `modules/ai_copilot.py` | Asistente financiero impulsado opcionalmente por **Google AI Studio** (`GEMINI_API_KEY`). | `google-genai` / `streamlit` |

---

## 4. Matriz de Consolidación Técnica (Corte 7)

1. **Consolidación Documental en Raíz:** Traslado y depuración de `PRD.md` y `MVP.md` a la raíz del repositorio junto con `README.md` actualizado (incluyendo sección de *Primer acceso* y variables de `.env.example`).
2. **Persistencia Directa en Base de Datos:** Sustitución de `if_exists='replace'` por sentencias SQL directas `INSERT` y `UPDATE` (`UPSERT`) en `database.py` y `cxc_cxp.py`, manteniendo la integridad de llaves primarias y alineando el comportamiento con `pytest`.
3. **Unificación de Riesgo VaR (`prob_deficit`):** Estandarización de la clave `prob_deficit` en `modules/risk.py`, las tarjetas KPI de `app.py` y la exportación Excel en `modules/reports.py`.
4. **Limpieza de Llamada Baseline:** Simplificación de `calcular_mejora_vs_baseline(df_historico_db)` eliminando parámetros redundantes en `app.py` y retornando métricas estructuradas.
5. **Seguridad sin Credenciales Hardcodeadas:** Inicialización dinámica de `admin@plurione.com` mediante `ADMIN_INITIAL_PASSWORD` y verificación estricta con `bcrypt`.

---

## 5. Criterios de Aceptación (Go / No-Go)

* **Pruebas Unitarias:** Ejecución limpia de `python -m pytest tests/` sin errores de esquema ni discrepancias de claves.
* **Despliegue de Métricas:** Visualización simultánea en el Cockpit de MAE, MAPE, mejora vs. Baseline, VaR 95%, VaR 99% y Probabilidad de Déficit (`prob_deficit`).
* **Exportación Íntegra:** Descarga funcional del archivo `PluriOne_Reporte_<N>D.xlsx` con todas las hojas formateadas.
* **Experiencia de Primer Acceso:** Arranque inmediato tras configurar `.env`, creación automática del usuario administrador y carga automática de `data/sample_flujo.csv`.