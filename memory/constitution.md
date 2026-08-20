# Constitución del proyecto

Principios que rigen toda decisión de arquitectura y de proceso en este repo. Cualquier spec o
plan que los contradiga tiene que justificarlo explícitamente en su sección de "Excepciones".

## 1. Arquitectura en capas

El código de `app/` se organiza en capas con una sola responsabilidad cada una, y las
dependencias solo miran "hacia abajo":

```
routes/        → controladores delgados: parsean el request, llaman a un service, renderizan.
services/      → lógica de negocio y reglas de acceso. No conocen Flask (request/response).
repositories/  → único punto de acceso a datos (queries de SQLAlchemy).
models/        → entidades de dominio (SQLAlchemy models).
```

- Una ruta **nunca** hace queries directas (`Modelo.query...`) ni contiene reglas de negocio.
- Un service **nunca** importa `flask` para leer el request ni arma responses HTTP.
- Todo acceso a datos nuevo pasa por un repository existente o uno nuevo — no se agregan queries
  sueltas en otras capas.

## 2. Patrones de diseño obligatorios

- **App Factory** (`app/__init__.py::create_app`): la app se construye a partir de una función,
  nunca como instancia global a nivel de módulo.
- **Factory/Strategy de configuración** (`app/config.py`): un entorno nuevo (staging, etc.) se
  agrega como una clase de config nueva, nunca con `if`s dispersos leyendo variables de entorno.
- **Repository**: acceso a datos encapsulado por entidad (`UsuarioRepository`, `CasoRepository`).
- **Service Layer**: lógica de negocio encapsulada por dominio (`AuthService`, `CasoService`).
- **Decorator**: control de acceso por rol vía `@requiere_rol(...)` (`app/services/decoradores.py`).

## 3. Testing

- Todo service y repository nuevo se testea con `pytest` usando `TestingConfig` (SQLite en
  memoria) — nunca contra la base de datos de desarrollo/producción.
- Un Pull Request que agrega lógica de negocio sin tests no se mergea.

## 4. Proceso: spec-driven development

Para features nuevas o cambios de arquitectura se sigue el flujo `/specify` → `/plan` → `/tasks` →
implementación, documentado en `CONTRIBUTING.md`. Las specs viven en `specs/NNN-nombre-feature/`.

## 5. Commits y CI

- Todo commit sigue Conventional Commits (`CONTRIBUTING.md`).
- Todo Pull Request pasa `flake8`, `pylint`, `pytest` y `commitlint` en CI antes de mergear.

## Excepciones

Ninguna registrada todavía. Si una spec necesita romper alguno de estos principios, se documenta
acá con el motivo y la fecha.
