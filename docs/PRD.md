# Product Requirement Document (PRD) | PluriOne

**Sistema Predictivo de Flujo de Efectivo & Tesorería Ejecutiva**  
**Código de Identificación Académica:** `G19X-ITZ-VHM-307-ACADEMIC`  
**Repositorio Oficial:** `Vale131/G19X-ITZ-VHM-307-ACADEMIC`  
**Versión de Producción:** v4.2 (Corte 7 Final) · Noviembre 2026  

---

## 1. Visión y Principios del Producto

> *"Que ninguna decisión de liquidez en PluriOne dependa de la intuición de un analista: que cada decisión de inversión, cobro y pago tenga detrás un copiloto matemático auditable, cuantitativo y transparente."*

El diseño funcional del sistema se rige por tres principios:
1. **Evidencia sobre intuición:** Toda cifra desplegada en el Cockpit proviene de un modelo estadístico estacional o de una consulta auditable en SQLite.
2. **Incertidumbre explícita:** Las proyecciones se acompañan de métricas de error fuera de muestra (**MAE**, **MAPE**, **mejora vs. Baseline**) y cuantificación estocástica de riesgo (**VaR 95%**, **VaR 99%** y **`prob_deficit`**).
3. **Decisión prescriptiva:** La interfaz facilita acciones operativas inmediatas sobre cuentas por cobrar, cuentas por pagar y reservas de liquidez.

---

## 2. Personas y Control de Acceso Basado en Roles (RBAC)

El acceso está regulado mediante un esquema RBAC de tres perfiles en `modules/database.py` y `app.py`:

| Perfil / Rol | Identificador en Sistema | Permisos y Capacidades |
| :--- | :--- | :--- |
| **Director Financiero (CFO)** | `Director Financiero (CFO)` | Acceso total al sistema, exportación de reportes ejecutivos en Excel (`.xlsx`), gestión integral de usuarios (alta, edición, baja y cambio de estatus) y configuración global. |
| **Analista de Tesorería** | `Analista de Tesorería` | Carga de históricos CSV, registro y actualización de cartera operativa (CxC/CxP), selección de escenarios estratégicos y horizontes temporales. |
| **Auditor de Riesgo** | `Auditor de Riesgo` | Consulta ejecutiva de precisión predictiva (MAE/MAPE/Baseline), simulaciones Monte Carlo (VaR 95%, VaR 99%, Probabilidad de Déficit) y diagnóstico prescriptivo. |

---

## 3. Requerimientos Funcionales (RF)

### RF-01: Autenticación y Seguridad de Credenciales
* **Descripción:** Acceso obligatorio mediante correo institucional y contraseña.
* **Especificación:** Almacenamiento exclusivo de hashes generados con `bcrypt` y sal aleatoria (`bcrypt.gensalt()`), sin comparaciones ni respaldos en texto plano.
* **Criterio de Aceptación:** El administrador inicial (`admin@plurione.com`) toma su contraseña de `ADMIN_INITIAL_PASSWORD` en `.env` durante el primer arranque; si la variable no existe, se emite una advertencia sin usar claves hardcodeadas.

### RF-02: Motor Predictivo de Flujo de Caja
* **Descripción:** Proyección diaria de ingresos, egresos, flujo neto y saldo acumulado para horizontes de 30, 60, 90, 180 y 365 días.
* **Especificación:** Estimación basada en estacionalidad por día de la semana modulada por factores de escenario (*Base: 1.00/1.00*, *Optimista: 1.15/0.90*, *Conservador: 0.85/1.10*) y saldo inicial dinámico calculado a partir del histórico acumulado.

