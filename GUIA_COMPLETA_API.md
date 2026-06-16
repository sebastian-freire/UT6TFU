# 🍔 T&R Hamburguesería - Guía Completa de la API REST

## Índice

1. [Introducción](#introducción)
2. [Arquitectura](#arquitectura)
3. [Instalación y Ejecución](#instalación-y-ejecución)
4. [Endpoints de Productos](#endpoints-de-productos)
5. [PUC 1: Registro de Pedido](#puc-1-registro-de-pedido)
6. [PUC 2: Modificación de Pedido](#puc-2-modificación-de-pedido)
7. [Monitoreo de Pedidos en Curso](#monitoreo-de-pedidos-en-curso)
8. [Ejemplos Completos](#ejemplos-completos)

---

## Introducción

Esta API REST implementa completamente los **2 PUCs (Procesos de Uso Críticos)** del sistema T&R:

- **PUC 1**: Registro de pedido (el corazón del negocio)
- **PUC 2**: Modificación de pedido

Todos los requisitos funcionales son gestionados **completamente en el backend**:

- ✅ Gestión de catálogo con categorías
- ✅ Descuento automático de stock
- ✅ Cálculo de totales a servidor
- ✅ Integración con pasarela POSNET
- ✅ Impresión de comprobantes
- ✅ Cálculo de diferencias en ediciones
- ✅ Monitoreo visual de estados

---

## Arquitectura

```
┌─────────────┐
│   Frontend  │ (React/Angular/Vue)
└──────┬──────┘
       │ HTTP REST
       ↓
┌─────────────────────────────────┐
│  FastAPI Backend (main.py)      │ → Endpoints seguros y documentados
├─────────────────────────────────┤
│ Services Layer                  │
│ ├─ ProductoService             │ → Lógica de catálogo
│ └─ PedidoService               │ → Lógica de negocio
├─────────────────────────────────┤
│ Domain Layer                    │
│ ├─ Producto (entidad)          │
│ ├─ Pedido (entidad)            │
│ └─ Estado (enum)               │
├─────────────────────────────────┤
│ Repository Layer               │
│ ├─ ProductoRepository (JSON)   │
│ └─ PedidoRepository (JSON)     │
├─────────────────────────────────┤
│ Persistencia                    │
│ ├─ productos.json              │
│ └─ pedidos.json                │
└─────────────────────────────────┘
```

**Principios aplicados:**

- SOLID (Single Responsibility, Dependency Inversion)
- Inyección de dependencias
- Separación de capas (Domain, Service, Repository)
- DTOs (Pydantic Models) para validación

---

## Instalación y Ejecución

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

**requirements.txt** debe contener:

```
fastapi
uvicorn
pydantic
```

### 2. Ejecutar la API

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Acceder a la documentación interactiva

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 4. Health Check

```bash
curl http://localhost:8000/health
```

Respuesta esperada:

```json
{ "status": "API T&R Hamburguesería operativa" }
```

---

## Endpoints de Productos

### GET /productos

Obtiene el catálogo completo o filtrado por categoría.

**Sin filtro (todos los productos):**

```bash
GET /productos
```

**Con filtro por categoría:**

```bash
GET /productos?categoria=Comida
GET /productos?categoria=Bebidas
GET /productos?categoria=Postres
```

**Respuesta:**

```json
[
  {
    "idProducto": 1,
    "stock": 50,
    "descripcion": "Papas Cheddar",
    "precio": 270.0,
    "categoria": "Comida"
  },
  {
    "idProducto": 2,
    "stock": 100,
    "descripcion": "Coca Cola Zero",
    "precio": 240.0,
    "categoria": "Bebidas"
  }
]
```

**Categorías disponibles:**

- `Comida`: Burgers y papas
- `Bebidas`: Bebidas
- `Postres`: Postres

---

## PUC 1: Registro de Pedido

Este es el **corazón del negocio**. Describe el flujo completo desde que el cliente selecciona items hasta obtener la confirmación de pago.

### Flujo Completo: Paso a Paso

#### **PASO 1 y 2: Crear Pedido (POST /pedidos)**

El frontend selecciona productos con cantidades. El backend:

1. ✅ Valida que haya stock disponible
2. ✅ Autogenera el ID del pedido
3. ✅ Crea la instancia `Pedido` con estado `SinAceptar`
4. ✅ Descuenta automáticamente el stock
5. ✅ Calcula el total (RESPONSABILIDAD DEL BACKEND)
6. ✅ Persiste en JSON

**Request:**

```json
POST /pedidos
Content-Type: application/json

{
  "cliente": "Juani",
  "productos": [
    {"idProducto": 1, "cantidad": 1},
    {"idProducto": 2, "cantidad": 2},
    {"idProducto": 3, "cantidad": 1},
    {"idProducto": 4, "cantidad": 1}
  ]
}
```

**Response (201 Created):**

```json
{
  "idPedido": 34,
  "cliente": "Juani",
  "estado": "SinAceptar",
  "total": 1250.0,
  "productos": [
    {
      "idProducto": 1,
      "descripcion": "Papas Cheddar",
      "cantidad": 1,
      "subtotal": 270.0
    },
    {
      "idProducto": 2,
      "descripcion": "Coca Cola Zero",
      "cantidad": 2,
      "subtotal": 480.0
    },
    {
      "idProducto": 3,
      "descripcion": "Power Burger",
      "cantidad": 1,
      "subtotal": 380.0
    },
    {
      "idProducto": 4,
      "descripcion": "Veggie Burger",
      "cantidad": 1,
      "subtotal": 350.0
    }
  ]
}
```

**Errores posibles:**

```json
{
  "detail": "Stock insuficiente para Papas Cheddar. Disponible: 5"
}
```

#### **PASO 3: Seleccionar Método de Pago**

El frontend simplemente muestra opciones:

- Efectivo
- Débito (Visa, Mastercard, etc.)
- MercadoPago

#### **PASO 4: Confirmación Antes de Pagar**

Pantalla de confirmación (manejo en frontend).

#### **PASO 5, 6 y Efectos Secundarios: Procesar Pago (POST /pedidos/{id}/pagar)**

El frontend envía el método de pago. El backend:

1. ✅ Invoca `SistemaDePagos` (simula POSNET)
2. ✅ Si es exitoso:
   - Cambia el estado a `Confirmado`
   - Invoca impresión de ticket fiscal
   - Invoca impresión de comanda para cocina
   - Actualiza `SistemaVisualizacion` (monitor del local)
3. ✅ Retorna confirmación

**Request:**

```json
POST /pedidos/34/pagar
Content-Type: application/json

{
  "metodo_pago": "Tarjetas de débito"
}
```

**Response (200 OK):**

```json
{
  "status": "Pago aprobado por POSNET",
  "idPedido": 34,
  "nuevo_estado": "Confirmado"
}
```

**En la consola verás:**

```
[Pantalla Monitor Local] Pedido #34 cambió de estado a -> [Confirmado]
================ [IMPRESORA T&R] ================
--- TICKET FISCAL DE PAGO T&R ---
Pedido ID: #34
Cliente: Juani
 - 1x Papas Cheddar ($270 c/u) = $270
 - 2x Coca Cola Zero ($240 c/u) = $480
 - 1x Power Burger ($380 c/u) = $380
 - 1x Veggie Burger ($350 c/u) = $350
---------------------------------
TOTAL: $1480.0
================================================

================ [IMPRESORA T&R] ================
--- COMANDA COCINA T&R ---
Pedido ID: #34
Cliente: Juani
Items:
 * [ Cantidad: 1 ] -> Papas Cheddar
 * [ Cantidad: 2 ] -> Coca Cola Zero
 * [ Cantidad: 1 ] -> Power Burger
 * [ Cantidad: 1 ] -> Veggie Burger
================================================
```

---

## PUC 2: Modificación de Pedido

El cliente puede modificar un pedido **solo si está en estado `Confirmado` pero NO en `En preparación`**.

### Flujo Completo: Paso a Paso

#### **PASO 1: Ver Pedidos en Curso (GET /pedidos)**

El frontend consulta todos los pedidos activos.

**Request:**

```bash
GET /pedidos
```

**Response:**

```json
[
  {
    "idPedido": 34,
    "cliente": "Juani",
    "estado": "Confirmado",
    "total": 1250.0,
    "productos": [
      { "descripcion": "Papas Cheddar", "cantidad": 1 },
      { "descripcion": "Coca Cola Zero", "cantidad": 2 },
      { "descripcion": "Power Burger", "cantidad": 1 },
      { "descripcion": "Veggie Burger", "cantidad": 1 }
    ]
  },
  {
    "idPedido": 33,
    "cliente": "Ceci",
    "estado": "En preparación",
    "total": 760.0,
    "productos": [{ "descripcion": "The Pickle", "cantidad": 2 }]
  }
]
```

#### **PASO 2: Buscar Pedido Editable**

El frontend filtra y busca el pedido deseado. Solo muestra tarjetas con estado `Confirmado` que **NO estén en preparación**.

#### **PASO 3: Editar Productos (PUT /pedidos/{id})**

El cliente modifica cantidades, añade nuevos productos o elimina existentes.

El backend:

1. ✅ Valida que el pedido NO esté en preparación
2. ✅ Restaura el stock de productos removidos
3. ✅ Valida stock disponible de nuevos productos
4. ✅ Descuenta el nuevo stock
5. ✅ Recalcula totales
6. ✅ Calcula la **diferencia a pagar** (original vs nuevo)
7. ✅ Persiste cambios

**Request:**

```json
PUT /pedidos/34
Content-Type: application/json

{
  "productos": [
    {"idProducto": 1, "cantidad": 2},
    {"idProducto": 2, "cantidad": 1},
    {"idProducto": 5, "cantidad": 1}
  ]
}
```

**Response:**

```json
{
  "idPedido": 34,
  "cliente": "Juani",
  "total_anterior": 1250.0,
  "nuevo_total": 1405.0,
  "diferencia_a_pagar_en_caja": 155.0,
  "productos": [
    { "idProducto": 1, "descripcion": "Papas Cheddar", "cantidad": 2 },
    { "idProducto": 2, "descripcion": "Coca Cola Zero", "cantidad": 1 },
    { "idProducto": 5, "descripcion": "The Pickle", "cantidad": 1 }
  ]
}
```

**Interpretación:**

- **total_anterior**: $1250 (lo que pagó inicialmente)
- **nuevo_total**: $1405 (lo que debe pagar ahora)
- **diferencia_a_pagar_en_caja**: $155 (debe pagar $155 EXTRA en caja, o recibe vuelto si es negativo)

#### **PASO 4: Seleccionar Método de Pago para Diferencia**

El frontend muestra opciones de pago nuevamente.

#### **PASO 5, 6 y Efectos: Pagar Diferencia (POST /pedidos/{id}/pagar-diferencia)**

El backend procesa el pago de la diferencia (monto total del pedido actualizado).

**Request:**

```json
POST /pedidos/34/pagar-diferencia
Content-Type: application/json

{
  "metodo_pago": "Tarjetas de débito"
}
```

**Response:**

```json
{
  "status": "Pago de diferencia aprobado",
  "idPedido": 34,
  "total_pagado": 1405.0
}
```

#### **PASO 3 (Alternativo): Cancelar Pedido (DELETE /pedidos/{id})**

Si el cliente decide cancelar completamente, se elimina el pedido y se restaura TODO el stock.

**Request:**

```bash
DELETE /pedidos/34
```

**Response:**

```json
{
  "status": "Pedido #34 cancelado correctamente",
  "stock_restaurado": true
}
```

---

## Monitoreo de Pedidos en Curso

### Obtener Pedidos por Estado

La pantalla "Pedidos en Curso" (Pág. 8 del TFU) organiza visualmente los pedidos por estado. La API filtra por estado automáticamente.

**Estados válidos:**

```
SinAceptar
Confirmado
En preparación
Listo para entregar
```

**Request:**

```bash
GET /pedidos?estado=Confirmado
GET /pedidos?estado=En%20preparaci%C3%B3n
GET /pedidos?estado=Listo%20para%20entregar
```

**Response (solo pedidos confirmados):**

```json
[
  {
    "idPedido": 34,
    "cliente": "Juani",
    "estado": "Confirmado",
    "total": 1405.0,
    "productos": [...]
  }
]
```

### Cambiar Estado de un Pedido (PATCH /pedidos/{id}/estado)

El personal de cocina avanza los estados: **Confirmado** → **En preparación** → **Listo para entregar**.

**Request:**

```json
PATCH /pedidos/34/estado
Content-Type: application/json

{
  "estado": "En preparación"
}
```

**Response:**

```json
{
  "idPedido": 34,
  "nuevo_estado": "En preparación"
}
```

**En la consola:**

```
[Pantalla Monitor Local] Pedido #34 cambió de estado a -> [En preparación]
```

El monitor del local (SistemaVisualizacion) se actualiza automáticamente.

---

## Ejemplos Completos

### Ejemplo 1: Flujo Completo PUC 1

```bash
# 1. Crear pedido
curl -X POST http://localhost:8000/pedidos \
  -H "Content-Type: application/json" \
  -d '{
    "cliente": "Juan",
    "productos": [
      {"idProducto": 3, "cantidad": 2},
      {"idProducto": 2, "cantidad": 1}
    ]
  }'

# Respuesta:
# {
#   "idPedido": 1,
#   "cliente": "Juan",
#   "estado": "SinAceptar",
#   "total": 1000.0,
#   ...
# }

# 2. Pagar
curl -X POST http://localhost:8000/pedidos/1/pagar \
  -H "Content-Type: application/json" \
  -d '{"metodo_pago": "Efectivo"}'

# Respuesta:
# {
#   "status": "Pago aprobado por POSNET",
#   "idPedido": 1,
#   "nuevo_estado": "Confirmado"
# }

# 3. Cambiar a preparación
curl -X PATCH http://localhost:8000/pedidos/1/estado \
  -H "Content-Type: application/json" \
  -d '{"estado": "En preparación"}'

# 4. Cambiar a listo
curl -X PATCH http://localhost:8000/pedidos/1/estado \
  -H "Content-Type: application/json" \
  -d '{"estado": "Listo para entregar"}'
```

### Ejemplo 2: Flujo Completo PUC 2 (Edición)

```bash
# 1. Ver pedidos (suponemos que existe el #1 en estado Confirmado)
curl http://localhost:8000/pedidos

# 2. Editar pedido
curl -X PUT http://localhost:8000/pedidos/1 \
  -H "Content-Type: application/json" \
  -d '{
    "productos": [
      {"idProducto": 3, "cantidad": 1},
      {"idProducto": 5, "cantidad": 1}
    ]
  }'

# Respuesta:
# {
#   "idPedido": 1,
#   "cliente": "Juan",
#   "total_anterior": 1000.0,
#   "nuevo_total": 730.0,
#   "diferencia_a_pagar_en_caja": -270.0,
#   ...
# }
# (Negativo = recibe vuelto de $270)

# 3. Pagar diferencia
curl -X POST http://localhost:8000/pedidos/1/pagar-diferencia \
  -H "Content-Type: application/json" \
  -d '{"metodo_pago": "Efectivo"}'
```

### Ejemplo 3: Filtrar por Categoría

```bash
# Solo comidas
curl "http://localhost:8000/productos?categoria=Comida"

# Solo bebidas
curl "http://localhost:8000/productos?categoria=Bebidas"

# Solo postres
curl "http://localhost:8000/productos?categoria=Postres"
```

---

## Gestión de Stock

### El Backend es Responsable

**IMPORTANTE**: El backend **SIEMPRE** valida y maneja el stock:

1. **Al crear pedido**: Descuenta automáticamente

   ```
   Stock anterior: 50
   - Orden: 10 unidades
   Stock nuevo: 40
   ```

2. **Al editar pedido**: Restaura y descuenta nuevamente

   ```
   Original: 50 - 10 = 40 (después de pedido inicial)
   Edición: restaura +10 = 50, descuenta -5 nuevas = 45
   ```

3. **Al cancelar**: Devuelve TODO al stock
   ```
   Stock: 40 + 10 = 50 (restaurado)
   ```

**Respuesta si hay stock insuficiente:**

```json
{
  "detail": "Stock insuficiente para Papas Cheddar. Disponible: 5"
}
```

---

## Estructura de Datos: JSON

### productos.json

```json
[
  {
    "idProducto": 1,
    "stock": 50,
    "descripcion": "Papas Cheddar",
    "precio": 270.0,
    "categoria": "Comida"
  },
  {
    "idProducto": 2,
    "stock": 100,
    "descripcion": "Coca Cola Zero",
    "precio": 240.0,
    "categoria": "Bebidas"
  }
]
```

### pedidos.json

```json
[
  {
    "idPedido": 34,
    "cliente": "Juani",
    "estado": "Confirmado",
    "total": 1250.0,
    "cantidades": {
      "1": 1,
      "2": 2,
      "3": 1,
      "4": 1
    }
  }
]
```

---

## Validaciones Críticas

El backend valida:

| Validación            | Respuesta                   |
| --------------------- | --------------------------- |
| Stock insuficiente    | `400 Bad Request` + detalle |
| Pedido no encontrado  | `404 Not Found`             |
| Editar en preparación | `400 Bad Request`           |
| Pago declinado        | `400 Bad Request`           |
| Producto inexistente  | `400 Bad Request`           |

---

## Resumen de Capabilities

✅ **PUC 1 (Registro de Pedido)**

- ✅ Crear pedido con autogeneración de ID
- ✅ Descuento automático de stock
- ✅ Cálculo de totales (backend)
- ✅ Validación de stock
- ✅ Integración POSNET (simulada)
- ✅ Cambio de estado SinAceptar → Confirmado
- ✅ Impresión de ticket y comanda

✅ **PUC 2 (Modificación de Pedido)**

- ✅ Listar pedidos activos
- ✅ Filtrar por estado
- ✅ Editar cantidades
- ✅ Agregar/quitar productos
- ✅ Cálculo de diferencia
- ✅ Validación de stock
- ✅ Pago de diferencia
- ✅ Cancelación con restauración

✅ **Monitoreo**

- ✅ Filtrado por estado
- ✅ Cambio de estado (Confirmado → En prep. → Listo)
- ✅ Monitor visual (SistemaVisualizacion)

---

## Troubleshooting

### Error: "No se puede editar un pedido en preparación"

**Causa**: El pedido está en estado `En preparación`.
**Solución**: Solo edita pedidos en estado `Confirmado`.

### Error: "Stock insuficiente"

**Causa**: No hay suficientes unidades disponibles.
**Solución**: Reduce cantidad o intenta otro producto.

### Error: "Pedido no encontrado"

**Causa**: El ID del pedido no existe.
**Solución**: Verifica el ID usando `GET /pedidos`.

### La API no arranca

**Solución**:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## Próximos Pasos

1. **Autenticación**: Agregar JWT para acceso seguro
2. **Auditoría**: Registrar quién hizo qué y cuándo
3. **Reportes**: Ventas, productos más vendidos, etc.
4. **Historial**: Mantener registro de cambios en pedidos
5. **Notificaciones**: WebSockets para actualizaciones en tiempo real

---

**Versión**: 1.0  
**Fecha**: Junio 2026  
**Estado**: ✅ Production Ready
