# Specs

Este directorio contiene las specs del proyecto siguiendo un flujo de **spec-driven
development** inspirado en [GitHub Spec Kit](https://github.com/github/spec-kit).

## Flujo

1. **`/specify`** — a partir de una descripción en lenguaje natural, crea
   `specs/NNN-nombre-feature/spec.md` (a partir de `templates/spec-template.md`): qué problema
   resuelve, requisitos funcionales, criterios de aceptación. Sin detalles de implementación.
2. **`/plan`** — a partir del `spec.md`, genera `plan.md` (a partir de `templates/plan-template.md`):
   diseño técnico, capas y patrones afectados (ver `memory/constitution.md`), contratos entre
   capas.
3. **`/tasks`** — a partir del `plan.md`, genera `tasks.md` (a partir de
   `templates/tasks-template.md`): checklist de tareas concretas y ordenadas, listas para
   ejecutar.
4. Implementación siguiendo `tasks.md`.

Cada carpeta se numera secuencialmente (`001-...`, `002-...`) y el nombre describe la feature en
minúsculas separadas por guiones.

## Specs existentes

- [`001-arquitectura-patrones-diseno`](./001-arquitectura-patrones-diseno/spec.md) — refactor de
  auth y casos aplicando Repository, Service Layer y Factory/Strategy de configuración.
- [`002-cicd-conventional-commits`](./002-cicd-conventional-commits/spec.md) — pipeline de CI/CD y
  adopción de Conventional Commits.
