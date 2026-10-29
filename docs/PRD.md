# Product Requirement Document (PRD) | PluriOne

**Sistema Predictivo de Flujo de Efectivo & Tesorería Ejecutiva**  
**Código de Identificación Académica:** `G19X-ITZ-VHM-307-ACADEMIC`  
**Repositorio Oficial:** `Vale131/G19X-ITZ-VHM-307-ACADEMIC`  
**Versión de Producción:** v3.2 / v4.2 Actualizada · Octubre 2026  

---

## 1. Visión y Estrategia del Producto

# Product Requirement Document (PRD) — PluriOne

**Estándar Académico:** `G19X-ITZ-VHM-307-ACADEMIC`  
**Autor:** Valeria Hernández Mendoza  
**Institución:** Instituto Tecnológico de Zitácuaro  

---

## 1. Definición del Problema
Las pequeñas y medianas empresas enfrentan severos problemas de iliquidez debido a la falta de herramientas accesibles para proyectar su flujo de caja futuro. El análisis tradicional omite la estacionalidad semanal de los ingresos/egresos y no cuantifica el riesgo implícito en el cobro diferido de las Cuentas por Cobrar (CxC) y el pago de las Cuentas por Pagar (CxP).

---

## 2. Definición de Usuarios y Roles (RBAC)
* **Director Financiero (CFO):** Acceso total al Cockpit Ejecutivo, ajuste de escenarios estratégicos, gestión de usuarios institucionales y exportación de reportes.
* **Analista de Tesorería:** Carga de histórico de caja, alta y actualización de compromisos de cartera (CxC / CxP).
* **Auditor de Riesgo:** Consulta de simulaciones estocásticas de Monte Carlo, métricas VaR y evaluación de precisión (Holdout MAE / MAPE).

---

## 3. Fuera de Alcance (Out of Scope)
* Conexión en tiempo real mediante APIs bancarias (Open Banking).
* Emisión o timbrado de facturación electrónica (CFDI).
* Procesamiento automatizado de transacciones multimoneda en tiempo real.

---

## 4. Declaración de Uso de Inteligencia Artificial
En el desarrollo de esta suite se utilizaron asistentes de Inteligencia Artificial para:
1. El diseño del esquema visual modular en Streamlit y paleta de colores institucional.
2. La estructuración de consultas SQL parametrizadas para la persistencia segura de datos.
3. La generación automatizada de pruebas unitarias y fixtures de aislamiento en `pytest`.


### 1. Visión
> *"Que ninguna decisión de liquidez en PluriOne dependa de la intuición de un analista: que cada decisión de inversión, cobro y pago tenga detrás un copiloto matemático auditable, cuantitativo y transparente."*

El sistema resuelve la ineficiencia estructural de la tesorería corporativa mediante tres principios fundamentales:
1. **Evidencia sobre intuición:** Toda cifra presentada en el Cockpit proviene de un cálculo estadístico estacional o de una consulta auditable en la base de datos relacional.
2. **Incertidumbre explícita:** Ninguna proyección se presenta como una certeza absoluta; se acompaña siempre de métricas de precisión Holdout (MAE/MAPE) y Value at Risk (VaR 95%/99%).
3. **Decisión prescriptiva:** El sistema está orientado a facilitar la acción inmediata (reprogramar pagos, acelerar cobros o ajustar reservas de capital de trabajo).

---

## 2. Personas y Control de Acceso Basado en Roles (RBAC)

El acceso al sistema está regulado por un esquema RBAC de tres niveles configurado en `modules/database.py` y `app.py`:

| Persona / Rol | Identificador en Sistema | Permisos y Capacidades |
| :--- | :--- | :--- |
| **Director Financiero (CFO)** | `Director Financiero (CFO)` | Acceso total al sistema, exportación de reportes ejecutivos en Excel, gestión integral de usuarios (creación, edición, eliminación y cambio de estatus) y configuración de parámetros globales. |
| **Analista de Tesorería** | `Analista de Tesorería` | Carga de históricos CSV, registro y edición de cartera de cuentas por cobrar y pagar (CxC/CxP), selección de escenarios estratégicos y horizontes temporales. |
| **Auditor de Riesgo** | `Auditor de Riesgo` | Vista de consulta ejecutiva sobre métricas de error (MAE/MAPE), simulaciones estocásticas Monte Carlo (VaR 95%, VaR 99%) y diagnóstico prescriptivo. |

---

## 3. Requerimientos Funcionales (RF)

### RF-01: Autenticación y Seguridad de Accesos
* **Descripción:** El acceso a la plataforma requiere autenticación obligatoria mediante correo y contraseña.
* **Especificación:** Las contraseñas se almacenan únicamente como hashes de `bcrypt` con generación de sal individual (`bcrypt.gensalt()`). Se elimina cualquier comparación en texto plano.
* **Criterio de Aceptación:** Si la variable `ADMIN_INITIAL_PASSWORD` no está configurada en `.env`, el sistema notifica una advertencia formal sin utilizar claves por defecto escritas en código.

