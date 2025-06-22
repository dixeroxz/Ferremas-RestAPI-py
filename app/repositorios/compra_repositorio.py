from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from app.modelos.detalle_compras import DetalleCompras
from app.modelos.compra import Compra
from app.modelos.producto import Producto


class CompraRepositorio:
    def __init__(self, db: Session):
        self.db = db
     
    def crear_compra_pendiente(self, usuario_id: int, productos: list[dict], total: float) -> Compra:
        compra = Compra(
            usuario_id=usuario_id,
            total=total,
            fecha=datetime.utcnow(),
            estado="pendiente"
          )
        self.db.add(compra)
        self.db.commit()
        self.db.refresh(compra)
                  
        for item in productos:
            producto = self.db.query(Producto).filter(Producto.codigo == item["codigo"]).first()
            if producto:
                detalle = DetalleCompras(
                    compra_id=compra.id,
                    producto_codigo=producto.codigo,
                    cantidad=item["cantidad"],
                    precio_unitario=producto.precio)
                self.db.add(detalle)
         
        self.db.commit()
        return compra
          
    def eliminar_compra(self, compra_id: int) -> bool:
        compra = self.db.query(Compra).filter(Compra.id == compra_id).first()
        if not compra:
         return False
        self.db.delete(compra)  # elimina también los detalles
        self.db.commit()
        return True
      
    def obtener_compra(self, compra_id: int) -> Compra:
        return self.db.query(Compra).filter(Compra.id == compra_id).first()
     
    def listar_compras(self) -> list[Compra]:
        return self.db.query(Compra).all()
         
    def confirmar_compra(self, compra_id: int) -> Compra:
        compra = self.db.query(Compra).filter(Compra.id == compra_id).first()
        if not compra:
            return None
        compra.estado = "aprobado"
        self.db.commit()
        self.db.refresh(compra)
        return compra
     
    def cancelar_compra(self, compra_id: int) -> Compra:
        compra = self.db.query(Compra).filter(Compra.id == compra_id).first()
        if not compra:
            return None
        compra.estado = "rechazado"
        self.db.commit()
        self.db.refresh(compra)
        return compra
    
    def obtener_ultima_compra_usuario(self, usuario_id: int) -> Compra:
        """Obtiene la última compra de un usuario con todos sus detalles"""
        compra = (self.db.query(Compra)
                  .options(joinedload(Compra.detalles).joinedload(DetalleCompras.producto))
                  .filter(Compra.usuario_id == usuario_id)
                  .order_by(Compra.fecha.desc())
                  .first())
        
        return compra