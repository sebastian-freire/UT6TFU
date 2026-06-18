from domain import Estado

class VisualizacionService:
    def actualizarPantalla(self, idPedido: int, estado: Estado) -> None:
        print(f"[Pantalla Monitor Local] Pedido #{idPedido} cambio de estado a -> [{estado.value}]")
