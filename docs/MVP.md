# Especificación del Producto Mínimo Viable (MVP) | PluriOne

**Sistema Predictivo de Flujo de Efectivo & Tesorería Ejecutiva**  
**Estándar Académico:** `G19X-ITZ-VHM-307-ACADEMIC`  
**Repositorio Oficial:** `Vale131/G19X-ITZ-VHM-307-ACADEMIC`  
**Versión de Producción:** v3.2 / v4.2 Actualizada · Octubre 2026  

---

## 1. Resumen Ejecutivo y Alcance del Sistema

El presente documento detalla la especificación técnica y de negocio del Producto Mínimo Viable (MVP) para el Sistema Predictivo de Flujo de Efectivo PluriOne, desarrollado bajo la clave académica `G19X-ITZ-VHM-307-ACADEMIC` y alojado en el repositorio GitHub `Vale131/G19X-ITZ-VHM-307-ACADEMIC`.

El MVP resuelve la incertidumbre en la liquidez de caja mediante una arquitectura modular en Python y Streamlit, combinando la proyección estacional de transacciones, la integración probabilística de la cartera de Cuentas por Cobrar y Pagar (CxC/CxP), la cuantificación del riesgo mediante Monte Carlo (VaR) y la asistencia ejecutiva con Inteligencia Artificial.

---

## 2. Objetivos del MVP e Indicadores de Logro

Cada objetivo específico se respalda con un mecanismo de verificación directo en el código y en la interfaz:

| Código | Objetivo Específico | Indicador de Logro y Mecanismo de Verificación |
| :--- | :--- | :--- |
| **OE-1** | **Pronóstico de Liquidez** | Proyección de flujo neto a horizontes de 30 a 365 días combinando promedios por día de la semana y factores de escenario (Base, Optimista, Conservador). |
| **OE-2** | **Validación Cuantitativa** | Autoevaluación del modelo mediante técnica Holdout sobre los últimos 14 días históricos, calculando MAE y MAPE en tiempo real. |
| **OE-3** | **Análisis de Riesgo VaR** | Ejecución de 1,000 iteraciones estocásticas basadas en la volatilidad histórica, presentando en pantalla las tarjetas KPI de VaR 95%, VaR 99% y Probabilidad de Déficit (%). |
| **OE-4** | **Integración de Cartera** | Esquema relacional unificado en `cartera` (`id`, `tipo`, `cliente_proveedor`, `monto`, `fecha_vencimiento`, `probabilidad`, `estatus`), donde cada compromiso altera la proyección multiplicando monto por probabilidad. |
| **OE-5** | **Seguridad & RBAC** | Cifrado estricto con `bcrypt`, inicialización dinámica desde `ADMIN_INITIAL_PASSWORD` en `.env` sin claves hardcodeadas, y panel RBAC (CFO, Analista, Auditor). |
| **OE-6** | **Exportación de Reportes** | Descarga consolidada de datos e indicadores a Excel (`.xlsx`) mediante `openpyxl` usando la clave corregida `prob_deficit`. |

---

## 3. Arquitectura de la Solución (Estructura de Módulos)

El sistema está construido de forma modular para garantizar desacoplamiento y mantenibilidad:

| Módulo / Archivo | Responsabilidad Principal | Tecnologías & Componentes |
| :--- | :--- | :--- |
| `app.py` | Orquestador de interfaz, barra lateral, navegación multi-vista y panel de gestión de usuarios con buscador y edición de roles. | Streamlit (`width='stretch'`), Plotly |
| `modules/database.py` | Gestión relacional SQLite (`flujo_efectivo.db`), esquemas unificados, cifrado `bcrypt` y lectura de `.env`. | SQLite3, `bcrypt`, `os`, `python-dotenv` |
| `modules/forecasting.py` | Pronóstico por día de la semana, factores por escenario, Holdout 14d (MAE/MAPE), baseline y ponderación CxC/CxP. | Pandas, NumPy, Plotly |
| `modules/cxc_cxp.py` | Gestión de cartera de cobros y pagos, alta de registros y actualización interactiva de estatus. | Streamlit, Pandas, Database |
| `modules/risk.py` | Motor de simulación Monte Carlo (1,000 iteraciones), cálculo de VaR 95%, VaR 99% y Probabilidad de Déficit. | NumPy, Plotly Graph Objects |
| `modules/reports.py` | Generación de libro Excel profesional con pestañas de histórico, proyección, cartera y métricas VaR. | `openpyxl`, Pandas |
| `modules/auth.py` | Pantalla de login ejecutiva con diseño borgoña, verificación de hash `bcrypt` y control de sesiones. | Streamlit, `bcrypt` |
| `modules/ai_copilot.py` & `support_agent.py` | Asistentes de Inteligencia Artificial (Copiloto CFO y PluriBot) con renderizado seguro sin inyección HTML. | Streamlit, OpenAI API |

---

## 4. Matriz de Cobertura y Cumplimiento de Retroalimentación

A continuación se resume la alineación del código respecto a la evaluación académica:

1. **Unificación de Cartera:** Esquema unificado en `database.py`, `cxc_cxp.py` y `forecasting.py`. Cada factura de cobro/pago se multiplica por su probabilidad antes de impactar el flujo.
2. **Documentación en Raíz:** `README.md` posicionado en la raíz con URL oficial `Vale131`, bloques de comandos formateados y corrección de tabla.
3. **Documento PRD / MVP:** Creación formal de `docs/PRD.md` y `docs/MVP.md` con la especificación completa del producto.
4. **Hardening de Seguridad:** Eliminada comparación en texto plano y fallback `"admin123"`. Se requiere `ADMIN_INITIAL_PASSWORD` en `.env`.
5. **Tarjetas VaR & Excel:** Despliegue de tarjetas KPI en pantalla (VaR 95%, VaR 99%, % Déficit) y corrección de clave `prob_deficit` en Excel.
6. **Cadencia de Versionado:** Commits descriptivos frecuentes en la rama `main` del repositorio remoto.

---

## 5. Rigor Matemático, Riesgo & Criterios de Aceptación (Go/No-Go)

### 5.1 Protocolo Holdout y Baseline
El sistema realiza una validación temporal reservando los últimos 14 días históricos. Muestra en el Cockpit Financiero las métricas **MAE** (Error Absoluto Medio) y **MAPE** (Error Porcentual Absoluto Medio), permitiendo auditar continuamente la precisión del modelo estacional.

### 5.2 Simulación Monte Carlo y VaR
A través del módulo `modules/risk.py`, el sistema ejecuta 1,000 iteraciones perturbando la proyección con la varianza histórica real para extraer:
* **VaR 95%:** Máxima pérdida esperada con 95% de confianza.
* **VaR 99%:** Saldo de caja extremo para calibración de la reserva de emergencia.
* **Probabilidad de Déficit:** Porcentaje de trayectorias con saldo menor a $0.00.

### 5.3 Criterios de Lanzamiento
* Puntuación Holdout (MAE/MAPE) visible en el Cockpit Financiero.
* Simulación Monte Carlo ejecutable en menos de 3 segundos reportando VaR 95%, VaR 99% y Probabilidad de Déficit.
* Actualización de sintaxis de interfaz Streamlit a `width="stretch"` eliminando advertencias en consola.
* Autenticación robusta probada con hash `bcrypt` sin fugas de información ni accesos no autorizados.