# Spec: Arquitectura en capas y patrones de diseño

## Problema

Los módulos `auth` y `casos` tienen la lógica de negocio y el acceso a datos escritos directamente
en las rutas (`Usuario.query...`, `Caso.query...` dentro de funciones de Flask). Esto hace difícil
testear la lógica sin levantar un request HTTP, y no deja un patrón claro para el código nuevo.

## Alcance

Refactor de los módulos existentes `auth` y `casos` para introducir capas de Repository y Service,
y formalizar la configuración por entorno. No agrega funcionalidad nueva de negocio.

## Requisitos funcionales

- RF-1: El comportamiento observable de login, recuperación de password, alta/edición/listado de
  casos y control de permisos por rol se mantiene idéntico al actual.
- RF-2: Toda query de SQLAlchemy para `Usuario` y `Caso` queda encapsulada en un repository.
- RF-3: Toda regla de negocio (duplicado de expediente, permisos de acceso a un caso, validación
  de token de recuperación) queda encapsulada en un service.
- RF-4: La app se puede levantar con una configuración de testing que no requiera Postgres.

## Requisitos no funcionales

- El refactor no puede degradar el rendimiento de las operaciones existentes.
- Los roles (`perito`, `abogado`, `aseguradora`, `administrador`) mantienen su semántica actual.

## Criterios de aceptación

- [x] Dado un usuario con credenciales válidas, cuando hace login, entonces se autentica igual que
      antes del refactor.
- [x] Dado un caso con un `numero_expediente` ya existente, cuando se intenta crear otro caso con
      el mismo número, entonces se rechaza con el mismo mensaje de error.
- [x] Dado un usuario que no es dueño ni administrador, cuando intenta ver o editar un caso ajeno,
      entonces se le deniega el acceso igual que antes.
- [x] Dado el entorno de testing, cuando se corren los tests, entonces no se necesita una base de
      datos Postgres real.

## Fuera de alcance

Agregar funcionalidad nueva de negocio (eso se especifica en una spec propia).
