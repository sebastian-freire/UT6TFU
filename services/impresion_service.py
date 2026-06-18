from repositories import PedidoRepository


class Impresora:
    def imprimir(self, texto: str) -> None:
        print(f"\n================ [IMPRESORA T&R] ================\n{texto}\n================================================\n")


class ImpresionService:
    def __init__(self, pedidoRepository: PedidoRepository):
        self.pedidoRepository = pedidoRepository
        self.impresora = Impresora()

    def enviarImprimirComanda(self, idPedido: int) -> None:
        pedido = self.pedidoRepository.buscarPorId(idPedido)
        if pedido:
            texto = f"--- COMANDA COCINA T&R ---\nPedido ID: #{pedido.idPedido}\nCliente: {pedido.cliente}\nItems:\n"
            for p in pedido.listaProductos:
                texto += f" * [ Cantidad: {pedido.obtenerCantidadProducto(p.idProducto)} ] -> {p.descripcion}\n"
            self.impresora.imprimir(texto)

    def enviarImprimirTicketPago(self, idPedido: int) -> None:
        pedido = self.pedidoRepository.buscarPorId(idPedido)
        if pedido:
            texto = f"--- TICKET FISCAL DE PAGO T&R ---\nPedido ID: #{pedido.idPedido}\nCliente: {pedido.cliente}\n"
            for p in pedido.listaProductos:
                cant = pedido.obtenerCantidadProducto(p.idProducto)
                texto += f" - {cant}x {p.descripcion} (${p.precio} c/u) = ${cant * p.precio}\n"
            texto += f"---------------------------------\nTOTAL: ${pedido.total}"
            self.impresora.imprimir(texto)
