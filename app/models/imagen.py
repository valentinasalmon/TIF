# app/models/imagen.py
#
# Modelo de la tabla `imagenes`, ya creada en Postgres.
# Representa las imágenes cargadas a un caso.

from app import db
from datetime import datetime


class Imagen(db.Model):
    __tablename__ = "imagenes"

    FORMATOS = ("jpeg", "jpg", "png", "heic")
    ORIGENES = ("carga_directa", "mail", "whatsapp", "otro", "no_se")

    id = db.Column(db.Integer, primary_key=True)
    caso_id = db.Column(
        db.Integer, db.ForeignKey("casos.id", ondelete="CASCADE"), nullable=False
    )
    nombre_archivo = db.Column(db.String(255), nullable=False)
    ruta_almacenamiento = db.Column(db.String(500), nullable=False)
    formato = db.Column(db.String(10), nullable=False)
    origen_declarado = db.Column(db.String(30), nullable=True)
    fecha_carga = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    usuario_carga_id = db.Column(
        db.Integer, db.ForeignKey("usuarios.id"), nullable=False
    )

    # Relaciones
    caso = db.relationship("Caso", backref="imagenes")
    usuario_carga = db.relationship("Usuario", backref="imagenes_cargadas")

    def __repr__(self):
        return f"<Imagen id={self.id} nombre={self.nombre_archivo} caso_id={self.caso_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "caso_id": self.caso_id,
            "nombre_archivo": self.nombre_archivo,
            "ruta_almacenamiento": self.ruta_almacenamiento,
            "formato": self.formato,
            "origen_declarado": self.origen_declarado,
            "fecha_carga": self.fecha_carga.isoformat(),
            "usuario_carga_id": self.usuario_carga_id,
        }