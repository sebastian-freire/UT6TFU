from typing import List

from domain import Estado, Pedido
from repositories import PedidoRepository, ProductoRepository

class PedidoService:
    def __init__(self, pedidoRepository: PedidoRepository, productoRepository: ProductoRepository):
        self.pedidoRepository = pedidoRepository
        self.productoRepository = productoRepository

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
                # Descontar stock automaticamente
                prod.cambiarStock(-item["cantidad"])
                self.productoRepository.ModificarProducto(prod)

        self.pedidoRepository.agregarPedido(nuevo_pedido)
        return nuevo_pedido

    def cambiarEstado(self, idPedido: int, estado: Estado) -> None:
        pedido = self.pedidoRepository.buscarPorId(idPedido)
        if pedido:
            pedido.cambiarEstado(estado)
            self.pedidoRepository.agregarPedido(pedido)

    def avanzarEstadoCocina(self, idPedido: int) -> Estado:
        pedido = self.pedidoRepository.buscarPorId(idPedido)
        if not pedido:
            raise ValueError("Pedido no encontrado")

        transiciones = {
            Estado.Confirmado: Estado.EnPreparacion,
            Estado.EnPreparacion: Estado.ListoParaEntregar,
        }

        if pedido.estado not in transiciones:
            raise ValueError(f"No se puede avanzar el pedido desde el estado {pedido.estado.value}")

        nuevo_estado = transiciones[pedido.estado]
        pedido.cambiarEstado(nuevo_estado)
        self.pedidoRepository.agregarPedido(pedido)
        return nuevo_estado

    def cancelarPedido(self, idPedido: int) -> None:
        pedido = self.pedidoRepository.buscarPorId(idPedido)
        if pedido:
            self.pedidoRepository.eliminarPedido(pedido)

    def devolverPedido(self, idPedido: int) -> Pedido:
        return self.pedidoRepository.buscarPorId(idPedido)

    def devolverPedidosEstado(self, estado: Estado) -> List[Pedido]:
        return self.pedidoRepository.obtenerFiltrado(estado)
