# Manual de Usuario Operativo | PluriOne

**Sistema Predictivo de Flujo de Efectivo y Tesorería Ejecutiva**  
**Identificador de Proyecto:** `G19X-ITZ-VHM-307-ACADEMIC`  
**Repositorio Oficial:** `https://github.com/Vale131/G19X-ITZ-VHM-307-ACADEMIC.git`  
**Versión:** v4.2 Producción  

---

## 1. Propósito y Alcance del Manual

Este manual constituye la guía oficial de operación para los equipos de **Tesorería**, **Dirección Financiera** y **Auditoría Interna** que utilizan **PluriOne**. Su objetivo es estandarizar los flujos de trabajo diarios, la calibración de escenarios estratégicos, la administración de cuentas por cobrar y por pagar (CxC / CxP), la interpretación de métricas estadísticas de error y riesgo, y la generación de reportes ejecutivos.

### 1.1. Flujo Operativo Integral de la Plataforma
PluriOne articula cuatro etapas continuas para convertir registros transaccionales en decisiones de liquidez:

1. **Ingesta Histórica:** Consolidación de entradas y salidas diarias de efectivo (`ds`, `Ingresos`, `Egresos`).
2. **Integración de Compromisos Futuros:** Registro de cuentas por cobrar y por pagar ponderadas por su probabilidad real de liquidación.
3. **Modelado Predictivo y Estrés Estocástico:** Proyección diaria modulada por escenarios estratégicos, auditada mediante validación Holdout de 14 días y sometida a 1,000 simulaciones Monte Carlo.
4. **Acción Ejecutiva y Reporteo:** Exportación de libros `.xlsx` formateados y consulta asistida con el Copiloto CFO.

---

## 2. Acceso al Sistema y Seguridad de Sesión

### 2.1. Inicio de Sesión
1. Abre tu navegador web e ingresa a la dirección del servidor (`http://localhost:8501` en despliegue local).
2. En la pantalla de autenticación institucional, captura tu **Correo Electrónico** corporativo y tu **Contraseña**.
3. Haz clic en **Iniciar Sesión**.

### 2.2. Control de Sesión y Cierre Seguro
* Una vez autenticado, la tarjeta superior de la barra lateral izquierda despliega tu **Nombre Completo** y tu **Rol Asignado** (`Director Financiero (CFO)`, `Analista de Tesorería` o `Auditor de Riesgo`).
* Al concluir tu jornada o abandonar tu estación de trabajo, pulsa el botón **Cerrar Sesión** ubicado al final de la barra lateral para invalidar la sesión activa en memoria.

---

## 3. Anatomía de la Interfaz y Controles Globales

La pantalla se divide en dos áreas: el **Panel Lateral de Navegación y Parámetros** (izquierda) y el **Área Analítica Principal** (derecha). Cualquier cambio en los controles globales recalcula automáticamente las gráficas, los indicadores KPI, la simulación Monte Carlo y el reporte Excel descargable.

### 3.1. Menú de Navegación por Módulos
* **Cockpit Financiero:** Tablero ejecutivo de mando con indicadores clave de desempeño, auditoría estadística del modelo predictivo y herramienta de carga de archivos CSV.
* **Saldos & Tesorería:** Visualización de la trayectoria acumulada de efectivo para detectar valles de liquidez o excedentes invertibles.
* **Capital de Trabajo & Cartera:** Administración operativa de Cuentas por Cobrar (CxC) y Cuentas por Pagar (CxP).
* **Modelado Estocástico & VaR:** Análisis de incertidumbre mediante simulación Monte Carlo, Value at Risk y probabilidad de déficit.
* **Centro de Inteligencia & IA:** Copiloto financiero CFO y asistente de soporte operativo sobre el uso de la plataforma.
* **Gestión de Usuarios:** Módulo administrativo visible exclusivamente para el perfil **Director Financiero (CFO)**.

