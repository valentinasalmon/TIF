import pytest

from app.services.caso_service import CasoService, CasoDuplicadoError, PermisoDenegadoError


def test_crear_caso(app, usuario):
    with app.app_context():
        servicio = CasoService()
        caso = servicio.crear_caso(
            usuario_id=usuario.id,
            numero_expediente="EXP-001",
            titulo="Choque en ruta 9",
            descripcion="Colisión entre dos vehículos",
            tipo="transito",
        )

        assert caso.id is not None
        assert caso.estado == "abierto"


def test_crear_caso_con_expediente_duplicado(app, usuario):
    with app.app_context():
        servicio = CasoService()
        servicio.crear_caso(usuario.id, "EXP-001", "Caso 1", "desc", "transito")

        with pytest.raises(CasoDuplicadoError):
            servicio.crear_caso(usuario.id, "EXP-001", "Caso 2", "otra desc", "laboral")


def test_puede_acceder_dueno(app, usuario):
    with app.app_context():
        servicio = CasoService()
        caso = servicio.crear_caso(usuario.id, "EXP-001", "Caso 1", "desc", "transito")

        assert servicio.puede_acceder(caso, usuario) is True


def test_puede_acceder_administrador(app, usuario, administrador):
    with app.app_context():
        servicio = CasoService()
        caso = servicio.crear_caso(usuario.id, "EXP-001", "Caso 1", "desc", "transito")

        assert servicio.puede_acceder(caso, administrador) is True


def test_actualizar_caso_sin_permiso(app, usuario, administrador):
    with app.app_context():
        from app.models.usuario import Usuario

        otro = Usuario(nombre="Otro", email="otro@example.com", rol="perito")
        otro.set_password("clave123")

        from app import db
        db.session.add(otro)
        db.session.commit()

        servicio = CasoService()
        caso = servicio.crear_caso(usuario.id, "EXP-001", "Caso 1", "desc", "transito")

        with pytest.raises(PermisoDenegadoError):
            servicio.actualizar_caso(
                caso, otro, titulo="x", descripcion="y", tipo="laboral", estado="cerrado"
            )
