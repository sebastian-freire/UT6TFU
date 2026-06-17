# 🎯 INSTRUCCIONES DE USO - T&R Hamburguesería API

## START AQUÍ 👈

Si es la primera vez que usas este proyecto, sigue estos pasos:

### ✅ Paso 1: Instalar Dependencias

```bash
cd "c:\Users\sebaf\Desktop\ADA ENTREGAS\UT6TFU"
pip install -r requirements.txt
```

**Verifica que se instale:**

- fastapi
- uvicorn
- pydantic

### ✅ Paso 2: Ejecutar la API

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Deberías ver:**

```
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete [uvicorn running on http://0.0.0.0:8000]
```

### ✅ Paso 3: Abrir Documentación Interactiva

Abre en tu navegador:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Allí puedes probar todos los endpoints directamente.

### ✅ Paso 4: Verificar que funciona

```bash
curl http://localhost:8000/health
```

Deberías recibir:

```json
{ "status": "API T&R Hamburguesería operativa" }
```

---

## 🔄 FLUJOS COMPLETOS

### FLUJO 1: Crear y Pagar un Pedido (PUC 1)

#### Paso 1a: Ver el catálogo

```bash
curl http://localhost:8000/productos
```

**Respuesta:**

```json
[
  {
    "idProducto": 1,
    "stock": 50,
    "descripcion": "Papas Cheddar",
    "precio": 270.0,
    "categoria": "comida"
  },
  ...
]
```

#### Paso 1b: Filtrar por categoría (opcional)

```bash
# Ver solo comidas
curl "http://localhost:8000/productos?categoria=comida"

# Ver solo bebidas
curl "http://localhost:8000/productos?categoria=bebida"

# Ver solo postres
curl "http://localhost:8000/productos?categoria=postre"
```

#### Paso 1c: Crear un pedido

```bash
curl -X POST http://localhost:8000/pedidos \
  -H "Content-Type: application/json" \
  -d '{
    "cliente": "Juani",
    "productos": [
      {"idProducto": 1, "cantidad": 1},
      {"idProducto": 2, "cantidad": 2},
      {"idProducto": 3, "cantidad": 1},
      {"idProducto": 4, "cantidad": 1}
    ]
  }'
```

**Lo que pasa automáticamente:**

- ✅ Genera ID: #34
- ✅ Descuenta stock
- ✅ Calcula total: $1250
- ✅ Estado: SinAceptar
- ✅ Guarda en JSON

**Respuesta:**

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
    ...
  ]
}
```

#### Paso 1d: Pagar el pedido

```bash
curl -X POST http://localhost:8000/pedidos/34/pagar \
  -H "Content-Type: application/json" \
  -d '{"metodo_pago": "Tarjetas de débito"}'
```

**Lo que pasa automáticamente:**

- ✅ POSNET: Simula transacción
- ✅ Estado: SinAceptar → Confirmado
- ✅ Imprime Ticket Fiscal
- ✅ Imprime Comanda
- ✅ Monitor se actualiza

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

**Respuesta HTTP:**

```json
{
  "status": "Pago aprobado por POSNET",
  "idPedido": 34,
  "nuevo_estado": "Confirmado"
}
```

---

### FLUJO 2: Editar un Pedido (PUC 2)

#### Paso 2a: Ver pedidos en curso

```bash
curl http://localhost:8000/pedidos
```

**Respuesta:**

```json
[
  {
    "idPedido": 34,
    "cliente": "Juani",
    "estado": "Confirmado",
    "total": 1250.0,
    "productos": [...]
  },
  ...
]
```

#### Paso 2b: Filtrar solo los que pueden editarse

```bash
# Solo confirmados (pueden editarse)
curl "http://localhost:8000/pedidos?estado=SinAceptar"

# Solo confirmados (pueden editarse)
curl "http://localhost:8000/pedidos?estado=Confirmado"

# Los que NO pueden editarse (ya en cocina)
curl "http://localhost:8000/pedidos?estado=En%20preparaci%C3%B3n"
```

#### Paso 2c: Editar un pedido

```bash
curl -X PUT http://localhost:8000/pedidos/34 \
  -H "Content-Type: application/json" \
  -d '{
    "productos": [
      {"idProducto": 1, "cantidad": 2},
      {"idProducto": 2, "cantidad": 1},
      {"idProducto": 5, "cantidad": 1}
    ]
  }'
```

**Lo que pasa automáticamente:**

- ✅ Valida que NO esté en preparación
- ✅ Restaura stock de productos eliminados
- ✅ Descuenta stock de productos nuevos
- ✅ Recalcula total
- ✅ Calcula diferencia

**Respuesta:**

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

- Pagó originalmente: $1250
- Ahora debe pagar: $1405
- Diferencia: +$155 (debe pagar extra)

#### Paso 2d: Pagar la diferencia

```bash
curl -X POST http://localhost:8000/pedidos/34/pagar-diferencia \
  -H "Content-Type: application/json" \
  -d '{"metodo_pago": "Efectivo"}'
```

**Respuesta:**

```json
{
  "status": "Pago de diferencia aprobado",
  "idPedido": 34,
  "total_pagado": 1405.0
}
```

#### Paso 2e (Alternativo): Cancelar pedido

```bash
curl -X DELETE http://localhost:8000/pedidos/34
```

**Lo que pasa:**

- ✅ Elimina el pedido
- ✅ Restaura TODO el stock

**Respuesta:**

```json
{
  "status": "Pedido #34 cancelado correctamente",
  "stock_restaurado": true
}
```

---

### FLUJO 3: Monitoreo de Pedidos en Cocina

#### Ver estado de pedidos

```bash
# Todos los confirmados (listos para cocina)
curl "http://localhost:8000/pedidos?estado=Confirmado"