### RF-03: Persistencia Directa e Integración de Cartera (CxC / CxP)
* **Descripción:** Gestión relacional de compromisos de cobro y pago en la tabla unificada `cartera` (`id`, `tipo`, `cliente_proveedor`, `monto`, `fecha_vencimiento`, `probabilidad`, `estatus`).
* **Especificación:** Las altas y actualizaciones se ejecutan mediante sentencias SQL directas (`INSERT` y `UPDATE` / `ON CONFLICT(id) DO UPDATE`), preservando los identificadores autoincrementales e integridad referencial sin reescribir tablas completas.
* **Impacto en Pronóstico:** Cada registro activo (`estatus != 'Pagado'` y `!= 'Cancelado'`) impacta su fecha de vencimiento ponderado por su probabilidad de realización ($\text{Monto} \times \text{Probabilidad}$).

### RF-04: Evaluación Holdout y Comparación vs. Baseline
* **Descripción:** Validación temporal del modelo reservando los últimos 14 días históricos como conjunto de prueba (*Holdout*).
* **Especificación:** Cálculo de **MAE**, **MAPE** y porcentaje de mejora frente a un modelo *Baseline* de promedio simple global mediante `calcular_mejora_vs_baseline(df_historico_db)`.

### RF-05: Modelado Estocástico Monte Carlo y VaR Unificado
* **Descripción:** Cuantificación del riesgo de iliquidez mediante 1,000 simulaciones estocásticas perturbadas con la desviación estándar histórica.
* **Especificación:** Exposición unificada de métricas bajo el diccionario `{"var_95", "var_99", "prob_deficit", "saldo_final_esperado"}` consumido de manera consistente por la interfaz de Streamlit y el exportador Excel.

### RF-06: Copiloto Financiero de IA (Opcional)
* **Descripción:** Asistente conversacional financiero en `modules/ai_copilot.py` conectado opcionalmente a **Google AI Studio** (`GEMINI_API_KEY`).
* **Criterio de Aceptación:** Si la llave de Google AI Studio no está configurada, el módulo informa su estado sin interrumpir el funcionamiento del resto de la plataforma.

---

## 4. Requerimientos No Funcionales (RNF)

* **RNF-01 (Cifrado y Prevención de Enumeración):** Hashing obligatorio con `bcrypt` y validación prioritaria de contraseña antes de informar el estatus de la cuenta.
* **RNF-02 (Sanitización y UI Adaptativa):** Escape HTML (`html.escape`) en metadatos de sesión y uso de `width="stretch"` en componentes de Streamlit.
* **RNF-03 (Integridad Transaccional SQLite):** Operaciones atómicas con `commit()` y `rollback()` explícito en `flujo_efectivo.db`, validadas mediante pruebas automatizadas en `pytest`.
* **RNF-04 (Consistencia de Exportación):** Sincronización exacta de claves financieras entre los módulos de cálculo y los libros `.xlsx` generados con `openpyxl`.

---

## 5. Definiciones Matemáticas y Gobernanza de Métricas

| Indicador | Definición Operativa | Implementación |
| :--- | :--- | :--- |
| **MAE** | $\frac{1}{n}\sum_{t=1}^{n} |y_t - \hat{y}_t|$ sobre ventana Holdout de 14 días. | `modules/forecasting.py` |
| **MAPE** | $\frac{100}{n}\sum_{t=1}^{n} \left|\frac{y_t - \hat{y}_t}{\max(|y_t|, 1)}\right|$ | `modules/forecasting.py` |
| **Mejora vs. Baseline** | $\frac{\text{MAE}_{\text{baseline}} - \text{MAE}_{\text{modelo}}}{\text{MAE}_{\text{baseline}}} \times 100$ | `calcular_mejora_vs_baseline` |
| **VaR 95% / VaR 99%** | $\max(0, \mathbb{E}[S_T] - P_{5}(S_T))$ y $\max(0, \mathbb{E}[S_T] - P_{1}(S_T))$ | `modules/risk.py` |
| **`prob_deficit`** | Porcentaje de trayectorias simuladas donde $S_t < 0$ en algún día $t \in [1, T]$. | `modules/risk.py` / `reports.py` |