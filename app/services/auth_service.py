"""Service Layer: lógica de negocio de autenticación, separada de las rutas."""
from app.repositories.usuario_repository import UsuarioRepository


class AuthService:

    def __init__(self, usuario_repository=None):
        self.usuario_repository = usuario_repository or UsuarioRepository()

    def autenticar(self, email, password):
        """Devuelve el Usuario si las credenciales son válidas, o None."""
        usuario = self.usuario_repository.obtener_por_email(email)
        if usuario and usuario.check_password(password):
            return usuario
        return None

    def solicitar_recuperacion(self, email):
        """Genera un token de recuperación para el email dado, si el usuario existe."""
        usuario = self.usuario_repository.obtener_por_email(email)
        if not usuario:
            return None
        return usuario.generar_token_recuperacion()

    def token_es_valido(self, token):
        return self._usuario_del_token(token) is not None

    def resetear_password(self, token, nueva_password):
        """Actualiza la contraseña del usuario asociado al token. True si tuvo éxito."""
        usuario = self._usuario_del_token(token)
        if not usuario:
            return False

        usuario.set_password(nueva_password)
        self.usuario_repository.actualizar()
        return True

    def _usuario_del_token(self, token):
        from app.models.usuario import Usuario

        return Usuario.verificar_token_recuperacion(token)
