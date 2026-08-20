# Plan técnico: CI/CD y Conventional Commits

Referencia: `spec.md` de esta misma carpeta.

## Capas afectadas

Infraestructura de proceso, no código de `app/`:

- `.github/workflows/ci.yml` (nuevo)
- `commitlint.config.js` (nuevo)
- `.pre-commit-config.yaml` (nuevo)
- `CONTRIBUTING.md` (nuevo)
- `requirements.txt` (agrega `pytest-cov`, `pre-commit`, y las dependencias que faltaban:
  `Flask-SQLAlchemy`, `Flask-Login`, `bcrypt`, `itsdangerous`)

## Patrones de diseño aplicados

No aplica (spec de infraestructura, no de código de dominio).

## Contratos entre capas

No aplica.

## Cambios en datos

Ninguno.

## Excepciones a la constitución

Ninguna.

## Riesgos

- El job `commitlint` podría bloquear PRs legítimos si algún colaborador no conoce la convención
  todavía. Mitigado documentando ejemplos claros en `CONTRIBUTING.md`.
