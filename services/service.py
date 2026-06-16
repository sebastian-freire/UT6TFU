from typing import List

from domain import Estado, Pedido, Producto
from repositories import PedidoRepository, ProductoRepository

from services.sistema_pagos import SistemaDePagos

class Impresora:
    def imprimir(self, texto: str) -> None:
        print(f"\n================ [IMPRESORA T&R] ================\n{texto}\n================================================\n")


class SistemaVisualizacion:
    def actualizarPantalla(self, idPedido: int, estado: Estado) -> None:
        print(f"[Pantalla Monitor Local] Pedido #{idPedido} cambió de estado a -> [{estado.value}]")


class ProductoService:
    def __init__(self, productoRepository: ProductoRepository):
        self.productoRepository = productoRepository

    def registrarProducto(self, stockInicial: int, descripcion: str, precio: float) -> Producto:
        productos = self.productoRepository.obtenerTodosProductos()
        nuevo_id = max([p.idProducto for p in productos], default=0) + 1
        nuevo_prod = Producto(nuevo_id, stockInicial, descripcion, precio)
        self.productoRepository.agregarProducto(nuevo_prod)
        return nuevo_prod

    def cambiarStock(self, idProducto: int, cantidad: int) -> None:
        prod = self.productoRepository.buscarPorId(idProducto)
        if prod:
            prod.cambiarStock(cantidad)
            self.productoRepository.ModificarProducto(prod)

    def mostarCatalogo(self) -> List[Producto]:
        return self.productoRepository.obtenerTodosProductos()


class PedidoService:
    def __init__(self, pedidoRepository: PedidoRepository, productoRepository: ProductoRepository):
        self.pedidoRepository = pedidoRepository
        self.productoRepository = productoRepository
        self.sistemaPagos = SistemaDePagos()
        self.impresora = Impresora()
        self.visualizacion = SistemaVisualizacion()

    def realizarPedido(self, cliente: str, productos_cantidades: List[dict]) -> Pedido:
        todos = self.pedidoRepository.obtenerTodos()
        nuevo_id = max([p.idPedido for p in todos], default=0) + 1
        
        nuevo_pedido = Pedido(nuevo_id, cliente)
        for item in productos_cantidades:
            prod = self.productoRepository.buscarPorId(item["idProducto"])
            if prod:
                # Validar stock disponible
                if prod.stock < item["cantidad"]:
                    raise ValueError(f"Stock insuficiente para {prod.descripcion}. Disponible: {prod.stock}")
                nuevo_pedido.agregarProducto(prod, item["cantidad"])
                # Descontar stock automáticamente
                prod.cambiarStock(-item["cantidad"])
                self.productoRepository.ModificarProducto(prod)
        
        self.pedidoRepository.agregarPedido(nuevo_pedido)
        return nuevo_pedido

    def cambiarEstado(self, idPedido: int, estado: Estado) -> None:
        pedido = self.pedidoRepository.buscarPorId(idPedido)
        if pedido:
            pedido.cambiarEstado(estado)
            self.pedidoRepository.agregarPedido(pedido)
            self.visualizacion.actualizarPantalla(idPedido, estado)

    def cancelarPedido(self, idPedido: int) -> None:
        pedido = self.pedidoRepository.buscarPorId(idPedido)
        if pedido:
            self.pedidoRepository.eliminarPedido(pedido)

    def devolverPedido(self, idPedido: int) -> Pedido:
        return self.pedidoRepository.buscarPorId(idPedido)

    def devolverPedidosEstado(self, estado: Estado) -> List[Pedido]:
        return self.pedidoRepository.obtenerFiltrado(estado)

    def enviarImprimirComanda(self, idPedido: int) -> None:
        pedido = self.pedidoRepository.buscarPorId(idPedido)
        if pedido:
            texto = f"--- COMANDA COCINA T&R ---\nPedido ID: #{pedido.idPedido}\nCliente: {pedido.cliente}\nItems:\n"
            for p in pedido.listaProductos:
                texto += f" * [ Cantidad: {pedido._cantidades[p.idProducto]} ] -> {p.descripcion}\n"
            self.impresora.imprimir(texto)

    def enviarImprimirTicketPago(self, idPedido: int) -> None:
        pedido = self.pedidoRepository.buscarPorId(idPedido)
        if pedido:
            texto = f"--- TICKET FISCAL DE PAGO T&R ---\nPedido ID: #{pedido.idPedido}\nCliente: {pedido.cliente}\n"
            for p in pedido.listaProductos:
                cant = pedido._cantidades[p.idProducto]
                texto += f" - {cant}x {p.descripcion} (${p.precio} c/u) = ${cant * p.precio}\n"
            texto += f"---------------------------------\nTOTAL: ${pedido.total}"
            self.impresora.imprimir(texto)
