from app import db
from app.models.caso import Caso
from app.repositories.caso_repository import CasoRepository


def _crear_caso(usuario_id, numero_expediente="EXP-001"):
    caso = Caso(
        numero_expediente=numero_expediente,
        titulo="Choque en ruta 9",
        descripcion="Colisión entre dos vehículos",
        tipo="transito",
        usuario_id=usuario_id,
    )
    db.session.add(caso)
    db.session.commit()
    return caso


def test_guardar_y_obtener_por_id(app, usuario):
    with app.app_context():
        repositorio = CasoRepository()
        caso = _crear_caso(usuario.id)

        encontrado = repositorio.obtener_por_id(caso.id)
        assert encontrado.numero_expediente == "EXP-001"


def test_obtener_por_numero_expediente(app, usuario):
    with app.app_context():
        repositorio = CasoRepository()
        _crear_caso(usuario.id, numero_expediente="EXP-777")

        encontrado = repositorio.obtener_por_numero_expediente("EXP-777")
        assert encontrado is not None
        assert repositorio.obtener_por_numero_expediente("NO-EXISTE") is None


def test_listar_por_usuario_ordena_por_fecha_desc(app, usuario):
    with app.app_context():
        repositorio = CasoRepository()
        _crear_caso(usuario.id, numero_expediente="EXP-001")
        _crear_caso(usuario.id, numero_expediente="EXP-002")

        casos = repositorio.listar_por_usuario(usuario.id)
        assert [c.numero_expediente for c in casos] == ["EXP-002", "EXP-001"]
