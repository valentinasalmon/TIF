# Guía de contribución

## Arquitectura

El proyecto sigue una arquitectura en capas. Antes de tocar código, revisá
`memory/constitution.md` y las specs en `specs/` para entender los patrones de diseño obligatorios
(App Factory, Repository, Service Layer, Decorator para control de acceso).

## Flujo de trabajo: spec-driven development

Para features nuevas o cambios de arquitectura, seguí el flujo:

1. `/specify <descripción de la feature>` — crea `specs/NNN-nombre/spec.md` con el problema a
   resolver y los criterios de aceptación.
2. `/plan` — genera `specs/NNN-nombre/plan.md` con el diseño técnico (capas afectadas, patrones a
   usar, contratos).
3. `/tasks` — genera `specs/NNN-nombre/tasks.md`, el checklist ejecutable de la implementación.
4. Implementar siguiendo `tasks.md`, con tests.

Para cambios chicos (fix de un typo, ajuste menor de estilo) no hace falta pasar por este flujo.

## Setup del entorno de desarrollo

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pre-commit install --hook-type commit-msg --hook-type pre-commit
```

`pre-commit install` deja instalado un hook local que:

- Valida que el mensaje de commit siga Conventional Commits (bloquea el commit si no cumple).
- Corre `flake8` sobre los archivos modificados antes de cada commit.

## Conventional Commits

Todos los commits deben seguir el formato:

```
<tipo>(<scope opcional>): <descripción en imperativo, minúscula, sin punto final>
```

Tipos permitidos:

| Tipo       | Uso                                                              |
|------------|-------------------------------------------------------------------|
| `feat`     | Nueva funcionalidad para el usuario                              |
| `fix`      | Corrección de un bug                                             |
| `docs`     | Cambios de documentación únicamente                              |
| `style`    | Formato, espacios, punto y coma — sin cambio de lógica           |
| `refactor` | Cambio de código que no agrega funcionalidad ni corrige un bug   |
| `test`     | Agregar o corregir tests                                         |
| `chore`    | Tareas de mantenimiento (dependencias, config, etc.)             |
| `ci`       | Cambios en pipelines de integración continua                     |
| `build`    | Cambios que afectan el sistema de build o dependencias externas  |
| `perf`     | Cambios que mejoran el rendimiento                                |

Ejemplos reales del repo:

```
feat(casos): agregar filtro de casos por estado
fix(auth): corregir expiración del token de recuperación de password
refactor(casos): mover acceso a datos a CasoRepository
test(auth): cubrir login con credenciales inválidas
ci: agregar job de commitlint al pipeline
```

Se valida automáticamente en dos lugares:

- **Local**: hook de `pre-commit` (`conventional-pre-commit`), rechaza el commit antes de crearlo.
- **CI**: job `commitlint` en `.github/workflows/ci.yml`, corre sobre los commits de cada Pull
  Request.

## Antes de abrir un Pull Request

```bash
flake8 app/
pylint app/
pytest --cov=app
```

Los tres deben pasar en verde — son los mismos checks que corre el CI.