### RF-02: Motor Predictivo Estocástico de Flujo de Caja
* **Descripción:** Generación de proyecciones diarias de ingresos, egresos, flujo neto y saldo acumulado para horizontes de 30 a 365 días.
* **Especificación:** El motor aplica patrones estacionales por día de la semana ajustados por multiplicadores de escenario (*Base: 1.0/1.0*, *Optimista: 1.15/0.90*, *Conservador: 0.85/1.10*) y saldo inicial dinámico.
* **Criterio de Aceptación:** El saldo inicial se calcula automáticamente como la suma del neto histórico acumulado o a través del parámetro asignado en la llamada.

### RF-03: Integración Unificada de Cartera (CxC / CxP)
* **Descripción:** Incorporación de compromisos operativos de cobro y pago al flujo proyectado.
* **Especificación:** Esquema de base de datos unificado (`cartera`: `id`, `tipo`, `cliente_proveedor`, `monto`, `fecha_vencimiento`, `probabilidad`, `estatus`).
* **Criterio de Aceptación:** Cada compromiso con estatus *Pendiente* impacta la fecha de vencimiento multiplicando su importe por la probabilidad de realización ($Monto \times Probabilidad$).

### RF-04: Autoevaluación del Modelo (Holdout Backtesting & Baseline)
* **Descripción:** Medición continua del margen de error del modelo sobre datos reales y comparación contra línea base.
* **Especificación:** El sistema aparta los últimos 14 días históricos, simula la proyección sobre dicha ventana y despliega **MAE** (Error Absoluto Medio) y **MAPE** (Error Porcentual Absoluto Medio), junto con la métrica de optimización vs. promedio simple.
* **Criterio de Aceptación:** Despliegue en tiempo real de las tarjetas MAE y MAPE en el Cockpit Financiero.

### RF-05: Simulación Estocástica y Value at Risk (VaR)
* **Descripción:** Cuantificación del riesgo de iliquidez mediante simulaciones de Monte Carlo.
* **Especificación:** Generación de 1,000 trayectorias estocásticas basadas en la volatilidad histórica de los flujos.
* **Criterio de Aceptación:** Despliegue en pantalla de las tarjetas **VaR 95%**, **VaR 99%** y **Probabilidad de Déficit (%)**, combinadas con el gráfico de distribución de densidad.

### RF-06: Administración Interactiva de Usuarios
* **Descripción:** Panel de control de usuarios con buscador en tiempo real.
* **Especificación:** Filtrado por texto (nombre, correo, rol, ID) y por estatus (Activo/Inactivo). Formulario de edición con preservación del índice de rol para evitar modificaciones involuntarias.
* **Criterio de Aceptación:** Edición directa y protección incondicional de la cuenta principal del administrador.

---

## 4. Requerimientos No Funcionales (RNF)

* **RNF-01 (Cifrado):** Ninguna contraseña se almacena o compara en texto plano. Uso obligatorio de `bcrypt`.
* **RNF-02 (Interfaz Adaptativa):** La interfaz de Streamlit utiliza la directiva de ancho adaptativo `width="stretch"` eliminando parámetros obsoletos (`use_container_width`).
* **RNF-03 (Persistencia Relacional):** Toda la información operativa y de usuarios persiste en SQLite (`flujo_efectivo.db`).
* **RNF-04 (Compatibilidad de Exportación):** El reporte Excel consolidado hidrata correctamente los campos de riesgo utilizando la clave unificada `prob_deficit`.

---

## 5. Arquitectura del Repositorio de Código

```text
G19X-ITZ-VHM-307-ACADEMIC/
├── app.py                      # Orquestador principal de la aplicación Streamlit
├── requirements.txt            # Dependencias del proyecto (Streamlit, Pandas, Bcrypt, Plotly, openpyxl, etc.)
├── .env.example                # Plantilla de variables de entorno (ADMIN_INITIAL_PASSWORD)
├── README.md                   # Guía de instalación y arquitectura en la raíz del repositorio
├── docs/
│   ├── PRD.md                  # Documento de Requerimientos del Producto (Markdown)
│   └── MVP.md                  # Especificación del MVP (Markdown)
├── data/
│   └── sample_flujo.csv        # Datos históricos de muestra
└── modules/
    ├── auth.py                 # Pantalla de autenticación estilizada
    ├── database.py             # Persistencia SQLite, bcrypt y CRUD de usuarios
    ├── forecasting.py          # Motor predictivo, Holdout MAE/MAPE, baseline y gráficos
    ├── cxc_cxp.py              # Gestión unificada de cartera (CxC/CxP)
    ├── risk.py                 # Monte Carlo y métricas VaR 95/99
    ├── reports.py              # Exportador de reportes en Excel
    ├── ai_copilot.py           # Copiloto financiero IA (CFO Assistant)
    ├── support_agent.py        # Agente de soporte técnico IA (PluriBot)
    └── styles.py               # Estilos CSS ejecutivos globales
```