### 3.2. Panel de Configuración de Simulación
* **Escenario de Estrategia:** Permite evaluar la sensibilidad de la caja ante tres contextos de negocio:

| Escenario | Ajuste sobre Ingresos Históricos | Ajuste sobre Egresos Históricos | Uso Recomendado |
| :--- | :---: | :---: | :--- |
| **Base** | $1.00 \times$ ($0\%$) | $1.00 \times$ ($0\%$) | Planeación ordinaria y presupuesto maestro sin desviaciones extraordinarias. |
| **Optimista** | $1.15 \times$ ($+15\%$) | $0.90 \times$ ($-10\%$) | Evaluación de capacidad de inversión ante campañas comerciales exitosas o programas de ahorro. |
| **Conservador** | $0.85 \times$ ($-15\%$) | $1.10 \times$ ($+10\%$) | Pruebas de resistencia (*stress testing*) ante caídas de demanda o inflación de insumos. |

* **Horizonte Temporal:** Selector desplegable para proyectar **30, 60, 90, 180 o 365 días** hacia adelante a partir de la última fecha registrada en el histórico.
* **Exportar Reporte Excel:** Botón de descarga directa que compila toda la información vigente en el archivo `PluriOne_Reporte_<N>D.xlsx`.

---

## 4. Guía Operativa Detallada por Módulo

### 4.1. Cockpit Financiero

#### A. Tarjetas Ejecutivas de Desempeño (KPIs)
En la franja superior se presentan cuatro indicadores calculados sobre el horizonte y escenario activos:
1. **Total Revenue (Ingresos Proyectados):** Suma acumulada de entradas estacionales esperadas más las Cuentas por Cobrar ponderadas dentro del horizonte.
2. **Net Cash Flow (Flujo Neto):** Diferencia total entre ingresos proyectados y egresos proyectados ($\sum I_t - \sum E_t$). Un valor negativo advierte consumo neto de reservas de caja.
3. **Operating Margin (Margen Operativo):** Proporción porcentual del flujo neto respecto a los ingresos totales proyectados.
4. **Closing Balance (Saldo Final Proyectado):** Disponibilidad estimada de efectivo al cierre del último día del horizonte, partiendo del saldo inicial dinámico acumulado.

#### B. Panel de Auditoría del Modelo Predictivo
Debajo de los KPIs principales, el sistema audita automáticamente la precisión del motor estadístico reservando los últimos **14 días reales** como ventana de validación fuera de muestra (*Holdout*):
* **MAE (Holdout):** Error Absoluto Medio expresado en unidades monetarias. Indica cuánto se desvía en promedio el pronóstico diario respecto al flujo real observado.
* **MAPE (Error %):** Error Porcentual Absoluto Medio. Permite comparar la precisión relativa independientemente de la escala monetaria de la empresa.
* **vs. Baseline:** Porcentaje de reducción de error que logra el modelo estacional frente a un pronóstico tradicional basado en el promedio simple global. Valores positivos confirman que capturar el patrón por día de la semana aporta mayor exactitud.

#### C. Sincronización de Históricos Bancarios (CSV)
1. Despliega el contenedor **Sincronizar Archivo Histórico de Flujo (CSV)**.
2. Selecciona un archivo `.csv` codificado en UTF-8 que contenga exactamente las siguientes columnas:

| Columna | Formato | Descripción y Reglas de Validación |
| :--- | :--- | :--- |
| `ds` | `YYYY-MM-DD` | Fecha calendario del cierre diario (ejemplo: `2026-10-15`). |
| `Ingresos` | Numérico (`float`) | Total de cobranzas y entradas de efectivo del día sin símbolos de moneda ni comas de miles. |
| `Egresos` | Numérico (`float`) | Total de pagos a proveedores, nómina y gastos operativos del día sin símbolos de moneda. |

