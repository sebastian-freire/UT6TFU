from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entidades import Pedido, Producto


class PedidoRepository(ABC):
    @abstractmethod
    def buscarPorId(self, idPedido: int) -> Optional[Pedido]:
        raise NotImplementedError

    @abstractmethod
    def agregarPedido(self, pedido: Pedido) -> None:
        raise NotImplementedError

    @abstractmethod
    def eliminarPedido(self, pedido: Pedido) -> None:
        raise NotImplementedError

    @abstractmethod
    def obtenerFiltrado(self, estado) -> List[Pedido]:
        raise NotImplementedError

    @abstractmethod
    def obtenerTodos(self) -> List[Pedido]:
        raise NotImplementedError


class ProductoRepository(ABC):
    @abstractmethod
    def buscarPorId(self, idProducto: int) -> Optional[Producto]:
        raise NotImplementedError

    @abstractmethod
    def agregarProducto(self, producto: Producto) -> None:
        raise NotImplementedError

    @abstractmethod
    def ModificarProducto(self, producto: Producto) -> None:
        raise NotImplementedError

    @abstractmethod
    def obtenerTodosProductos(self) -> List[Producto]:
        raise NotImplementedError
