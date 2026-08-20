from app.services.auth_service import AuthService


def test_autenticar_con_credenciales_validas(app, usuario):
    with app.app_context():
        resultado = AuthService().autenticar("ana@example.com", "clave123")
        assert resultado is not None
        assert resultado.email == "ana@example.com"


def test_autenticar_con_password_incorrecta(app, usuario):
    with app.app_context():
        resultado = AuthService().autenticar("ana@example.com", "otra-clave")
        assert resultado is None


def test_autenticar_con_email_inexistente(app):
    with app.app_context():
        resultado = AuthService().autenticar("no-existe@example.com", "clave123")
        assert resultado is None


def test_solicitar_recuperacion_devuelve_token_para_usuario_existente(app, usuario):
    with app.app_context():
        token = AuthService().solicitar_recuperacion("ana@example.com")
        assert token is not None


def test_solicitar_recuperacion_devuelve_none_si_no_existe(app):
    with app.app_context():
        token = AuthService().solicitar_recuperacion("no-existe@example.com")
        assert token is None


def test_resetear_password_actualiza_la_contrasena(app, usuario):
    with app.app_context():
        servicio = AuthService()
        token = servicio.solicitar_recuperacion("ana@example.com")

        assert servicio.resetear_password(token, "clave-nueva") is True
        assert servicio.autenticar("ana@example.com", "clave-nueva") is not None


def test_resetear_password_con_token_invalido(app):
    with app.app_context():
        assert AuthService().resetear_password("token-invalido", "clave-nueva") is False