3. Al cargar un archivo válido, el sistema actualiza la tabla `historico_flujo` en SQLite y recalcula de inmediato el saldo inicial dinámico, las medias por día de la semana y las métricas Holdout.

> **Precarga automática inicial:** Cuando se inicia sesión con una base de datos nueva donde `historico_flujo` está vacía, PluriOne ingesta automáticamente el conjunto de referencia `data/sample_flujo.csv` para que los tableros operen desde el primer segundo.

---

### 4.2. Saldos & Tesorería

Este módulo presenta la curva de área **Evolución del Saldo de Caja Acumulado** junto con el desglose diario de ingresos, egresos y saldo resultante:

* **Identificación de Puntos Críticos:** Posiciona el cursor sobre la curva para inspeccionar fechas específicas donde el saldo acumulado desciende cerca de cero o entra en terreno negativo por concentración de pagos (quincenas, impuestos o vencimientos de CxP).
* **Comparativa de Entradas vs. Salidas:** El gráfico de barras contrasta el volumen acumulado de ingresos contra egresos en el periodo elegido, facilitando la detección visual de brechas estructurales de liquidez.

---

### 4.3. Capital de Trabajo & Cartera (CxC / CxP)

Permite incorporar compromisos futuros conocidos que aún no forman parte del histórico bancario cerrado.

#### A. Registro de Nuevos Compromisos (Pestaña `Agregar Compromiso`)
1. Selecciona el **Tipo de Movimiento**:
   * `CxC (Cuenta por Cobrar)`: Facturas emitidas a clientes pendientes de cobro.
   * `CxP (Cuenta por Pagar)`: Facturas de proveedores, obligaciones fiscales o pagos programados.
2. Captura el nombre del **Cliente o Proveedor** (incluyendo referencia de factura si aplica).
3. Ingresa el **Monto Nominal** del documento.
4. Selecciona la **Fecha de Vencimiento** esperada.
5. Calibra la **Probabilidad de Cobro/Pago (%)** mediante el control deslizante. El motor multiplicará el monto nominal por este porcentaje ($\text{Monto} \times \text{Probabilidad}$) para evitar sobreestimar cobros inciertos.

**Criterios sugeridos de calibración de probabilidad:**

| Categoría del Documento | Probabilidad Sugerida | Justificación Financiera |
| :--- | :---: | :--- |
| CxP obligatorias (nómina, impuestos, servicios críticos) | $100\%$ | Compromisos ineludibles en fecha fija. |
| CxC vigentes con clientes AAA / historial puntual | $90\% - 100\%$ | Alta certidumbre de cobro en tiempo y forma. |
| CxC con vencimiento entre 1 y 30 días de atraso | $60\% - 80\%$ | Requieren gestión activa de cobranza y presentan riesgo de diferimiento. |
| CxC en litigio o morosidad superior a 60 días | $10\% - 30\%$ | Conservadurismo contable para no comprometer liquidez con flujos altamente inciertos. |

6. Haz clic en **Guardar en Cartera**. El registro quedará almacenado de forma persistente en SQLite y se sumará automáticamente a la proyección de su fecha de vencimiento.

#### B. Actualización de Estatus y Prevención de Duplicidades (Pestaña `Cartera Registrada`)
1. Consulta la tabla de compromisos activos con su identificador único (`id`), tipo, contraparte, monto, vencimiento, probabilidad y estatus actual.
2. Cuando una factura sea cobrada o pagada, o bien cancelada:
   * Localiza su número de **`id`** en la tabla.
   * En el panel inferior **Actualización de Estatus**, selecciona dicho **`id`**, elige el nuevo estado (`Pendiente`, `Pagado` o `Cancelado`) y pulsa **Actualizar Estatus**.
3. **Regla de integridad:** Únicamente los registros con estatus `Pendiente` impactan el pronóstico futuro. Al marcar un registro como `Pagado`, deja de sumarse en las proyecciones para evitar duplicarlo una vez que el movimiento real se cargue en el archivo histórico CSV.

