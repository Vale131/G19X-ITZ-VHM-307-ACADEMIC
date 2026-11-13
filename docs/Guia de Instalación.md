# Guía de Instalación y Despliegue | PluriOne

**Sistema Predictivo de Flujo de Efectivo y Tesorería Ejecutiva**  
**Identificador de Proyecto:** `G19X-ITZ-VHM-307-ACADEMIC`  
**Repositorio Oficial:** `https://github.com/Vale131/G19X-ITZ-VHM-307-ACADEMIC.git`  
**Versión:** v4.2 Producción  

---

## 1. Propósito y Reproducibilidad

Esta guía detalla el procedimiento estándar para clonar, configurar, validar y ejecutar **PluriOne** en un entorno local aislado. El uso de un entorno virtual de Python (`venv`) y un manifiesto de dependencias exactas (`requirements.txt`) garantiza un despliegue reproducible en menos de cinco minutos sobre Windows, macOS o Linux.

---

## 2. Prerrequisitos del Sistema

* **Sistema Operativo:** Windows 10/11, macOS o Linux.
* **Python:** Versión **3.10 o superior** con `pip` habilitado en el `PATH` del sistema.
* **Git:** Cliente de línea de comandos para clonar el repositorio.
* **Navegador Web:** Google Chrome, Microsoft Edge, Mozilla Firefox o Safari.

---

## 3. Instalación Paso a Paso

Abre una terminal (**PowerShell** en Windows o **Terminal** en macOS/Linux) y ejecuta los siguientes comandos en orden:

### Paso 1. Clonar el repositorio oficial

```bash
git clone https://github.com/Vale131/G19X-ITZ-VHM-307-ACADEMIC.git
cd G19X-ITZ-VHM-307-ACADEMIC
```

### Paso 2. Crear y activar el entorno virtual

```bash
python -m venv .venv
```

* **En Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
* **En macOS / Linux:**
  ```bash
  source .venv/bin/activate
  ```

### Paso 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 4. Configurar las variables de entorno (`.env`)

Crea el archivo `.env` en la raíz del proyecto a partir de la plantilla `.env.example`:

```bash
cp .env.example .env
```

Edita `.env` y define tus parámetros locales:

```env
# Obligatoria: Contraseña inicial para crear el administrador (admin@plurione.com) en el primer arranque
ADMIN_INITIAL_PASSWORD=TuPasswordSegura2026!

# Opcional: Llave de API de Google AI Studio (no utiliza OpenAI) para modules/ai_copilot.py
GEMINI_API_KEY=
```

| Variable | Requerida | Descripción |
| :--- | :---: | :--- |
| `ADMIN_INITIAL_PASSWORD` | **Sí** | Define la contraseña con la que se creará automáticamente la cuenta `admin@plurione.com` en el primer arranque. No existen contraseñas escritas en el código fuente. |
| `GEMINI_API_KEY` | **Opcional** | Llave obtenida desde **Google AI Studio** para el Copiloto CFO (`modules/ai_copilot.py`). Si se omite, el asistente opera con un motor de diagnóstico financiero local sin afectar ninguna otra función del sistema. |

---

## 4. Validación Automatizada y Arranque

### 4.1. Ejecutar la suite de pruebas (`pytest`)
Antes de iniciar la interfaz web, verifica la integridad de la base de datos, el cifrado `bcrypt`, las operaciones CRUD de cartera y el motor Monte Carlo:

```bash
python -m pytest tests/
```

La ejecución debe finalizar con **7 pruebas aprobadas (`7 passed`)**. La suite utiliza una base de datos temporal (`flujo_efectivo_test.db`) que se destruye automáticamente al concluir, sin alterar tus datos operativos.

### 4.2. Iniciar el servidor de aplicación

```bash
python -m streamlit run app.py
```

El servidor se iniciará en `http://localhost:8501` y abrirá automáticamente la pantalla de inicio de sesión en tu navegador predeterminado.

---

## 5. Primer Acceso y Solución de Incidencias

### 5.1. Credenciales de Primer Acceso
1. **Correo electrónico:** `admin@plurione.com`
2. **Contraseña:** El valor configurado en `ADMIN_INITIAL_PASSWORD` dentro de `.env`.
3. **Precarga automática de datos:** Al iniciar sesión por primera vez, si la tabla `historico_flujo` está vacía, el sistema ingesta automáticamente `data/sample_flujo.csv` para habilitar de inmediato los tableros, métricas Holdout y simulaciones VaR.

### 5.2. Resolución de Problemas Frecuentes

| Síntoma | Causa Probable | Solución |
| :--- | :--- | :--- |
| Advertencia en consola: `ADMIN_INITIAL_PASSWORD no está configurada` y acceso denegado | Se ejecutó `streamlit run app.py` antes de crear el archivo `.env` o la variable estaba vacía. | Configura `ADMIN_INITIAL_PASSWORD` en `.env`, elimina el archivo `flujo_efectivo.db` generado sin administrador y vuelve a ejecutar `python -m streamlit run app.py`. |
| Error de permisos al activar `.venv` en Windows PowerShell | La política de ejecución de scripts local restringe archivos `.ps1`. | Ejecuta `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` en PowerShell y reactiva `.venv\Scripts\Activate.ps1`. |
| El Copiloto CFO muestra *Modo Local Activo* | La variable `GEMINI_API_KEY` está vacía en `.env`. | Comportamiento esperado cuando no se configura llave de Google AI Studio. Para habilitar respuestas generativas con `gemini-1.5-flash`, agrega tu llave de Google AI Studio en `.env` y reinicia la aplicación. |