<div align="center">

<br/>

```
██╗██████╗ ████████╗██╗   ██╗     ██████╗ ██████╗ ███╗   ██╗████████╗██████╗  ██████╗ ██╗
██║██╔══██╗╚══██╔══╝██║   ██║    ██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔═══██╗██║
██║██████╔╝   ██║   ██║   ██║    ██║     ██║   ██║██╔██╗ ██║   ██║   ██████╔╝██║   ██║██║
██║██╔═══╝    ██║   ╚██╗ ██╔╝    ██║     ██║   ██║██║╚██╗██║   ██║   ██╔══██╗██║   ██║██║
██║██║        ██║    ╚████╔╝     ╚██████╗╚██████╔╝██║ ╚████║   ██║   ██║  ██║╚██████╔╝███████╗
╚═╝╚═╝        ╚═╝     ╚═══╝       ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
                                    C E N T E R
```

**Panel administrativo interno para negocios IPTV**

*Gestión de clientes · Suscripciones · Pagos · Renovaciones*

<br/>

![Python](https://img.shields.io/badge/Python-3.10+-3b82f6?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-10b981?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-94a3b8?style=for-the-badge&logo=sqlite&logoColor=white)
![JWT](https://img.shields.io/badge/Auth-JWT-f59e0b?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![License](https://img.shields.io/badge/Uso-Interno-ef4444?style=for-the-badge)

<br/>

</div>

---

## ✦ Contenido

- [Vista general](#-vista-general)
- [Stack tecnológico](#-stack-tecnológico)
- [Instalación](#-instalación)
- [Primer acceso](#-primer-acceso)
- [Módulos del sistema](#-módulos-del-sistema)
- [Roles y permisos](#-roles-y-permisos)
- [Base de datos](#-base-de-datos)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Diseño y UI](#-diseño-y-ui)
- [Variables de configuración](#-variables-de-configuración)

---

## ✦ Vista General

**IPTV Control Center** es un panel administrativo de uso interno construido con FastAPI y Jinja2. Está diseñado para operar negocios de IPTV de forma profesional: desde el alta de clientes hasta el seguimiento de renovaciones críticas y el control de ingresos.

> **Uso exclusivamente interno.** No tiene registro público. El acceso está controlado por roles y autenticación JWT vía cookie HttpOnly.

### Capacidades principales

| Área | Descripción |
|---|---|
| 📊 Dashboard | Métricas en tiempo real: activos, vencidos, ingresos del mes, ventas del día |
| 👤 Clientes | CRUD completo con etiquetas, búsqueda y vista de historial |
| 📺 Suscripciones | Gestión con cálculo automático de estado por fecha |
| 📦 Planes | Catálogo de planes con activación/desactivación |
| 💰 Pagos | Registro y confirmación de pagos multi-moneda |
| 🔔 Renovaciones | Vista crítica de clientes que vencen hoy, en 3 días o ya vencidos |
| 👥 Usuarios | Gestión de accesos desde la web (solo superadmin) |

---

## ✦ Stack Tecnológico

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   Backend       FastAPI + SQLAlchemy + SQLite           │
│   Plantillas    Jinja2                                  │
│   Auth          passlib[bcrypt] + python-jose (JWT)     │
│   Frontend      HTML + CSS vanilla + JavaScript         │
│   Servidor      Uvicorn                                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Sin frameworks frontend. Sin archivo `.env`. Sin registro público.**

---

## ✦ Instalación

### Requisitos previos

- Python 3.10 o superior
- pip

### Pasos

```bash
# 1. Clonar o descomprimir el proyecto
cd iptv_control

# 2. (Recomendado) Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt
```

### `requirements.txt`

```
fastapi
uvicorn[standard]
sqlalchemy
jinja2
passlib[bcrypt]
python-jose[cryptography]
python-multipart
```

---

## ✦ Primer Acceso

### Paso 1 — Crear el superadmin inicial

> Este script se ejecuta **una sola vez**. Si ya existe un superadmin activo, el script lo detecta y no crea duplicados.

```bash
python create_first_admin.py
```

```
Email: admin@miempresa.com
Password: ········
Confirmar password: ········
✅ Superadmin creado. Ya puedes ingresar al panel.
```

> La contraseña se oculta al escribir gracias a `getpass`. Si las contraseñas no coinciden, el script vuelve a pedirlas.

### Paso 2 — Iniciar el servidor

```bash
uvicorn app.main:app --reload
```

### Paso 3 — Abrir el panel

```
http://localhost:8000
```

> A partir de aquí, la gestión de usuarios (crear, editar, eliminar) se hace **desde el panel web** en la sección `/users`.

---

## ✦ Módulos del Sistema

### 📊 Dashboard

Vista principal con 5 cards de métricas calculadas en tiempo real desde la base de datos:

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Clientes   │  │   Clientes   │  │  Próximos a  │  │  Ventas del  │  │ Ingresos del │
│   Activos    │  │   Vencidos   │  │   Vencer     │  │     Día      │  │     Mes      │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

Debajo de las cards: tabla de **Expiraciones Críticas** (suscripciones con ≤ 3 días restantes).

---

### 👤 Clientes

CRUD completo con los siguientes campos:

| Campo | Tipo | Requerido |
|---|---|---|
| Nombre | Texto | ✅ |
| WhatsApp | Texto | ✅ |
| Email | Texto | ❌ |
| País | Texto | ✅ |
| Username | Texto | ✅ |
| Estado | Enum | ✅ |
| Notas | Texto largo | ❌ |
| Etiquetas | Checkboxes | ❌ |

**Estados de cliente:**

| Badge | Estado |
|---|---|
| 🟢 Verde | Activo |
| 🔴 Rojo | Vencido |
| 🟡 Amarillo | Suspendido |

**Funciones adicionales:**
- Búsqueda en tiempo real por nombre o username
- Filtro por estado
- Vista de detalle con historial completo de suscripciones y pagos

---

### 🏷️ Etiquetas

Tres etiquetas fijas. Se insertan automáticamente al iniciar el servidor. **No se pueden crear, editar ni eliminar desde la UI.**

```
● Cliente frecuente      ● Internacional      ● Soporte frecuente
```

- Relación many-to-many con clientes
- Selección mediante checkboxes en el formulario de cliente
- Visualización como badges en tablas y vistas de detalle

---

### 📺 Suscripciones

CRUD completo. Al seleccionar un plan, el precio y las pantallas se autocompletan vía JavaScript sin recargar la página.

**Lógica de estado (calculada automáticamente al cargar cada vista):**

```python
if fecha_actual > fecha_vencimiento:
    estado = "vencida"
elif (fecha_vencimiento - fecha_actual).days <= 3:
    estado = "por vencer"
else:
    estado = "activa"
```

---

### 📦 Planes

| Campo | Descripción |
|---|---|
| Nombre | Identificador del plan |
| Duración (días) | Vigencia de la suscripción |
| Pantallas | Número de pantallas incluidas |
| Precio | Precio base del plan |
| Activo | Toggle — los inactivos no aparecen al crear suscripciones |

---

### 💰 Pagos

**Métodos de pago disponibles:**
`Binance` · `PayPal` · `Transferencia bancaria` · `Efectivo` · `Otro`

**Monedas disponibles:**
`USD` · `EUR` · `BS` · `COP` · `MXN`

**Flujo de un pago:**

```
Registrar pago           Confirmar pago
[pendiente]     ──────►  [confirmado]
```

- Historial filtrable por cliente
- Solo los pagos `confirmados` cuentan en las métricas del dashboard

---

### 🔔 Renovaciones

Vista de seguimiento dividida en tres secciones con filtrado automático por fecha:

```
┌─────────────────────────────────────────────────────────────┐
│  🔴  VENCEN HOY                                             │
│       Cliente · Plan · Fecha · [Renovar] [Pago] [Ver]       │
├─────────────────────────────────────────────────────────────┤
│  🟡  VENCEN EN 3 DÍAS                                       │
│       Cliente · Plan · Fecha · [Renovar] [Pago] [Ver]       │
├─────────────────────────────────────────────────────────────┤
│  ⚫  YA VENCIDAS                                            │
│       Cliente · Plan · Fecha · [Renovar] [Pago] [Ver]       │
└─────────────────────────────────────────────────────────────┘
```

**Acciones por fila:**
- **Renovar** → abre formulario de nueva suscripción prellenado con los datos del cliente
- **Registrar pago** → redirige al formulario de pago con el cliente preseleccionado
- **Ver cliente** → abre la vista de detalle del cliente

---

### 👥 Usuarios *(exclusivo superadmin)*

Gestión completa desde el panel web en `/users`:

- Listar todos los usuarios con rol y estado
- Crear usuario: email + contraseña + confirmación + rol
- Editar: email, rol, estado activo/inactivo, contraseña (opcional — vacío = sin cambios)
- Eliminar con confirmación modal

---

## ✦ Roles y Permisos

```
┌─────────────────────────────────────────────────────────────┐
│  ROL: superadmin                                            │
│  ✅ Acceso total al sistema                                 │
│  ✅ Sección /users (crear, editar, eliminar usuarios)       │
├─────────────────────────────────────────────────────────────┤
│  ROL: admin                                                 │
│  ✅ Acceso total al sistema                                 │
│  ❌ Sección /users no visible ni accesible                  │
└─────────────────────────────────────────────────────────────┘
```

### Restricciones de seguridad

- ⛔ No se puede eliminar al propio usuario logueado
- ⛔ No se puede eliminar al único superadmin activo
- ⛔ No se puede desactivar al único superadmin activo
- ⛔ No se puede crear un usuario con email ya registrado

---

## ✦ Base de Datos

**Motor:** SQLite · **ORM:** SQLAlchemy · **Archivo:** `iptv.db` (se crea automáticamente)

```
users
 └── id, email, hashed_password, rol, is_active

customers
 └── id, nombre, whatsapp, email, país, username, estado, notas
      └──[M:M]── tags (via customer_tags)

tags
 └── id, nombre
      [seed automático: "Cliente frecuente", "Internacional", "Soporte frecuente"]

plans
 └── id, nombre, duración_días, pantallas, precio, activo

subscriptions
 └── id, customer_id ──► customers
      plan_id ──► plans
      fecha_inicio, fecha_vencimiento, pantallas, precio, estado

payments
 └── id, customer_id ──► customers
      subscription_id ──► subscriptions
      método, monto, moneda, fecha, estado
```

---

## ✦ Estructura del Proyecto

```
iptv_control/
│
├── app/
│   ├── main.py                   # Entrada, startup, seed de tags
│   │
│   ├── core/
│   │   ├── config.py             # Configuración global
│   │   ├── security.py           # Hashing y generación de JWT
│   │   └── dependencies.py       # get_current_user, verificación de roles
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   └── session.py            # Engine y SessionLocal
│   │
│   ├── models/                   # Modelos SQLAlchemy (tablas)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── customer.py
│   │   ├── plan.py
│   │   ├── subscription.py
│   │   └── payment.py
│   │
│   ├── schemas/                  # Validación de entrada/salida (Pydantic)
│   │   └── (un archivo por módulo)
│   │
│   ├── services/                 # Lógica de negocio
│   │   └── (un archivo por módulo)
│   │
│   └── routes/                   # Endpoints FastAPI + renderizado Jinja2
│       └── (un archivo por módulo)
│
├── templates/                    # HTML con Jinja2
│   ├── base.html                 # Layout base: sidebar + navbar
│   ├── login.html
│   ├── dashboard.html
│   ├── users/
│   ├── customers/
│   ├── plans/
│   ├── subscriptions/
│   ├── payments/
│   └── renewals/
│
├── static/
│   ├── css/
│   │   └── main.css              # Variables CSS + estilos globales
│   └── js/
│       └── main.js               # Autocomplete, modales, validaciones
│
├── create_first_admin.py         # Script de primer arranque (una sola vez)
└── requirements.txt
```

---

## ✦ Diseño y UI

**Tema:** Deep Midnight Professional — oscuro, denso, de alta legibilidad.

### Paleta de colores

```css
:root {
  --bg-primary:      #111318;   /* Superficie principal */
  --bg-secondary:    #1a1c20;   /* Sidebar y contenedores */
  --bg-tertiary:     #0c0e12;   /* Fondos profundos, inputs */
  --accent:          #3b82f6;   /* Azul eléctrico — CTAs y foco */
  --accent-hover:    #2563eb;
  --text-main:       #f8fafc;   /* Texto de alta legibilidad */
  --text-muted:      #94a3b8;   /* Labels y texto secundario */
  --border:          #2d313e;   /* Bordes sutiles */
  --status-success:  #10b981;   /* Activo */
  --status-warning:  #f59e0b;   /* Por vencer / Suspendido */
  --status-error:    #ef4444;   /* Vencido / Error */
}
```

### Componentes

- **Sidebar** fijo con `backdrop-filter: blur` y bordes definidos
- **Navbar** superior con usuario logueado y logout
- **Badges** con fondo semi-transparente al 15% del color de estado
- **Inputs** con fondo `--bg-tertiary` y borde de foco en `--accent`
- **Botones** con `border-radius: 6px` y transiciones suaves
- **Modales** para todas las acciones destructivas
- **Mensajes flash** de éxito y error
- **Responsive** básico con sidebar colapsable en móvil

---

## ✦ Variables de Configuración

Toda la configuración está en `app/core/config.py`. No se usa archivo `.env`.

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `SECRET_KEY` | Clave para firmar JWT | Definida en `config.py` |
| `ALGORITHM` | Algoritmo JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duración del token | `480` (8 horas) |
| `DATABASE_URL` | Ruta de la base de datos SQLite | `sqlite:///./iptv.db` |

---

<div align="center">

<br/>

**IPTV Control Center** — uso interno · no distribuir

<br/>

</div>