---

### 4.4. Modelado Estocástico & VaR

Dado que los flujos futuros están sujetos a volatilidad operativa, este módulo ejecuta **1,000 simulaciones de Monte Carlo** perturbando el flujo neto diario proyectado con la desviación estándar histórica.

#### Interpretación de las Métricas de Riesgo
* **Saldo Final Esperado:** Media aritmética del saldo de caja al final del horizonte tras las 1,000 trayectorias simuladas.
* **VaR 95% (Value at Risk al 95% de confianza):** Pérdida máxima esperada respecto al saldo final esperado en el $95\%$ de los escenarios. Existe solo un $5\%$ de probabilidad de que el deterioro de caja supere este monto.
* **VaR 99% (Value at Risk al 99% de confianza):** Pérdida máxima esperada en escenarios extremos de estrés ($1\%$ de cola izquierda de la distribución).
* **Probabilidad de Déficit (`prob_deficit`):** Porcentaje de trayectorias simuladas en las que el saldo acumulado cae por debajo de $\$0.00$ en **cualquier día** dentro del horizonte analizado.

#### Guía de Decisión según Probabilidad de Déficit

| Nivel de `prob_deficit` | Diagnóstico de Liquidez | Acciones Recomendadas para Tesorería y CFO |
| :--- | :--- | :--- |
| **$0.0\%$ a $5.0\%$** | **Liquidez Sólida** | Evaluar colocación de excedentes en instrumentos de renta fija de corto plazo (*overnight* o pagarés bancarios). |
| **$5.1\%$ a $20.0\%$** | **Riesgo Moderado / Vigilancia** | Monitorear semanalmente la cobranza de CxC críticas y escalonar pagos no urgentes a proveedores. |
| **Mayor a $20.0\%$** | **Alerta de Tensión de Caja** | Activar protocolo preventivo: ofrecer descuentos por pronto pago a clientes, renegociar plazos de CxP o disponer de líneas de crédito revolventes antes del valle proyectado. |

---

### 4.5. Centro de Inteligencia & IA

Integra dos herramientas de asistencia ejecutiva:

1. **Copiloto CFO:** Analiza tus consultas financieras considerando el contexto vigente de tu proyección (escenario, horizonte, flujo neto y nivel de riesgo).
   * Si el administrador configuró la variable `GEMINI_API_KEY` de **Google AI Studio** en `.env`, el copiloto utiliza el modelo `gemini-1.5-flash` para generar recomendaciones estratégicas redactadas en lenguaje ejecutivo.
   * Si `GEMINI_API_KEY` no está configurada, el sistema activa automáticamente el **Modo Local**, entregando diagnósticos financieros estructurados basados en reglas sin requerir conexión externa.
2. **Agente de Soporte Técnico:** Responde dudas operativas sobre formatos de archivos CSV, interpretación de columnas, permisos por rol y flujos de trabajo dentro de la aplicación.

---

### 4.6. Gestión de Usuarios (Exclusivo Director Financiero / CFO)

Permite administrar el ciclo de vida completo de las cuentas institucionales:

1. **Directorio y Búsqueda Dinámica:** Filtra usuarios registrados en tiempo real escribiendo cualquier fragmento de nombre, correo electrónico, rol o ID.
2. **Dar de Alta Usuario:** Captura nombre completo, correo institucional, contraseña inicial (cifrada automáticamente con `bcrypt`) y asigna uno de los tres perfiles RBAC (`Director Financiero (CFO)`, `Analista de Tesorería` o `Auditor de Riesgo`).
3. **Editar Cuenta y Suspender Accesos:** Selecciona cualquier usuario registrado para modificar su rol, restablecer su contraseña o cambiar su estatus a **`Inactivo`**. Una cuenta marcada como `Inactivo` conserva su historial de auditoría en la base de datos pero tiene bloqueado el acceso al sistema.
4. **Protección de Cuenta Maestra:** La cuenta principal `admin@plurione.com` está protegida contra eliminación accidental para garantizar la continuidad administrativa de la plataforma.

