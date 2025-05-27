from datetime import datetime
from sqlalchemy.orm import Session
from app.modelos.producto import Producto, HistorialPrecio

class ProductoRepositorio:
    def __init__(self, db: Session):
        self.db = db

    def obtener_por_codigo(self, codigo: str) -> Producto | None:
        return (
            self.db
            .query(Producto)
            .filter(Producto.codigo == codigo)
            .first()
        )

    def listar_todos(self) -> list[Producto]:
        return self.db.query(Producto).all()

    def listar_por_nombre(self, nombre: str) -> list[Producto]:
        return (
            self.db
            .query(Producto)
            .filter(Producto.nombre.ilike(f"%{nombre}%"))
            .all()
        )

    def listar_por_categoria(self, categoria: str) -> list[Producto]:
        return (
            self.db
            .query(Producto)
            .filter(Producto.categoria == categoria)
            .all()
        )

    def listar_por_stock_menor(self, umbral: int) -> list[Producto]:
        return (
            self.db
            .query(Producto)
            .filter(Producto.stock < umbral)
            .all()
        )

    def obtener_historial_precios(self, producto_id: int) -> list[HistorialPrecio]:
        return (
            self.db
            .query(HistorialPrecio)
            .filter(HistorialPrecio.producto_id == producto_id)
            .order_by(HistorialPrecio.fecha.desc())
            .all()
        )

    def actualizar_precio(self, producto: Producto, nuevo_valor: float) -> None:
        # Actualiza el precio vigente
        producto.precio = nuevo_valor
        self.db.add(producto)
        # Registra en historial
        registro = HistorialPrecio(producto_id=producto.id, valor=nuevo_valor)
        self.db.add(registro)
        self.db.commit()

    def crear(self, codigo, marca, nombre, categoria, stock, precio):
        nuevo = Producto(
            codigo=codigo,
            marca=marca,
            nombre=nombre,
            categoria=categoria,
            stock=stock,
            precio=precio
        )
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)

        historial = HistorialPrecio(
            producto_id=nuevo.id,
            fecha=datetime.now(),
            valor=precio
        )
        self.db.add(historial)
        self.db.commit()

        return nuevo

    def obtener_historial(self, codigo):
        return (
            self.db.query(HistorialPrecio)
            .join(Producto)
            .filter(Producto.codigo == codigo)
            .order_by(HistorialPrecio.fecha.desc())
            .all()
        )