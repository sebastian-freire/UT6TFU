# 🍔 T&R Hamburguesería - API REST Backend

## Descripción

API REST completa que implementa los 2 **Procesos de Uso Críticos (PUCs)** del sistema de gestión de pedidos T&R:

- **PUC 1**: Registro de pedido (el corazón del negocio)
- **PUC 2**: Modificación de pedido

## ✅ Características Principales

### Gestión de Catálogo

- ✅ Productos organizados por categoría (Comida, Bebidas, Postres)
- ✅ Control automático de stock
- ✅ Filtrado por categoría en API

### Registro de Pedidos (PUC 1)

- ✅ Creación automática de pedidos con ID correlativo
- ✅ Descuento automático de stock
- ✅ Cálculo de totales en backend (responsabilidad del servidor)
- ✅ Integración con POSNET (simulada)
- ✅ Impresión de ticket fiscal y comanda

### Modificación de Pedidos (PUC 2)

- ✅ Edición de cantidades
- ✅ Agregar/quitar productos
- ✅ Cálculo de diferencia a pagar
- ✅ Restauración automática de stock
- ✅ Validación: no permite editar si está en preparación

### Monitoreo

- ✅ Filtrado de pedidos por estado
- ✅ Cambio de estado: Confirmado → En preparación → Listo para entregar
- ✅ Monitor visual del local (SistemaVisualizacion)

## 📁 Estructura del Proyecto

```
├── main.py                      # Endpoints FastAPI (completamente reescrito)
├── requirements.txt             # Dependencias Python
├── README.md                    # Este archivo
├── GUIA_COMPLETA_API.md         # 📚 Documentación detallada (LEER ESTO)
│
├── domain/
│   ├── __init__.py
│   ├── entidades.py            # Producto (con categoría), Pedido, Estado
│   └── interfaces.py           # Interfaces de repositorios
│
├── repositories/
│   ├── __init__.py
│   └── json_repository.py      # Persistencia en JSON (actualizado)
│
├── services/
│   ├── __init__.py
│   ├── service.py              # Lógica de servicios (pedidos, productos, pagos)
│   └── sistema_pagos.py        # Simula POSNET
│
├── productos.json              # Catálogo (auto-generado con categorías)
└── pedidos.json               # Pedidos (auto-generado vacío)
```

## 🚀 Instalación y Ejecución

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

**requirements.txt contiene:**

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
- **Health Check**: http://localhost:8000/health

## 🎯 Quick Start

### Ver todos los productos

```bash
curl http://localhost:8000/productos
```

### Ver solo productos de una categoría

```bash
curl "http://localhost:8000/productos?categoria=Comida"
curl "http://localhost:8000/productos?categoria=Bebidas"
curl "http://localhost:8000/productos?categoria=Postres"
```

### Crear un pedido (PUC 1)

```bash
curl -X POST http://localhost:8000/pedidos \
  -H "Content-Type: application/json" \
  -d '{
    "cliente": "Juan",
    "productos": [
      {"idProducto": 3, "cantidad": 1},
      {"idProducto": 2, "cantidad": 1}
    ]
  }'
```

### Pagar un pedido

```bash
curl -X POST http://localhost:8000/pedidos/1/pagar \
  -H "Content-Type: application/json" \
  -d '{"metodo_pago": "Efectivo"}'
```

### Ver pedidos en curso

```bash
curl http://localhost:8000/pedidos
```

### Filtrar por estado

```bash
curl "http://localhost:8000/pedidos?estado=Confirmado"
curl "http://localhost:8000/pedidos?estado=En%20preparaci%C3%B3n"
```

### Editar un pedido (PUC 2)

```bash
curl -X PUT http://localhost:8000/pedidos/1 \
  -H "Content-Type: application/json" \
  -d '{
    "productos": [
      {"idProducto": 3, "cantidad": 2},
      {"idProducto": 5, "cantidad": 1}
    ]
  }'
```

### Cambiar estado del pedido

```bash
curl -X PATCH http://localhost:8000/pedidos/1/estado \
  -H "Content-Type: application/json" \
  -d '{"estado": "En preparación"}'
```

## 📊 Endpoints Disponibles

| Método | Endpoint                         | Descripción                            | PUC       |
| ------ | -------------------------------- | -------------------------------------- | --------- |
| GET    | `/productos`                     | Listar catálogo (con filtro opcional)  | Catálogo  |
| POST   | `/pedidos`                       | Crear pedido                           | **PUC 1** |
| GET    | `/pedidos`                       | Listar pedidos (con filtro por estado) | Monitoreo |
| GET    | `/pedidos/{id}`                  | Obtener pedido específico              | -         |
| POST   | `/pedidos/{id}/pagar`            | Procesar pago                          | **PUC 1** |
| PUT    | `/pedidos/{id}`                  | Editar pedido                          | **PUC 2** |
| POST   | `/pedidos/{id}/pagar-diferencia` | Pagar diferencia                       | **PUC 2** |
| PATCH  | `/pedidos/{id}/estado`           | Cambiar estado                         | Monitoreo |
| DELETE | `/pedidos/{id}`                  | Cancelar pedido                        | **PUC 2** |
| GET    | `/health`                        | Health check                           | -         |

