"""Repository Pattern: único punto de acceso a datos para Caso."""
from app.models.caso import Caso


class CasoRepository:

    def obtener_por_id(self, caso_id):
        return Caso.query.get_or_404(caso_id)

    def obtener_por_numero_expediente(self, numero_expediente):
        return Caso.query.filter_by(numero_expediente=numero_expediente).first()

    def listar_por_usuario(self, usuario_id):
        return (
            Caso.query.filter_by(usuario_id=usuario_id)
            .order_by(Caso.fecha_creacion.desc())
            .all()
        )

    def guardar(self, caso):
        from app import db
        db.session.add(caso)
        db.session.commit()
        return caso

    def actualizar(self):
        from app import db
        db.session.commit()
