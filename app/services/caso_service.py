"""Service Layer: lógica de negocio del módulo de casos, separada de las rutas."""
from app.repositories.caso_repository import CasoRepository
from app.models.caso import Caso


class CasoDuplicadoError(Exception):
    """Ya existe un caso con ese número de expediente."""


class PermisoDenegadoError(Exception):
    """El usuario no tiene permiso para operar sobre este caso."""


class CasoService:

    def __init__(self, caso_repository=None):
        self.caso_repository = caso_repository or CasoRepository()

    def listar_casos_de_usuario(self, usuario_id):
        return self.caso_repository.listar_por_usuario(usuario_id)

    def crear_caso(self, usuario_id, numero_expediente, titulo, descripcion, tipo):
        if self.caso_repository.obtener_por_numero_expediente(numero_expediente):
            raise CasoDuplicadoError(
                f"Ya existe un caso con el expediente {numero_expediente}"
            )

        caso = Caso(
            numero_expediente=numero_expediente,
            titulo=titulo,
            descripcion=descripcion,
            tipo=tipo,
            usuario_id=usuario_id,
        )
        return self.caso_repository.guardar(caso)

    def obtener_caso(self, caso_id):
        return self.caso_repository.obtener_por_id(caso_id)

    def puede_acceder(self, caso, usuario):
        return caso.usuario_id == usuario.id or usuario.rol == "administrador"

    def actualizar_caso(self, caso, usuario, titulo, descripcion, tipo, estado):
        if not self.puede_acceder(caso, usuario):
            raise PermisoDenegadoError("No tenés permiso para editar este caso")

        caso.titulo = titulo
        caso.descripcion = descripcion
        caso.tipo = tipo
        caso.estado = estado
        self.caso_repository.actualizar()
        return caso
