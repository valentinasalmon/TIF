# app/repositories/analisis_repository.py
#
# Acceso a datos del módulo de análisis forense.
# Sin lógica de negocio acá - solo lectura/escritura en Postgres.

from app import db
from app.models.analisis import ResultadoAnalisis, AnomaliaDetectada, ConclusionFinal


class AnalisisRepository:

    @staticmethod
    def crear_resultado(imagen_id, tipo_analisis, clasificacion, estado="completado"):
        """Crea una fila en resultados_analisis y la persiste."""
        resultado = ResultadoAnalisis(
            imagen_id=imagen_id,
            tipo_analisis=tipo_analisis,
            clasificacion=clasificacion,
            estado=estado,
        )
        db.session.add(resultado)
        db.session.commit()
        return resultado

    @staticmethod
    def guardar_anomalias(resultado_id, lista_anomalias):
        """
        Inserta todas las anomalías detectadas para un resultado.
        lista_anomalias: lista de dicts con keys:
            campo_afectado, valor_detectado, descripcion, severidad
        """
        objetos = [
            AnomaliaDetectada(
                resultado_id=resultado_id,
                campo_afectado=a["campo_afectado"],
                valor_detectado=a.get("valor_detectado"),
                descripcion=a["descripcion"],
                severidad=a["severidad"],
            )
            for a in lista_anomalias
        ]
        db.session.bulk_save_objects(objetos)
        db.session.commit()

    @staticmethod
    def obtener_resultado(imagen_id, tipo_analisis):
        """Busca si ya existe un análisis de este tipo para esta imagen."""
        return ResultadoAnalisis.query.filter_by(
            imagen_id=imagen_id, tipo_analisis=tipo_analisis
        ).first()

    @staticmethod
    def obtener_todos_resultados(imagen_id):
        """Devuelve los resultados de las 4 capas (o las que existan) para una imagen."""
        return ResultadoAnalisis.query.filter_by(imagen_id=imagen_id).all()

    @staticmethod
    def crear_conclusion_final(imagen_id, conclusion, recomendacion=None):
        """Crea o actualiza la conclusión combinada de una imagen."""
        existente = ConclusionFinal.query.filter_by(imagen_id=imagen_id).first()
        if existente:
            existente.conclusion = conclusion
            existente.recomendacion = recomendacion
            db.session.commit()
            return existente

        nueva = ConclusionFinal(
            imagen_id=imagen_id,
            conclusion=conclusion,
            recomendacion=recomendacion,
        )
        db.session.add(nueva)
        db.session.commit()
        return nueva