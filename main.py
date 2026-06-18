from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from domain import Estado
from repositories import ProductoRepository, PedidoRepository
from services import ProductoService, PedidoService, ImpresionService, PagoService, VisualizacionService

app = FastAPI(title="T&R Hamburguesería - API Backend")

# Orquestación de dependencias siguiendo SOLID
producto_repo = ProductoRepository()
pedido_repo = PedidoRepository(producto_repo=producto_repo)

producto_service = ProductoService(producto_repo)
pedido_service = PedidoService(pedido_repo, producto_repo)
impresion_service = ImpresionService(pedido_repo)
pago_service = PagoService()
visualizacion_service = VisualizacionService()


# ==================== MODELOS PYDANTIC ====================
class ItemPedidoInput(BaseModel):
    idProducto: int
    cantidad: int

class CrearPedidoInput(BaseModel):
    cliente: str
    productos: List[ItemPedidoInput]

class PagoInput(BaseModel):
    metodo_pago: str

class EditarPedidoInput(BaseModel):
    productos: List[ItemPedidoInput]

# ==================== ENDPOINTS PRODUCTOS ====================
@app.get("/productos")
def listar_productos(categoria: Optional[str] = Query(None, description="Filtrar por categoría: comida, bebida, postre")):
    """
    Obtiene el listado de productos del catálogo.
    Opcional: filtrar por categoría (comida, bebida, postre).
    """
    catalogo = producto_service.mostarCatalogo()
    
    if categoria:
        catalogo = [p for p in catalogo if p.categoria.lower() == categoria.lower()]
    
    return [
        {
            "idProducto": p.idProducto,
            "stock": p.stock,
            "descripcion": p.descripcion,
            "precio": p.precio,
            "categoria": p.categoria
        }
        for p in catalogo
    ]


