---
description: Crea una spec nueva (specs/NNN-nombre/spec.md) a partir de una descripción en lenguaje natural.
---

Instrucciones para Claude:

1. Leé `memory/constitution.md` para conocer los principios de arquitectura del proyecto.
2. A partir de la descripción de feature que dio el usuario (`$ARGUMENTS`), determiná el próximo
   número de spec (`ls specs/` y tomá el siguiente correlativo de 3 dígitos) y un nombre corto en
   minúsculas separado por guiones.
3. Creá el directorio `specs/NNN-nombre-feature/` y copiá `specs/templates/spec-template.md` como
   `spec.md`, completando todas las secciones:
   - Problema, alcance, requisitos funcionales/no funcionales, criterios de aceptación, fuera de
     alcance.
   - No incluyas detalles de implementación (eso es trabajo de `/plan`).
4. Si algo del pedido es ambiguo (alcance, roles afectados, etc.), preguntale al usuario antes de
   completar la spec en vez de asumir.
5. Agregá la nueva spec al listado de `specs/README.md`.
6. Mostrale al usuario el `spec.md` resultante y preguntale si está listo para pasar a `/plan`.
