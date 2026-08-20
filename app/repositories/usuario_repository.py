"""Repository Pattern: único punto de acceso a datos para Usuario."""
from app.models.usuario import Usuario


class UsuarioRepository:

    def obtener_por_id(self, usuario_id):
        return Usuario.query.get(int(usuario_id))

    def obtener_por_email(self, email):
        return Usuario.query.filter_by(email=email).first()

    def guardar(self, usuario):
        from app import db
        db.session.add(usuario)
        db.session.commit()
        return usuario

    def actualizar(self):
        from app import db
        db.session.commit()
