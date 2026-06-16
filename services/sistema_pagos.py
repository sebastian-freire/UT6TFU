class SistemaDePagos:
    def procesarPago(self, idPedido: int, monto: float) -> bool:
        print(f"[Pasarela POSNET externo] Procesando cobro del pedido #{idPedido} por un monto de ${monto}")
        return True