# Que se envió a cocina
curl "http://localhost:8000/pedidos?estado=En%20preparaci%C3%B3n"

# Listos para retirar
curl "http://localhost:8000/pedidos?estado=Listo%20para%20entregar"
```

#### Cambiar estado de un pedido

```bash
# Paso 1: De Confirmado a En preparación
curl -X PATCH http://localhost:8000/pedidos/34/estado \
  -H "Content-Type: application/json" \
  -d '{"estado": "En preparación"}'
```

**En la consola:**

```
[Pantalla Monitor Local] Pedido #34 cambió de estado a -> [En preparación]
```

```bash
# Paso 2: De En preparación a Listo para entregar
curl -X PATCH http://localhost:8000/pedidos/34/estado \
  -H "Content-Type: application/json" \
  -d '{"estado": "Listo para entregar"}'
```

**En la consola:**

```
[Pantalla Monitor Local] Pedido #34 cambió de estado a -> [Listo para entregar]
```

---

## ⚠️ ERRORES COMUNES Y SOLUCIONES

### Error: "Stock insuficiente para Papas Cheddar. Disponible: 5"

**Causa:** Intentaste ordenar más de lo que hay.
**Solución:** Reduce la cantidad.

```bash
# ❌ NO funciona (hay solo 5)
{"idProducto": 1, "cantidad": 10}

# ✅ SÍ funciona
{"idProducto": 1, "cantidad": 3}
```

### Error: "No se puede editar un pedido en preparación"

**Causa:** El pedido ya está siendo preparado en cocina.
**Solución:** Solo puedes editar pedidos en estado "Confirmado".

```bash
# ❌ NO puedes editar (estado: "En preparación")
# ✅ SÍ puedes editar (estado: "Confirmado")
```

### Error: "Pedido no encontrado"

**Causa:** El ID del pedido no existe.
**Solución:** Verifica el ID primero.

```bash
curl http://localhost:8000/pedidos  # Ver todos
curl http://localhost:8000/pedidos/34  # Ver ese específicamente
```

### Error: "Port 8000 already in use"

**Causa:** Ya hay algo usando el puerto 8000.
**Solución:** Usa otro puerto.

```bash
uvicorn main:app --reload --port 8001
```

---

## 📖 DOCUMENTACIÓN ADICIONAL

### Para entender todo en detalle:

👉 **[GUIA_COMPLETA_API.md](GUIA_COMPLETA_API.md)**

### Para ver resumen de cambios:

👉 **[VALIDACION_CAMBIOS.md](VALIDACION_CAMBIOS.md)**

### Para arquitectura del proyecto:

👉 **[README.md](README.md)**

---

## 🧪 PRUEBA RÁPIDA (5 minutos)

```bash
# 1. Obtener productos
curl http://localhost:8000/productos | grep -i papas

# 2. Crear pedido
RESPONSE=$(curl -s -X POST http://localhost:8000/pedidos \
  -H "Content-Type: application/json" \
  -d '{"cliente":"Test","productos":[{"idProducto":1,"cantidad":1}]}')

echo $RESPONSE | grep idPedido

# 3. Extraer ID del pedido (ejemplo: 1)
ID=$(echo $RESPONSE | grep -o '"idPedido":[0-9]*' | cut -d: -f2)

# 4. Pagar
curl -X POST http://localhost:8000/pedidos/$ID/pagar \
  -H "Content-Type: application/json" \
  -d '{"metodo_pago":"Efectivo"}'

# 5. Ver resultado
curl http://localhost:8000/pedidos/$ID
```

---

## 🎛️ TRANSICIONES DE ESTADO VÁLIDAS

```
Creación
   ↓
SinAceptar (pedido creado, esperando pago)
   ↓ [POST /pagar - EXITOSO]
Confirmado (pago aprobado, listo para cocina)
   ↓ [PATCH /estado]
En preparación (preparando en cocina)
   ↓ [PATCH /estado]
Listo para entregar (listo para cliente)
```

---

## 💡 TIPS

✅ **Usa Swagger para probar:**
http://localhost:8000/docs

✅ **Verifica el monitor:**
Mira la consola para ver `[Pantalla Monitor Local]`

✅ **Stock se maneja automáticamente:**

- Crear pedido → descuenta
- Editar → restaura + descuenta
- Cancelar → devuelve todo

✅ **Totales siempre en backend:**
Nunca confíes en el cliente para calcular

✅ **Los JSONs se crean solos:**
No necesitas crearlos manualmente

---

## ✅ Checklist de Verificación

- [ ] Instalé pip install -r requirements.txt
- [ ] Ejecuté uvicorn main:app --reload
- [ ] Accedí a http://localhost:8000/docs
- [ ] Vi la documentación Swagger
- [ ] Probé GET /productos
- [ ] Probé crear un pedido
- [ ] Probé pagar un pedido
- [ ] Vi los prints de impresión en consola
- [ ] Probé editar un pedido
- [ ] Probé cambiar estado
- [ ] Leí [GUIA_COMPLETA_API.md](GUIA_COMPLETA_API.md)

---

## 🚀 ¡Listo para empezar!

```bash
cd "c:\Users\sebaf\Desktop\ADA ENTREGAS\UT6TFU"
pip install -r requirements.txt
uvicorn main:app --reload
```

Abre: http://localhost:8000/docs

¡Que lo disfrutes! 🍔

---

**Versión**: 1.0  
**Fecha**: 16/06/2026  
**Estado**: ✅ LISTO PARA USAR
