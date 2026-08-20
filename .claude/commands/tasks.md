---
description: Genera el checklist de tareas ejecutables (tasks.md) a partir del plan técnico.
---

Instrucciones para Claude:

1. Identificá la spec: mismo criterio que en `/plan` (parámetro en `$ARGUMENTS` o la más reciente
   con `plan.md` pero sin `tasks.md`).
2. Leé `spec.md` y `plan.md` de esa carpeta.
3. Completá `tasks.md` (a partir de `specs/templates/tasks-template.md`) con tareas concretas,
   ordenadas de forma ejecutable, siguiendo el orden natural de capas: config/modelos →
   repositories → services → routes → tests → verificación manual.
4. Cada tarea tiene que ser lo suficientemente chica para implementarse y verificarse de forma
   independiente. Incluí siempre al menos una tarea de tests y una de verificación manual/end-to-end.
5. Mostrale al usuario el `tasks.md` resultante y preguntale si querés que empieces a implementarlo.
