from services.sistema_pagos import SistemaDePagos


class PagoService:
    def __init__(self, sistemaPagos: SistemaDePagos = None):
        self.sistemaPagos = sistemaPagos or SistemaDePagos()

    def procesarPago(self, idPedido: int, monto: float) -> bool:
        return self.sistemaPagos.procesarPago(idPedido, monto)
