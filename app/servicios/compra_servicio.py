from sqlalchemy.orm import Session
from app.repositorios.compra_repositorio import CompraRepositorio
from app.modelos.compra import Compra
from typing import List


class CompraServicio:
    def __init__(self, db: Session):
        self.repositorio = CompraRepositorio(db)
    
    def crear_compra_con_detalles(self, usuario_id: int, productos: List[dict], total: float) -> Compra:
        # Paso 1: Crear compra pendiente
        compra = self.repositorio.crear_compra_pendiente(usuario_id=usuario_id, productos=productos, total=total)
        
        # Paso 2: Agregar productos como detalle de compra
        self.repositorio.agregar_detalles_a_compra(compra.id, productos)
        
        # Paso 3: Retornar compra creada
        return compra
    
    def confirmar_compra(self, compra_id: int) -> Compra:
        return self.repositorio.confirmar_compra(compra_id)
    
    def cancelar_compra(self, compra_id: int) -> Compra:
        return self.repositorio.cancelar_compra(compra_id)
    
    def obtener_compra(self, compra_id: int) -> Compra:
        return self.repositorio.obtener_compra(compra_id)
    
    def listar_compras(self) -> List[Compra]:
        return self.repositorio.listar_compras()
    
    def listar_compras_por_usuario(self, usuario_id: int) -> List[Compra]:
        """Lista todas las compras de un usuario específico con detalles"""
        return self.repositorio.listar_compras_por_usuario(usuario_id)
        
    def obtener_ultima_compra_usuario_con_detalles(self, usuario_id: int) -> Compra:
        """Obtiene la última compra del usuario con todos los detalles"""
        return self.repositorio.obtener_ultima_compra_usuario(usuario_id)