# Spec: CI/CD y Conventional Commits

## Problema

No hay pipeline automático que verifique lint, tests ni formato de commits antes de mergear
cambios. Los errores de estilo o dependencias faltantes (como el `requirements.txt` incompleto)
solo se detectan manualmente, si alguien se acuerda.

## Alcance

Pipeline de CI en GitHub Actions con lint y tests automáticos, más adopción de Conventional
Commits documentada, validada en CI y reforzada con un hook local.

## Requisitos funcionales

- RF-1: Todo `push` y `pull_request` corre lint (`flake8`, `pylint`) y tests (`pytest --cov`).
- RF-2: Todo Pull Request valida que sus commits sigan Conventional Commits.
- RF-3: Un desarrollador puede instalar un hook local que rechace un commit mal formateado antes
  de crearlo.
- RF-4: La convención de commits está documentada con ejemplos concretos del repo.

## Requisitos no funcionales

- El job de tests no depende de una instancia de Postgres (usa `TestingConfig` con SQLite).

## Criterios de aceptación

- [x] Dado un push a cualquier rama, cuando corre el workflow, entonces se ejecutan los jobs
      `lint` y `test`.
- [x] Dado un Pull Request con un commit mal formateado, cuando corre el workflow, entonces el job
      `commitlint` falla.
- [x] Dado un hook de `pre-commit` instalado, cuando se intenta commitear con un mensaje inválido,
      entonces el commit se rechaza localmente.

## Fuera de alcance

Deploy automático (no se pidió en esta iteración).
