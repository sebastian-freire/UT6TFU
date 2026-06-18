from typing import List

from domain import Producto
from repositories import ProductoRepository

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