---

## 5. Estructura del Reporte Ejecutivo Excel (`.xlsx`)

Al pulsar **Exportar Reporte Excel**, el sistema descarga un libro multi-pestaña auditado y listo para comités directivos:

| Pestaña | Contenido y Estructura |
| :--- | :--- |
| **Resumen & VaR** | Tabla ejecutiva consolidada con Ingresos Totales Proyectados, Egresos Totales Proyectados, Flujo Neto, Saldo Final Esperado, VaR 95%, VaR 99% y Probabilidad de Déficit (`prob_deficit`), formateada con estilos corporativos. |
| **Proyección de Flujo** | Serie diaria completa del horizonte seleccionado (`Fecha`, `Ingresos Proyectados`, `Egresos Proyectados`, `Flujo Neto Diario`, `Saldo Acumulado`). |
| **Cartera CxC y CxP** | Inventario completo de compromisos registrados en SQLite con su ID, tipo, contraparte, monto nominal, vencimiento, probabilidad y estatus. |
| **Histórico de Caja** | Respaldo tabular de los movimientos históricos reales (`ds`, `Ingresos`, `Egresos`) sobre los cuales se calibró el modelo estacional. |

---

## 6. Cadencia Operativa Recomendada por Perfil

* **Rutina Diaria / Semanal (Analista de Tesorería):**
  1. Actualizar estatus a `Pagado` en *Capital de Trabajo & Cartera* para las facturas liquidadas durante la semana.
  2. Cargar el corte actualizado del archivo histórico CSV en el *Cockpit Financiero*.
  3. Registrar nuevas facturas emitidas (CxC) y compromisos adquiridos (CxP) con su probabilidad estimada.
* **Rutina Semanal de Comité (Director Financiero / CFO):**
  1. Revisar el *Cockpit Financiero* bajo el escenario **Base** y contrastar contra el escenario **Conservador** a 90 días.
  2. Verificar la **Probabilidad de Déficit** y el **VaR 99%** en *Modelado Estocástico & VaR*.
  3. Descargar el archivo `PluriOne_Reporte_<N>D.xlsx` como soporte documental para la junta de dirección.
* **Rutina Mensual de Control (Auditor de Riesgo):**
  1. Auditar los indicadores **MAE**, **MAPE** y **vs. Baseline** para confirmar que la desviación del modelo se mantiene dentro de los parámetros aceptables.
  2. Revisar la vigencia de los usuarios activos en el directorio institucional y verificar que las probabilidades asignadas a la cartera vencida reflejen criterios prudentes.

---

## 7. Glosario Financiero y Estadístico

* **Baseline (Modelo de Referencia):** Estimación ingenua basada únicamente en el promedio aritmético global histórico, utilizada como punto de comparación para medir el valor agregado del modelo estacional.
* **Holdout Validation:** Metodología de evaluación que oculta al modelo los últimos 14 días reales durante el entrenamiento para medir su precisión sobre datos no vistos.
* **MAE (Mean Absolute Error):** Promedio de las diferencias absolutas entre el flujo neto real y el flujo neto pronosticado.
* **MAPE (Mean Absolute Percentage Error):** Promedio porcentual del error de pronóstico respecto al valor real observado.
* **Ponderación de Cartera:** Ajuste por riesgo crediticio u operativo que multiplica el valor nominal de un documento por su probabilidad estimada de ocurrencia.
* **Saldo Inicial Dinámico ($S_0$):** Posición de caja de arranque calculada automáticamente a partir del flujo neto acumulado en el histórico cargado.
* **VaR (Value at Risk):** Medida estadística que cuantifica la pérdida máxima probable de liquidez dentro de un horizonte temporal dado y bajo un nivel de confianza específico ($95\%$ o $99\%$).