# Bitácora de Desarrollo y Control de Versiones | PluriOne

**Sistema Predictivo de Flujo de Efectivo y Tesorería Ejecutiva**  
**Identificador de Proyecto:** `G19X-ITZ-VHM-307-ACADEMIC`  
**Repositorio Oficial:** `https://github.com/Vale131/G19X-ITZ-VHM-307-ACADEMIC.git`  
**Versión:** v4.2 Producción  

---

## 1. Metodología de Construcción Iterativa

El desarrollo de **PluriOne** se estructuró bajo un enfoque iterativo e incremental. Cada ciclo produjo un incremento funcional verificable de extremo a extremo, permitiendo validar la integridad matemática y operativa antes de incorporar nuevas capas de complejidad:

1. **Trazabilidad Arquitectónica:** Cada iteración responde directamente a los requerimientos funcionales (`RF-01` a `RF-06`) y no funcionales (`RNF-01` a `RNF-04`) especificados en `PRD.md`.
2. **Desacoplamiento Modular:** La separación estricta entre persistencia (`database.py`), pronóstico (`forecasting.py`), riesgo estocástico (`risk.py`), cartera (`cxc_cxp.py`), reportes (`reports.py`) y presentación (`app.py`) permite evolucionar algoritmos sin comprometer la estabilidad de la interfaz.
3. **Verificación Automatizada:** Las reglas críticas de seguridad, persistencia transaccional, ponderación de cartera y simulación de riesgo están cubiertas por pruebas unitarias aisladas en `tests/test_core.py`.

---

## 2. Evolución Cronológica por Versiones

| Versión | Módulos Involucrados | Entregable Técnico | Justificación de Ingeniería y Negocio |
| :--- | :--- | :--- | :--- |
| **v1.0** | Estructura base, `README.md`, `requirements.txt` | Inicialización del repositorio, definición de dependencias y entorno virtual aislado. | Garantizar reproducibilidad multiplataforma desde el inicio del ciclo de vida. |
| **v2.0** | `modules/database.py` | Diseño del esquema relacional SQLite (`usuarios`, `historico_flujo`, `cartera`) y rutinas de inicialización `init_db()`. | Establecer persistencia transaccional en disco (`flujo_efectivo.db`), superando las limitaciones de almacenamiento volátil en memoria. |
| **v3.0** | `modules/forecasting.py` | Motor predictivo por estacionalidad semanal, multiplicadores de escenario y validación fuera de muestra (*Holdout* 14 días) con **MAE**, **MAPE** y **mejora vs. Baseline**. | Transformar series históricas en proyecciones de liquidez auditables y demostrar cuantitativamente la ganancia de precisión frente a un promedio global simple. |
| **v4.0** | `modules/cxc_cxp.py`, `modules/forecasting.py` | Integración de cuentas por cobrar (CxC) y por pagar (CxP) ponderadas por su probabilidad de realización ($\text{Monto} \times \text{Probabilidad}$). | Incorporar compromisos operativos futuros en sus fechas exactas de vencimiento para reflejar la liquidez real comprometida. |
| **v4.1** | `modules/risk.py`, `modules/auth.py`, `.env.example` | Simulación Monte Carlo de 1,000 trayectorias (**VaR 95%**, **VaR 99%**, **`prob_deficit`**), hashing `bcrypt` con sal aleatoria y RBAC de tres perfiles. | Cuantificar la exposición ante volatilidad de caja y blindar el acceso a información financiera sin credenciales en código fuente (`RNF-01`). |
| **v4.2** | `app.py`, `database.py`, `cxc_cxp.py`, `reports.py`, `ai_copilot.py`, `tests/` | Persistencia atómica SQL (`INSERT` / `ON CONFLICT(id) DO UPDATE`), unificación de `prob_deficit` en interfaz y Excel, integración opcional de Google AI Studio (`GEMINI_API_KEY`), auto-carga de `data/sample_flujo.csv` y suite de 7 pruebas en `pytest`. | Eliminar reescrituras destructivas de tablas, garantizar consistencia exacta entre los indicadores del Cockpit y los reportes `.xlsx`, y asegurar cobertura completa de pruebas automatizadas. |

---

## 3. Estándar de Control de Versiones

El historial de cambios en la rama `main` sigue la convención **Conventional Commits** para mantener una bitácora auditable:

* `feat(...)`: Incorporación de nuevas capacidades funcionales (ej. `feat(risk): implementar simulacion Monte Carlo y calculo VaR 95/99`).
* `refactor(...)`: Reestructuración interna orientada a mantenibilidad, atomicidad SQL o limpieza de firmas sin alterar contratos externos.
* `fix(...)`: Resolución de incidencias o estandarización de claves entre módulos (ej. `fix(ia): estandarizar GEMINI_API_KEY de Google AI Studio en ai_copilot y .env.example`).
* `test(...)`: Incorporación y actualización de pruebas unitarias aisladas en `tests/test_core.py`.
* `docs(...)`: Actualización de `README.md`, `PRD.md`, `MVP.md` y la documentación técnica en `docs/`.

---

## 4. Hitos de Consolidación de la Versión de Producción (v4.2)

1. **Persistencia Atómica en Base de Datos:** Sustitución de reemplazos completos de tabla por sentencias SQL parametrizadas `INSERT` y `UPDATE` (`UPSERT`), preservando las llaves primarias autoincrementales en `cartera` y asegurando transacciones limpias con `commit()` y `rollback()`.
2. **Contrato Unificado de Métricas de Riesgo:** Estandarización de la clave `prob_deficit` entre `modules/risk.py`, las tarjetas KPI de `app.py` y el libro Excel generado por `modules/reports.py`.
3. **Optimización del Benchmarking Baseline:** Simplificación de `calcular_mejora_vs_baseline(df_hist)` para evaluar directamente la reducción porcentual de MAE del modelo estacional frente a la media global simple, retornando un valor flotante compatible tanto con el Cockpit como con `pytest`.
4. **Copiloto Financiero Desacoplado:** Integración opcional con Google AI Studio (`GEMINI_API_KEY`) mediante el modelo `gemini-1.5-flash` y respaldo automático mediante motor de diagnóstico local cuando no se configura llave de API.
5. **Experiencia de Primer Arranque:** Carga automática del dataset de referencia `data/sample_flujo.csv` cuando la tabla `historico_flujo` se encuentra vacía al iniciar sesión.