# ==================== ENDPOINTS PEDIDOS ====================
@app.post("/pedidos", status_code=201)
def crear_pedido(input_data: CrearPedidoInput):
    """
    **PUC 1 - Paso 1 y 2**: Crear un nuevo pedido.
    El backend instancia automáticamente el Pedido, calcula totales y autogenera el ID.
    Descuenta automáticamente el stock de los productos.
    """
    try:
        items = [{"idProducto": item.idProducto, "cantidad": item.cantidad} for item in input_data.productos]
        nuevo_pedido = pedido_service.realizarPedido(input_data.cliente, items)
        
        return {
            "idPedido": nuevo_pedido.idPedido,
            "cliente": nuevo_pedido.cliente,
            "estado": nuevo_pedido.estado.value,
            "total": nuevo_pedido.total,
            "productos": [
                {
                    "idProducto": p.idProducto,
                    "descripcion": p.descripcion,
                    "cantidad": nuevo_pedido.obtenerCantidadProducto(p.idProducto),
                    "subtotal": p.precio * nuevo_pedido.obtenerCantidadProducto(p.idProducto)
                }
                for p in nuevo_pedido.listaProductos
            ]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/pedidos")
def consultar_pedidos(estado: Optional[Estado] = Query(None, description="Filtrar por estado: SinAceptar, Confirmado, En preparación, Listo para entregar")):
    """
    **PUC 2 - Paso 1**: Obtiene todos los pedidos o filtra por estado.
    Útil para la pantalla "Pedidos en curso" que muestra la grilla de estados.
    """
    if estado:
        pedidos = pedido_service.devolverPedidosEstado(estado)
    else:
        pedidos = pedido_repo.obtenerTodos()
    
    resultado = []
    for p in pedidos:
        resultado.append({
            "idPedido": p.idPedido,
            "cliente": p.cliente,
            "estado": p.estado.value,
            "total": p.total,
            "productos": [
                {"descripcion": prod.descripcion, "cantidad": p.obtenerCantidadProducto(prod.idProducto)}
                for prod in p.listaProductos
            ]
        })
    return resultado


@app.get("/pedidos/{id_pedido}")
def obtener_pedido_por_id(id_pedido: int):
    """
    Obtiene un pedido específico por su ID.
    """
    pedido = pedido_service.devolverPedido(id_pedido)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    return {
        "idPedido": pedido.idPedido,
        "cliente": pedido.cliente,
        "estado": pedido.estado.value,
        "total": pedido.total,
        "productos": [
            {"idProducto": p.idProducto, "descripcion": p.descripcion, "cantidad": pedido.obtenerCantidadProducto(p.idProducto)}
            for p in pedido.listaProductos
        ]
    }


@app.post("/pedidos/{id_pedido}/pagar")
def pagar_pedido(id_pedido: int, pago: PagoInput):
    """
    **PUC 1 - Paso 3, 4, 5 y 6**: Procesar pago e integración con POSNET.
    - Simula transacción en la pasarela
    - Si es exitoso: cambia estado a Confirmado
    - Dispara impresión de ticket fiscal y comanda
    """
    pedido = pedido_service.devolverPedido(id_pedido)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    # Procesar pago
    pago_exitoso = pago_service.procesarPago(pedido.idPedido, pedido.total)
    
    if pago_exitoso:
        # Cambiar estado a Confirmado
        pedido_service.cambiarEstado(pedido.idPedido, Estado.Confirmado)
        visualizacion_service.actualizarPantalla(pedido.idPedido, Estado.Confirmado)
        # Imprimir comprobantes
        impresion_service.enviarImprimirTicketPago(pedido.idPedido)
        impresion_service.enviarImprimirComanda(pedido.idPedido)
        
        return {
            "status": "Pago aprobado por POSNET",
            "idPedido": pedido.idPedido
        }
    else:
        raise HTTPException(status_code=400, detail="Transacción declinada")


@app.put("/pedidos/{id_pedido}")
def editar_pedido(id_pedido: int, input_data: EditarPedidoInput):
    """
    **PUC 2 - Paso 3**: Editar un pedido existente.
    - Recalcula el total
    - Devuelve la diferencia a pagar (positivo si debe más, negativo si recibe vuelto)
    - Solo permite editar pedidos en estado "Confirmado" pero no en "En preparación"
    """
    pedido = pedido_service.devolverPedido(id_pedido)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    # Validar que no esté en preparación
    if pedido.estado == Estado.EnPreparacion:
        raise HTTPException(status_code=400, detail="No se puede editar un pedido en preparación")
    
    total_anterior = pedido.total
    
    # Restaurar stock de productos removidos
    productos_copia = list(pedido.listaProductos)
    for prod in productos_copia:
        cant_anterior = pedido.obtenerCantidadProducto(prod.idProducto)
        prod.cambiarStock(cant_anterior)  # Devolver al stock
        producto_repo.ModificarProducto(prod)
        pedido.quitarProducto(prod, cant_anterior)
    
    # Aplicar nuevos productos y descontar stock
    for item in input_data.productos:
        prod = producto_repo.buscarPorId(item.idProducto)
        if prod:
            if prod.stock < item.cantidad:
                raise HTTPException(status_code=400, detail=f"Stock insuficiente para {prod.descripcion}")
            pedido.agregarProducto(prod, item.cantidad)
            prod.cambiarStock(-item.cantidad)
            producto_repo.ModificarProducto(prod)
    
    pedido_repo.agregarPedido(pedido)
    diferencia = pedido.total - total_anterior
    
    return {
        "idPedido": pedido.idPedido,
        "cliente": pedido.cliente,
        "total_anterior": total_anterior,
        "nuevo_total": pedido.total,
        "diferencia_a_pagar_en_caja": diferencia,
        "productos": [
            {"idProducto": p.idProducto, "descripcion": p.descripcion, "cantidad": pedido.obtenerCantidadProducto(p.idProducto)}
            for p in pedido.listaProductos
        ]
    }


@app.post("/pedidos/{id_pedido}/pagar-diferencia")
def pagar_diferencia_edicion(id_pedido: int, pago: PagoInput):
    """
    **PUC 2 - Paso 4, 5 y 6**: Pagar la diferencia luego de editar un pedido.
    - Procesa el pago solo de la diferencia (ya calculada en edición)
    - Si es exitoso, imprime nuevo ticket
    """
    pedido = pedido_service.devolverPedido(id_pedido)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    pago_exitoso = pago_service.procesarPago(pedido.idPedido, pedido.total)
    
    if pago_exitoso:
        impresion_service.enviarImprimirTicketPago(pedido.idPedido)
        return {
            "status": "Pago de diferencia aprobado",
            "idPedido": pedido.idPedido,
            "total_pagado": pedido.total
        }
    else:
        raise HTTPException(status_code=400, detail="Transacción declinada")


@app.patch("/pedidos/{id_pedido}/estado")
def actualizar_estado_cocina(id_pedido: int):
    """
    **PUC 2 - Paso 2 y Monitoreo**: Avanzar el estado de cocina de un pedido.
    Transiciones válidas:
    - Confirmado → En preparación
    - En preparación → Listo para entregar
    Actualiza automáticamente el monitor del local (VisualizacionService).
    """
    pedido = pedido_service.devolverPedido(id_pedido)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    try:
        nuevo_estado = pedido_service.avanzarEstadoCocina(id_pedido)
        visualizacion_service.actualizarPantalla(id_pedido, nuevo_estado)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {
        "idPedido": id_pedido,
        "nuevo_estado": nuevo_estado.value
    }


@app.delete("/pedidos/{id_pedido}")
def eliminar_pedido(id_pedido: int):
    """
    **PUC 2**: Cancelar un pedido existente.
    Elimina el pedido del repositorio y restaura el stock de sus productos.
    """
    pedido = pedido_service.devolverPedido(id_pedido)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    # Restaurar stock de todos los productos
    for prod in pedido.listaProductos:
        cant = pedido.obtenerCantidadProducto(prod.idProducto)
        prod.cambiarStock(cant)
        producto_repo.ModificarProducto(prod)
    
    pedido_service.cancelarPedido(id_pedido)
    
    return {
        "status": f"Pedido #{id_pedido} cancelado correctamente",
        "stock_restaurado": True
    }


# ==================== HEALTH CHECK ====================
@app.get("/health")
def health():
    """Verifica que la API esté funcionando"""
    return {"status": "API T&R Hamburguesería operativa"}
