import json
import os
from typing import List
from domain import Pedido, Producto, Estado
from domain.interfaces import PedidoRepository as PedidoRepositoryBase, ProductoRepository as ProductoRepositoryBase

class ProductoRepository(ProductoRepositoryBase):
    def __init__(self, filepath: str = "productos.json"):
        self.filepath = filepath
        self._inicializar_datos_prueba()

    def _inicializar_datos_prueba(self):
        """Pre-carga el catálogo real que diseñaron en el prototipo de la UT4 con categorías"""
        if not os.path.exists(self.filepath):
            productos_iniciales = [
                {"idProducto": 1, "stock": 50, "descripcion": "Papas Cheddar", "precio": 270.0, "categoria": "comida"},
                {"idProducto": 2, "stock": 100, "descripcion": "Coca Cola Zero", "precio": 240.0, "categoria": "bebida"},
                {"idProducto": 3, "stock": 30, "descripcion": "Power Burger", "precio": 380.0, "categoria": "comida"},
                {"idProducto": 4, "stock": 30, "descripcion": "Veggie Burger", "precio": 350.0, "categoria": "comida"},
                {"idProducto": 5, "stock": 25, "descripcion": "The Pickle", "precio": 380.0, "categoria": "comida"},
                {"idProducto": 6, "stock": 25, "descripcion": "Onion Burger", "precio": 390.0, "categoria": "comida"},
                {"idProducto": 7, "stock": 25, "descripcion": "Crunch Burger", "precio": 390.0, "categoria": "comida"},
                {"idProducto": 8, "stock": 25, "descripcion": "Moonwalk Burger", "precio": 390.0, "categoria": "comida"},
                {"idProducto": 9, "stock": 40, "descripcion": "Flan", "precio": 150.0, "categoria": "postre"},
                {"idProducto": 10, "stock": 35, "descripcion": "Tiramisú", "precio": 180.0, "categoria": "postre"}
            ]
            self._guardar_todos(productos_iniciales)

    def _leer_todos(self) -> list:
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _guardar_todos(self, data: list) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def buscarPorId(self, idProducto: int) -> Producto:
        for p in self._leer_todos():
            if p["idProducto"] == idProducto:
                return Producto(p["idProducto"], p["stock"], p["descripcion"], p["precio"], p.get("categoria", "comida"))
        return None

    def agregarProducto(self, producto: Producto) -> None:
        data = self._leer_todos()
        data.append({
            "idProducto": producto.idProducto,
            "stock": producto.stock,
            "descripcion": producto.descripcion,
            "precio": producto.precio,
            "categoria": producto.categoria
        })
        self._guardar_todos(data)

    def ModificarProducto(self, producto: Producto) -> None:
        data = self._leer_todos()
        for p in data:
            if p["idProducto"] == producto.idProducto:
                p["stock"] = producto.stock
                p["descripcion"] = producto.descripcion
                p["precio"] = producto.precio
                p["categoria"] = producto.categoria
                break
        self._guardar_todos(data)

    def obtenerTodosProductos(self) -> List[Producto]:
        return [Producto(p["idProducto"], p["stock"], p["descripcion"], p["precio"], p.get("categoria", "comida")) for p in self._leer_todos()]


class PedidoRepository(PedidoRepositoryBase):
    def __init__(self, filepath: str = "pedidos.json", producto_repo: ProductoRepository = None):
        self.filepath = filepath
        self.producto_repo = producto_repo
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _leer_todos(self) -> list:
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _guardar_todos(self, data: list) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def buscarPorId(self, idPedido: int) -> Pedido:
        for p_dict in self._leer_todos():
            if p_dict["idPedido"] == idPedido:
                pedido = Pedido(p_dict["idPedido"], p_dict.get("cliente", ""))
                pedido.estado = Estado(p_dict["estado"])
                pedido.total = p_dict["total"]
                for prod_id_str, cant in p_dict["cantidades"].items():
                    prod = self.producto_repo.buscarPorId(int(prod_id_str))
                    if prod:
                        pedido.agregarProducto(prod, cant)
                return pedido
        return None

    def agregarPedido(self, pedido: Pedido) -> None:
        data = self._leer_todos()
        data = [p for p in data if p["idPedido"] != pedido.idPedido]  # Simula reemplazo/upsert
        data.append({
            "idPedido": pedido.idPedido,
            "cliente": pedido.cliente,
            "estado": pedido.estado.value,
            "total": pedido.total,
            "cantidades": pedido.obtenerCantidades()
        })
        self._guardar_todos(data)

    def eliminarPedido(self, pedido: Pedido) -> None:
        data = self._leer_todos()
        data = [p for p in data if p["idPedido"] != pedido.idPedido]
        self._guardar_todos(data)

    def obtenerFiltrado(self, estado: Estado) -> List[Pedido]:
        filtrados = []
        for p_dict in self._leer_todos():
            if p_dict["estado"] == estado.value:
                p = self.buscarPorId(p_dict["idPedido"])
                if p:
                    filtrados.append(p)
        return filtrados

    def obtenerTodos(self) -> List[Pedido]:
        lista = []
        for p_dict in self._leer_todos():
            p = self.buscarPorId(p_dict["idPedido"])
            if p:
                lista.append(p)
        return lista
