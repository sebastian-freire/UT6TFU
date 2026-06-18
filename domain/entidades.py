from enum import Enum
from typing import List

class Estado(str, Enum):
    SinAceptar = "SinAceptar"
    Confirmado = "Confirmado"
    EnPreparacion = "En preparación"
    ListoParaEntregar = "Listo para entregar"

class Producto:
    def __init__(self, idProducto: int, stock: int, descripcion: str, precio: float, categoria: str = "comida"):
        self.idProducto: int = idProducto
        self.stock: int = stock
        self.descripcion: str = descripcion
        self.precio: float = precio
        self.categoria: str = categoria

    def cambiarStock(self, cantidad: int) -> None:
        self.stock += cantidad

class Pedido:
    def __init__(self, idPedido: int, cliente: str = ""):
        self.idPedido: int = idPedido
        self.cliente: str = cliente 
        self.estado: Estado = Estado.SinAceptar
        self.total: float = 0.0
        self.listaProductos: List[Producto] = []
        self._cantidades = {}

    def cambiarEstado(self, estado: Estado) -> None:
        self.estado = estado

    def devolverEstado(self) -> Estado:
        return self.estado

    def obtenerCantidadProducto(self, idProducto: int) -> int:
        return self._cantidades.get(idProducto, 0)

    def obtenerCantidades(self) -> dict:
        return self._cantidades.copy()

    def agregarProducto(self, producto: Producto, cantidad: int) -> None:
        if producto.idProducto in self._cantidades:
            self._cantidades[producto.idProducto] += cantidad
        else:
            self._cantidades[producto.idProducto] = cantidad
            self.listaProductos.append(producto)
        self.calcularTotal()

    def quitarProducto(self, producto: Producto, cantidad: int) -> None:
        if producto.idProducto in self._cantidades:
            self._cantidades[producto.idProducto] -= cantidad
            if self._cantidades[producto.idProducto] <= 0:
                if producto.idProducto in self._cantidades:
                    del self._cantidades[producto.idProducto]
                self.listaProductos = [p for p in self.listaProductos if p.idProducto != producto.idProducto]
        self.calcularTotal()

    def calcularTotal(self) -> float:
        self.total = sum(p.precio * self._cantidades[p.idProducto] for p in self.listaProductos)
        return self.total
