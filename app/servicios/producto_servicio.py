from fastapi import HTTPException
from app.repositorios.producto_repositorio import ProductoRepositorio
from app.modelos.producto import Producto, HistorialPrecio

class ProductoServicio:
    def __init__(self, repositorio: ProductoRepositorio):
        self.repositorio = repositorio

    def obtener_detalle(self, codigo: str) -> tuple[Producto, list[HistorialPrecio]]:
        producto = self.repositorio.obtener_por_codigo(codigo)
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        historial = self.repositorio.obtener_historial_precios(producto.id)
        return producto, historial

    def listar(self, nombre: str | None = None) -> list[tuple[Producto, list[HistorialPrecio]]]:
        if nombre:
            productos = self.repositorio.listar_por_nombre(nombre)
        else:
            productos = self.repositorio.listar_todos()
        resultado = []
        for prod in productos:
            historial = self.repositorio.obtener_historial_precios(prod.id)
            resultado.append((prod, historial))
        return resultado

    def listar_por_categoria(self, categoria: str) -> list[tuple[Producto, list[HistorialPrecio]]]:
        productos = self.repositorio.listar_por_categoria(categoria)
        return [(p, self.repositorio.obtener_historial_precios(p.id)) for p in productos]

    def listar_stock_bajo(self, umbral: int) -> list[tuple[Producto, list[HistorialPrecio]]]:
        productos = self.repositorio.listar_por_stock_menor(umbral)
        return [(p, self.repositorio.obtener_historial_precios(p.id)) for p in productos]

    def cambiar_precio(self, codigo: str, nuevo_valor: float) -> tuple[Producto, list[HistorialPrecio]]:
        producto = self.repositorio.obtener_por_codigo(codigo)
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        self.repositorio.actualizar_precio(producto, nuevo_valor)
        historial = self.repositorio.obtener_historial_precios(producto.id)
        return producto, historial
