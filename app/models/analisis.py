# app/models/analisis.py
#
# Modelos del módulo de análisis forense: metadatos / ELA / PRNU / modelo IA
# Define 3 tablas: resultados_analisis, anomalias_detectadas, conclusiones_finales

from app import db
from datetime import datetime


# ============================================================
# ResultadoAnalisis
# Una fila por cada capa de análisis ejecutada sobre una imagen
# ============================================================
class ResultadoAnalisis(db.Model):
    __tablename__ = "resultados_analisis"

    TIPOS_ANALISIS = ("metadatos", "ela", "prnu", "modelo_ia")
    CLASIFICACIONES = ("sin_indicios", "debil", "moderado", "fuerte")
    ESTADOS = ("completado", "error", "procesando")

    id = db.Column(db.Integer, primary_key=True)
    imagen_id = db.Column(
        db.Integer, db.ForeignKey("imagenes.id", ondelete="CASCADE"), nullable=False
    )
    tipo_analisis = db.Column(db.String(20), nullable=False)
    clasificacion = db.Column(db.String(20), nullable=False)
    fecha_analisis = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    estado = db.Column(db.String(20), nullable=False, default="completado")

    # Relaciones
    imagen = db.relationship("Imagen", backref="resultados_analisis")
    anomalias = db.relationship(
        "AnomaliaDetectada",
        backref="resultado",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    def __repr__(self):
        return (
            f"<ResultadoAnalisis imagen_id={self.imagen_id} "
            f"tipo={self.tipo_analisis} clasificacion={self.clasificacion}>"
        )

    def to_dict(self):
        return {
            "id": self.id,
            "imagen_id": self.imagen_id,
            "tipo_analisis": self.tipo_analisis,
            "clasificacion": self.clasificacion,
            "fecha_analisis": self.fecha_analisis.isoformat(),
            "estado": self.estado,
            "anomalias": [a.to_dict() for a in self.anomalias],
        }


# ============================================================
# AnomaliaDetectada
# Una fila por cada anomalía encontrada dentro de un resultado
# ============================================================
class AnomaliaDetectada(db.Model):
    __tablename__ = "anomalias_detectadas"

    SEVERIDADES = ("directo", "fuerte", "moderado", "debil", "neutro")

    id = db.Column(db.Integer, primary_key=True)
    resultado_id = db.Column(
        db.Integer,
        db.ForeignKey("resultados_analisis.id", ondelete="CASCADE"),
        nullable=False,
    )
    campo_afectado = db.Column(db.String(50), nullable=False)
    valor_detectado = db.Column(db.Text, nullable=True)
    descripcion = db.Column(db.Text, nullable=False)
    severidad = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<AnomaliaDetectada campo={self.campo_afectado} severidad={self.severidad}>"

    def to_dict(self):
        return {
            "id": self.id,
            "campo_afectado": self.campo_afectado,
            "valor_detectado": self.valor_detectado,
            "descripcion": self.descripcion,
            "severidad": self.severidad,
        }


# ============================================================
# ConclusionFinal
# Una fila por imagen: cruce de las 4 capas en una conclusión única
# ============================================================
class ConclusionFinal(db.Model):
    __tablename__ = "conclusiones_finales"

    CONCLUSIONES = (
        "alta_probabilidad",
        "probabilidad_considerable",
        "indicios_leves",
        "sin_evidencia",
    )

    id = db.Column(db.Integer, primary_key=True)
    imagen_id = db.Column(
        db.Integer,
        db.ForeignKey("imagenes.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    conclusion = db.Column(db.String(50), nullable=False)
    recomendacion = db.Column(db.Text, nullable=True)
    fecha_generacion = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )

    imagen = db.relationship("Imagen", backref=db.backref(
        "conclusion_final", uselist=False
    ))

    def __repr__(self):
        return f"<ConclusionFinal imagen_id={self.imagen_id} conclusion={self.conclusion}>"

    def to_dict(self):
        return {
            "id": self.id,
            "imagen_id": self.imagen_id,
            "conclusion": self.conclusion,
            "recomendacion": self.recomendacion,
            "fecha_generacion": self.fecha_generacion.isoformat(),
        }