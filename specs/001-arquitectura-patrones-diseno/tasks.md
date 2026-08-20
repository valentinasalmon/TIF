# Tareas: Arquitectura en capas y patrones de diseño

Referencia: `plan.md` de esta misma carpeta.

- [x] T1 — Crear `app/config.py` con `Config`/`DevelopmentConfig`/`TestingConfig`/`ProductionConfig`
      y actualizar `create_app` para usarla.
- [x] T2 — Crear `UsuarioRepository` y `CasoRepository`.
- [x] T3 — Crear `AuthService` y `CasoService` sobre los repositories.
- [x] T4 — Reescribir `app/routes/auth.py` y `app/routes/casos.py` como controladores delgados.
- [x] T5 — Tests: `test_auth_service.py`, `test_caso_repository.py`, `test_caso_service.py` con
      `TestingConfig` (SQLite en memoria).
- [x] T6 — Verificación manual: login, alta de caso, listado y detección de duplicado vía
      `app.test_client()`.
