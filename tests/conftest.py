import pytest

from app import create_app, db
from app.models.usuario import Usuario


@pytest.fixture
def app():
    app = create_app("testing")
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def usuario(app):
    with app.app_context():
        usuario = Usuario(nombre="Ana Perito", email="ana@example.com", rol="perito")
        usuario.set_password("clave123")
        db.session.add(usuario)
        db.session.commit()
        yield usuario


@pytest.fixture
def administrador(app):
    with app.app_context():
        admin = Usuario(nombre="Admin", email="admin@example.com", rol="administrador")
        admin.set_password("clave123")
        db.session.add(admin)
        db.session.commit()
        yield admin
