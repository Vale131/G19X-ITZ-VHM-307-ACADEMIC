# Especificación del Producto Mínimo Viable (MVP) | PluriOne

**Sistema Predictivo de Flujo de Efectivo & Tesorería Ejecutiva**  
**Identificador de Proyecto:** `G19X-ITZ-VHM-307-ACADEMIC`  
**Repositorio Oficial:** `https://github.com/Vale131/G19X-ITZ-VHM-307-ACADEMIC.git`  
**Versión:** v4.2 Producción  

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

### 3.1 Estructura de Archivos

```text
G19X-ITZ-VHM-307-ACADEMIC/
+-- .env.example            # Plantilla de variables (ADMIN_INITIAL_PASSWORD, GEMINI_API_KEY)
+-- .gitignore              # Exclusión de entorno virtual, .env y base de datos local
+-- README.md               # Guía de instalación, variables de entorno y primer acceso
+-- PRD.md                  # Product Requirement Document (Requerimientos y métricas)
+-- MVP.md                  # Especificación del Producto Mínimo Viable
+-- requirements.txt        # Dependencias del proyecto
+-- app.py                  # Orquestador principal Streamlit y vistas ejecutivas
+-- docs/                   # Manuales técnicos y operativos en Markdown
|   +-- 01_Accesos_de_Prueba.md
|   +-- 02_Bitacora_de_Desarrollo.md
|   +-- 03_Documento_Tecnico.md
|   +-- 05_Guia_de_Instalacion.md
|   +-- 06_Manual_de_Usuario.md
|   +-- 07_Manual_Tecnico.md
+-- modules/                # Módulos desacoplados del núcleo
|   +-- ai_copilot.py       # Copiloto CFO con Google AI Studio (opcional)
|   +-- auth.py             # Autenticación y gestión de sesión
|   +-- cxc_cxp.py          # Interfaz y operaciones directas de cartera CxC/CxP
|   +-- database.py         # Persistencia SQLite (INSERT/UPDATE directos) y bcrypt
|   +-- forecasting.py      # Motor de pronóstico, Holdout MAE/MAPE y Baseline
|   +-- reports.py          # Generador de libros Excel con openpyxl
|   +-- risk.py             # Simulación Monte Carlo (VaR 95%, VaR 99%, prob_deficit)
|   +-- styles.py           # Estilos CSS corporativos y formato de gráficas
|   +-- support_agent.py    # Agente de soporte técnico integrado
+-- data/                   # Datos históricos iniciales
|   +-- sample_flujo.csv
+-- tests/                  # Suite de pruebas automatizadas
    +-- test_core.py
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
| `modules/ai_copilot.py` | Asistente financiero impulsado opcionalmente por **Google AI Studio** (`GEMINI_API_KEY`). | `openai` (endpoint Google), `streamlit` |

---

## 4. Criterios de Aceptación (Go / No-Go)

* **Pruebas Unitarias:** Ejecución limpia de `python -m pytest tests/` (`7 passed`) sin errores de esquema ni discrepancias de claves.
* **Despliegue de Métricas:** Visualización simultánea en el Cockpit de MAE, MAPE, mejora vs. Baseline, VaR 95%, VaR 99% y Probabilidad de Déficit (`prob_deficit`).
* **Exportación Íntegra:** Descarga funcional del archivo `PluriOne_Reporte_<N>D.xlsx` con todas las hojas formateadas.
* **Experiencia de Primer Acceso:** Arranque inmediato tras configurar `.env`, creación automática del usuario administrador y carga automática de `data/sample_flujo.csv`.