## 🎛️ Estados de Pedido

```
SinAceptar
    ↓
Confirmado  (después de pago exitoso)
    ↓
En preparación  (personal de cocina)
    ↓
Listo para entregar
```

## 🔐 Validaciones Críticas

El backend valida automáticamente:

- ✅ Stock disponible (rechaza si no hay)
- ✅ Edición solo en Confirmado (rechaza si está En preparación)
- ✅ Existencia de productos
- ✅ Formatos de entrada (Pydantic)
- ✅ Transiciones válidas de estado

## 📚 DOCUMENTACIÓN COMPLETA

### ⭐ **IMPORTANTE**: Leer [GUIA_COMPLETA_API.md](GUIA_COMPLETA_API.md)

Contiene:

- Arquitectura detallada
- Flujos completos PUC 1 y PUC 2 (paso a paso)
- Ejemplos con curl para cada caso
- Manejo de errores
- Troubleshooting
- Gestión de stock
- Y mucho más...

## 🛠️ Cambios Realizados

### En `domain/entidades.py`

- ✅ Agregado campo `categoria: str` a clase `Producto`

### En `repositories/json_repository.py`

- ✅ Actualizado para manejar categorías en productos
- ✅ Agregados productos postres al catálogo inicial
- ✅ Todos los métodos actualizados

### En `services/service.py`

- ✅ **INTEGRADO**: Descuento automático de stock al crear pedido
- ✅ **INTEGRADO**: Restauración de stock al editar/cancelar

### En `main.py` (COMPLETA REESCRITURA)

- ✅ Filtro por categoría en `/productos`
- ✅ Manejo de errores de stock
- ✅ Mejor estructura de respuestas
- ✅ Documentación en docstrings
- ✅ Estado en body de PATCH (no en query)
- ✅ Nuevo endpoint para pagar diferencia
- ✅ Restauración de stock en cancelación
- ✅ Health check endpoint

## 🏗️ Principios de Diseño

✅ **SOLID**

- Single Responsibility: cada clase tiene una responsabilidad
- Dependency Inversion: depende de abstracciones

✅ **Separación de Capas**

- **Domain**: Entidades y interfaces (sin dependencias externas)
- **Service**: Lógica de negocio (orquesta domain + repository)
- **Repository**: Acceso a datos (implementa interfaces)
- **API**: Endpoints REST (consume servicios)

✅ **DTOs**

- Pydantic Models para entrada/salida
- Separación entre API y lógica interna

✅ **Testing Friendly**

- Fácil de probar con inyección de dependencias
- Repositorio intercambiable (JSON → DB)

## 💾 Datos

### productos.json (auto-generado)

```json
[
  {"idProducto": 1, "stock": 50, "descripcion": "Papas Cheddar", "precio": 270.0, "categoria": "Comida"},
  {"idProducto": 2, "stock": 100, "descripcion": "Coca Cola Zero", "precio": 240.0, "categoria": "Bebidas"},
  ...
]
```

### pedidos.json (auto-generado)

```json
[
  {
    "idPedido": 34,
    "cliente": "Juani",
    "estado": "Confirmado",
    "total": 1250.0,
    "cantidades": { "1": 1, "2": 2, "3": 1, "4": 1 }
  }
]
```

## 🔍 Tecnologías Usadas

- **FastAPI** - Framework web async de alta performance
- **Uvicorn** - Servidor ASGI
- **Pydantic** - Validación de datos con type hints
- **Python 3.7+** - Lenguaje

## 📈 Próximas Mejoras

- [ ] Agregar autenticación JWT
- [ ] Migrar a base de datos (SQLite/PostgreSQL)
- [ ] Auditoría de cambios (quién, cuándo, qué)
- [ ] WebSockets para actualizaciones en tiempo real
- [ ] Reportes y estadísticas
- [ ] Caché de productos

## ❓ Troubleshooting

| Problema                                         | Solución                                    |
| ------------------------------------------------ | ------------------------------------------- |
| `ModuleNotFoundError: No module named 'fastapi'` | Ejecutar: `pip install -r requirements.txt` |
| `Port 8000 already in use`                       | Cambiar puerto: `--port 8001`               |
| `Stock insuficiente`                             | Reducer cantidad o esperar a que se reponga |
| `Pedido no encontrado`                           | Verificar ID con `GET /pedidos`             |
| `No se puede editar en preparación`              | Solo edita Confirmado (no En preparación)   |

## 📞 Soporte

Para más información:

- Leer [GUIA_COMPLETA_API.md](GUIA_COMPLETA_API.md)
- Probar en Swagger: http://localhost:8000/docs
- Revisar docstrings de endpoints

---

**Versión**: 1.0  
**Fecha**: Junio 2026  
**Estado**: ✅ Production Ready

**Hecho con ❤️ para T&R Hamburguesería**
