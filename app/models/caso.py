from datetime import datetime

from app import db


class Caso(db.Model):
    __tablename__ = "casos"

    id = db.Column(db.Integer, primary_key=True)
    numero_expediente = db.Column(db.String(50), unique=True, nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    tipo = db.Column(db.String(50), nullable=False)  # transito, laboral
    # abierto, en_analisis, cerrado
    estado = db.Column(db.String(30), nullable=False, default="abierto")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    usuario = db.relationship("Usuario", backref="casos")

    def __repr__(self):
        return f"<Caso {self.numero_expediente}>"
