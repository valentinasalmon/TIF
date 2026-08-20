# Plan técnico: Arquitectura en capas y patrones de diseño

Referencia: `spec.md` de esta misma carpeta.

## Capas afectadas

- Routes: `app/routes/auth.py`, `app/routes/casos.py` — se reescriben como controladores delgados.
- Services (nuevos): `app/services/auth_service.py`, `app/services/caso_service.py`.
- Repositories (nuevos): `app/repositories/usuario_repository.py`,
  `app/repositories/caso_repository.py`.
- Config (nuevo): `app/config.py`.
- Models: sin cambios de esquema; solo limpieza de estilo.

## Patrones de diseño aplicados

- **Repository**: `UsuarioRepository` y `CasoRepository` encapsulan `Usuario.query...` /
  `Caso.query...`.
- **Service Layer**: `AuthService` (login, recuperación/reseteo de password) y `CasoService`
  (alta, edición, permisos, detección de duplicados).
- **Factory + Strategy de configuración**: `app/config.py` con `DevelopmentConfig`,
  `TestingConfig` (SQLite en memoria), `ProductionConfig`, seleccionadas por
  `obtener_config(nombre_entorno)`.
- **Decorator** (ya existente, sin cambios): `@requiere_rol(...)` en
  `app/services/decoradores.py`.

## Contratos entre capas

- `AuthService.autenticar(email, password) -> Usuario | None`
- `AuthService.solicitar_recuperacion(email) -> str | None` (token)
- `AuthService.token_es_valido(token) -> bool`
- `AuthService.resetear_password(token, nueva_password) -> bool`
- `CasoService.listar_casos_de_usuario(usuario_id) -> list[Caso]`
- `CasoService.crear_caso(usuario_id, numero_expediente, titulo, descripcion, tipo) -> Caso`,
  lanza `CasoDuplicadoError`
- `CasoService.puede_acceder(caso, usuario) -> bool`
- `CasoService.actualizar_caso(caso, usuario, titulo, descripcion, tipo, estado) -> Caso`, lanza
  `PermisoDenegadoError`

## Cambios en datos

Ninguno. Mismo esquema de `Usuario` y `Caso`.

## Excepciones a la constitución

Ninguna.

## Riesgos

- Romper el flujo de recuperación de password al mover la verificación de token a `AuthService`.
  Mitigado con tests de `token_es_valido` / `resetear_password` y prueba manual end-to-end.
