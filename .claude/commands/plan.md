---
description: Genera el plan técnico (plan.md) para la spec más reciente o la que indique el usuario.
---

Instrucciones para Claude:

1. Identificá la spec sobre la que trabajar: si el usuario pasó un número/nombre en
   `$ARGUMENTS`, usá esa carpeta bajo `specs/`; si no, usá la de número más alto que todavía no
   tenga `plan.md`.
2. Leé `spec.md` de esa carpeta y `memory/constitution.md`.
3. Explorá el código relevante en `app/` para entender los patrones existentes en capas similares
   (routes, services, repositories) antes de proponer el diseño.
4. Completá `plan.md` (a partir de `specs/templates/plan-template.md`):
   - Qué capas se tocan (routes/services/repositories/models).
   - Qué patrones de `memory/constitution.md` aplican.
   - Contratos concretos: firmas de métodos nuevos/modificados en services y repositories, con
     tipos de entrada/salida y excepciones que pueden lanzar.
   - Cambios de datos si los hay.
   - Sección "Excepciones a la constitución": si el plan se aparta de algún principio, justificarlo
     explícitamente; si no, escribir "Ninguna".
   - Riesgos y cómo se mitigan.
5. Si el plan requiere apartarse de la arquitectura en capas o de un patrón obligatorio, avisale al
   usuario explícitamente antes de continuar.
6. Mostrale el `plan.md` resultante y preguntale si está listo para pasar a `/tasks`.
