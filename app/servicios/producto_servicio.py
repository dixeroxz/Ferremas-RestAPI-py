from fastapi import HTTPException
from app.repositorios.producto_repositorio import ProductoRepositorio
from app.modelos.producto import Producto, HistorialPrecio

class ProductoServicio:
    def __init__(self, repositorio: ProductoRepositorio):
        self.repo = repositorio

    def crear_producto(
        self,
        codigo: str,
        marca: str,
        nombre: str,
        categoria: str,
        stock: int,
        precio: float
    ):
        # Crear el producto
        nuevo_producto = self.repo.crear(codigo, marca, nombre, categoria, stock, precio)

        # Obtener historial actualizado
        historial = self.repo.obtener_historial(nuevo_producto.codigo)

        return nuevo_producto, historial

    def obtener_detalle(self, codigo: str) -> tuple[Producto, list[HistorialPrecio]]:
        producto = self.repo.obtener_por_codigo(codigo)
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        historial = self.repo.obtener_historial_precios(producto.id)
        return producto, historial

    def listar(self, nombre: str | None = None) -> list[tuple[Producto, list[HistorialPrecio]]]:
        if nombre:
            productos = self.repo.listar_por_nombre(nombre)
        else:
            productos = self.repo.listar_todos()
        resultado = []
        for prod in productos:
            historial = self.repo.obtener_historial_precios(prod.id)
            resultado.append((prod, historial))
        return resultado

    def listar_por_categoria(self, categoria: str) -> list[tuple[Producto, list[HistorialPrecio]]]:
        productos = self.repo.listar_por_categoria(categoria)
        return [(p, self.repo.obtener_historial_precios(p.id)) for p in productos]

    def listar_stock_bajo(self, umbral: int) -> list[tuple[Producto, list[HistorialPrecio]]]:
        productos = self.repo.listar_por_stock_menor(umbral)
        return [(p, self.repo.obtener_historial_precios(p.id)) for p in productos]

    def cambiar_precio(self, codigo: str, nuevo_valor: float) -> tuple[Producto, list[HistorialPrecio]]:
        producto = self.repo.obtener_por_codigo(codigo)
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        self.repo.actualizar_precio(producto, nuevo_valor)
        historial = self.repo.obtener_historial_precios(producto.id)
        return producto, historial

    def borrar_producto(self, codigo: str) -> None:
            """
            Lanza HTTPException 404 si el producto no existe,
            sino borra y retorna None.
            """
            ok = self.repo.eliminar_por_codigo(codigo)
            if not ok:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
