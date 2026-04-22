# Control de acceso de usuarios y patron para otros modelos

Este documento explica el diseño actual de control de acceso para `AuthUser` y como reutilizar el mismo patron en los demas modelos del sistema.

## Objetivo

Queremos cubrir dos necesidades distintas:

- Cada usuario puede consultar y editar su propio perfil.
- Un administrador puede consultar y editar cualquier usuario humano.

Ademas:

- Los usuarios `SYSTEM` como el `bot` no deben aparecer en el flujo normal del frontend.
- Cambiar perfil no debe mezclar credenciales, permisos ni administracion global.

## Idea central

El control no se resuelve con una sola mutation.

Se separa en tres caminos:

- `me`
  - devuelve el usuario autenticado actual
- `updateMyProfile`
  - permite que un usuario edite solo sus propios datos seguros
- `updateUserByAdmin`
  - permite que un administrador edite usuarios humanos

Y un cuarto camino aparte para credenciales:

- `changeMyPassword`

Esta separacion evita que un usuario comun pueda tocar campos sensibles solo porque existe una mutation de update demasiado amplia.

## Como quedo implementado

### Query del usuario autenticado

Archivo:

- `app/auth/graphql/query.py`

Query:

- `me`

Proteccion:

- `IsAuthenticated`

Funcion:

- obtiene el `user_id` desde el JWT
- carga el usuario real
- devuelve su perfil serializado

## Edicion del propio perfil

Archivos:

- `app/auth/graphql/types.py`
- `app/auth/graphql/mutation.py`
- `app/auth/service/auth_user.py`

Mutation:

- `updateMyProfile(payload)`

Proteccion:

- `IsAuthenticated`

Campos permitidos:

- `name`
- `avatar_url`
- `theme`
- `lang_id`
- `tz_id`
- `tz_offset`
- `page_size`

Campos no permitidos en este flujo:

- `email`
- `active`
- `user_type`
- `company_id`
- roles
- permisos
- password

La validacion ocurre en `AuthUserService.update_my_profile(...)`.

## Cambio de contraseña

Archivos:

- `app/auth/graphql/types.py`
- `app/auth/graphql/mutation.py`
- `app/auth/service/authentication.py`

Mutation:

- `changeMyPassword(payload)`

Proteccion:

- `IsAuthenticated`

Reglas:

- pide `current_password`
- pide `new_password`
- valida que la contraseña actual sea correcta
- exige minimo 8 caracteres para la nueva
- no permite reutilizar la misma
- bloquea usuarios `SYSTEM`

## Administracion de usuarios

Archivos:

- `app/auth/graphql/mutation.py`
- `app/auth/graphql/query.py`
- `app/auth/service/auth_user.py`

Query administrativa:

- `getAllUsers`

Mutation administrativa:

- `updateUserByAdmin(userId, payload)`

Proteccion:

- `HasModuleAccess("auth", "read")` para lectura
- `HasModuleAccess("auth", "admin")` para administracion

Campos permitidos para admin:

- `email`
- `name`
- `avatar_url`
- `active`
- `theme`
- `lang_id`
- `tz_id`
- `tz_offset`
- `page_size`
- `company_id`

Restricciones:

- no se listan usuarios `SYSTEM`
- no se permite editar usuarios `SYSTEM` desde este flujo

## Por que no usar una sola mutation de update

Porque mezclar estos escenarios genera riesgo:

- editar perfil propio
- editar usuarios ajenos
- editar campos sensibles
- cambiar contraseñas

Si todo eso vive en un solo endpoint o mutation:

- el frontend termina mandando payloads demasiado grandes
- el backend necesita demasiadas excepciones
- es mas facil abrir huecos de seguridad

Separar por intencion hace el sistema mas claro y seguro.

## RBAC usado

Permisos actuales de `auth`:

- `auth.read`
- `auth.admin`

Interpretacion:

- `auth.read`
  - permite consultas administrativas como lista de usuarios
- `auth.admin`
  - permite modificar usuarios ajenos, roles y permisos

Los seeds iniciales asignan ambos al rol `administrator`.

## Como se filtran los bots

Archivo:

- `app/auth/repository/auth_user.py`

Comportamiento:

- `get_all()` excluye `UserType.SYSTEM` por default
- `get_by_id()` excluye `UserType.SYSTEM` por default
- `get_by_email()` no filtra porque login, seeds y procesos internos si necesitan resolver al bot

Esto deja al usuario tecnico fuera del frontend normal sin romper la operacion interna.

## Patron recomendado para otros modelos

Este mismo enfoque aplica muy bien a entidades como:

- `Company`
- `Party`
- `Country`
- `Page`
- cualquier modelo nuevo

La regla es separar tres tipos de operaciones:

### 1. Consulta

Usa permisos de lectura por modulo:

- `core.read`
- `sales.read`
- `crm.read`

Ejemplo:

```python
CoreReadAccess = HasModuleAccess("core", "read")
```

### 2. Edicion propia o por ownership

Si la entidad pertenece a un usuario o tiene responsable, usa una regla de ownership.

Ejemplos:

- un usuario puede editar su propio perfil
- un usuario puede editar su propia configuracion
- un usuario puede editar sus propios registros si `owner_id == current_user.id`

Patron:

1. obtener `current_user.id` desde JWT
2. cargar el registro
3. validar ownership
4. permitir solo campos seguros

Esto no depende solo del permiso global. Depende tambien de que el registro sea suyo.

### 3. Administracion global

Cuando alguien puede modificar registros ajenos o campos sensibles, usa permisos administrativos del modulo:

- `core.admin`
- `auth.admin`
- `sales.admin`

O si quieres granularidad clasica:

- `core.create`
- `core.update`
- `core.delete`

## Ejemplo de diseño recomendado por modelo

Para un modelo cualquiera, por ejemplo `Company`, yo recomiendo:

- `getAllCompanies`
  - permiso `core.read`
- `getCompanyById`
  - permiso `core.read`
- `updateMyCompanyPreferences`
  - ownership o relacion explicita con el usuario actual
- `updateCompanyByAdmin`
  - permiso `core.update` o `core.admin`
- `deleteCompany`
  - permiso `core.delete`

No todo debe pasar por una sola mutation `updateCompany`.

## Regla practica para futuros modelos

Cuando crees una nueva entidad, piensa primero en estas preguntas:

1. Quien puede verla
2. Quien puede crearla
3. Quien puede editarla
4. Hay campos que el duenio si puede editar pero otros no
5. Existe un admin que puede editar mas que el usuario normal
6. La entidad tiene ownership

Con esas respuestas defines si necesitas:

- una mutation comun por modulo
- una mutation propia del usuario
- una mutation administrativa

## Resumen corto

El patron correcto no es solo RBAC.

Es combinar:

- autenticacion
- permisos por modulo
- ownership cuando aplica
- payloads separados por intencion

En este proyecto, `AuthUser` ya quedo como referencia de ese patron:

- `me`
- `updateMyProfile`
- `changeMyPassword`
- `getAllUsers`
- `updateUserByAdmin`

Si replicas ese enfoque en los demas modelos, el backend se vuelve mucho mas seguro, entendible y facil de mantener.

## Asignacion de usuarios a sistema, equipo, modulo, entidad o feature

Para relacionar usuarios con la taxonomia funcional, el proyecto usa una tabla pivote separada:

- `core_user_assignments`

La idea es no meter listas de usuarios dentro de:

- `core_systems`
- `core_teams`
- `core_modules`
- `core_features`

Porque eso mezclaria estructura con pertenencia.

### Que representa una asignacion

Una fila en `core_user_assignments` significa:

- este usuario pertenece o esta asignado a este alcance funcional

Campos principales:

- `user_id`
- `system_id`
- `team_id`
- `module_id`
- `entity_id`
- `feature_id`
- `assignment_role`
- `is_manager`
- `active`

Regla importante:

- exactamente uno de estos debe venir por fila:
  - `system_id`
  - `team_id`
  - `module_id`
  - `entity_id`
  - `feature_id`

Eso ya queda validado en modelo, service y base de datos.

### Ejemplos

- Usuario asignado al sistema `comercial`
  - `user_id=10`
  - `system_id=1`

- Usuario asignado al equipo `ventas`
  - `user_id=10`
  - `team_id=3`

- Usuario asignado al modulo `quotes`
  - `user_id=10`
  - `module_id=8`

- Usuario asignado a la entidad `facebook_ad`
  - `user_id=10`
  - `entity_id=13`

- Usuario asignado a la feature `approval`
  - `user_id=10`
  - `feature_id=21`

### Por que asi y no con `user_ids` en cada tabla

Porque separar asignacion de estructura te da:

- menos acoplamiento
- mejor mantenimiento
- facilidad para mover usuarios
- posibilidad de agregar rol local o manager por nodo
- claridad entre pertenencia y autorizacion

### Muy importante

Esto no reemplaza RBAC.

Son dos cosas distintas:

- `core_user_assignments`
  - define donde pertenece o participa el usuario
- `auth_user_roles` y `auth_role_permissions`
  - definen que puede hacer el usuario

En otras palabras:

- asignacion = alcance organizacional
- permiso = capacidad de accion

### Mutations y queries disponibles

Queries:

- `getAllUserAssignments`
- `getUserAssignmentsByUser`
- `getUserAssignmentsBySystem`
- `getUserAssignmentsByTeam`
- `getUserAssignmentsByModule`
- `getUserAssignmentsByEntity`
- `getUserAssignmentsByFeature`
- `getMyLandingPath`

Mutations:

- `createUserAssignment`
- `updateUserAssignment`
- `deleteUserAssignment`

## Referencia de arquitectura funcional

Para organizar la empresa y el backend, una jerarquia util es:

1. `Sistema`
2. `Equipo`
3. `Modulo`
4. `Entidad`
5. `Feature`
6. `Accion`

### Que significa cada nivel

- `Sistema`
  - dominio grande del negocio
  - ejemplo: `comercial`, `finanzas`, `operaciones`

- `Equipo`
  - agrupacion funcional u organizacional dentro del sistema
  - ejemplo en `comercial`: `marketing`, `ventas`, `experiencia_cliente`

- `Modulo`
  - unidad funcional de software o negocio que ya tiene sentido propio
  - ejemplo en `ventas`: `leads`, `oportunidades`, `cotizaciones`, `pedidos`

- `Entidad`
  - objeto de datos concreto dentro del modulo
  - ejemplo en `cotizaciones`: `quote`, `quote_line`, `price_rule`

- `Feature`
  - capacidad puntual dentro de la entidad o de la pantalla de trabajo
  - ejemplo en `cotizaciones`: `approval`, `pdf_export`, `clone`

- `Accion`
  - operacion permitida sobre la entidad o el modulo
  - ejemplo: `read`, `create`, `update`, `delete`, `approve`, `export`

### Aclaracion importante

`Modulo` no suele ser el area minima.

Normalmente por debajo del modulo todavia existen:

- entidades
- procesos
- acciones

Por eso, para diseño de permisos y APIs, es mejor pensar asi:

- `sistema` organiza el dominio
- `equipo` organiza responsables
- `modulo` organiza funcionalidades
- `entidad` organiza datos
- `feature` organiza capacidades visibles dentro de la entidad
- `accion` organiza permisos

### Ejemplo en sistema comercial

- `Sistema`: `comercial`
- `Equipos`:
  - `marketing`
  - `ventas`
  - `experiencia_cliente`

- `Modulo` dentro de `ventas`:
  - `leads`
  - `oportunidades`
  - `cotizaciones`
  - `pedidos`

- `Entidades` dentro de `cotizaciones`:
  - `quote`
  - `quote_line`
  - `price_rule`

- `Features` dentro de `cotizaciones`:
  - `approval`
  - `pdf_export`
  - `clone`

### Regla de URL

La URL base recomendada llega hasta `entity`:

```txt
/system/{system}/team/{team}/module/{module}/entity/{entity}
```

Las `features` no deben ir por default en la URL base del dominio.

Normalmente se expresan como:

- tabs
- secciones
- botones
- vistas internas de la pantalla

### Como calcular donde inicia el usuario

La idea es resolver el punto de entrada con la asignacion mas especifica disponible, pero aterrizar siempre en una URL de `entity`.

Prioridad actual implementada:

1. `entity`
2. `module`
3. `team`
4. `system`

Que significa "mas especifica":

- una asignacion a `entity` gana sobre una asignacion a `module`
- una asignacion a `module` gana sobre una asignacion a `team`
- una asignacion a `team` gana sobre una asignacion a `system`

Ejemplo:

- si un usuario tiene una asignacion a `system-technology`
- y otra a `team-software-implementation`

la asignacion mas especifica es `team-software-implementation`

Otro ejemplo:

- si el usuario tiene asignacion a `system`
- a `team`
- y a un `module` dentro de ese team

la asignacion de `module` es la que define el `landing_path`

Nota:

- hoy la implementacion no prioriza `feature` para resolver el inicio
- la logica real en servicio considera solo `entity`, `module`, `team` y `system`

Si el usuario solo tiene alcance a:

- `module`
  - se redirige a la entidad default de ese modulo
- `team`
  - se redirige al modulo y entidad default de ese equipo
- `system`
  - se redirige al modulo y entidad default de ese sistema

Si luego quieres experiencia mas rica, ya dentro de la pantalla de la entidad puedes abrir la `feature` inicial como tab activa o seccion destacada.

- `Acciones`:
  - `read`
  - `create`
  - `update`
  - `delete`
  - `approve`

### Como aterrizarlo a permisos

Hay dos niveles validos de granularidad:

- por sistema o modulo simple
  - `core.read`
  - `core.update`
  - `auth.admin`

- por dominio mas especifico
  - `commercial.quotes.read`
  - `commercial.quotes.create`
  - `finance.invoicing.update`

### Recomendacion practica para este backend

Si el proyecto aun esta en consolidacion, conviene empezar simple:

- permisos por modulo y accion
- ownership cuando aplique
- rutas administrativas separadas

Y dejar una evolucion posible hacia mayor granularidad si despues la operacion real lo exige.

### Ejemplo de decision de diseño

Para una entidad nueva, antes de crear queries y mutations, conviene responder:

1. Quien puede verla
2. Quien puede crearla
3. Quien puede editarla
4. El dueno puede editar solo ciertos campos
5. Un admin puede editar campos mas sensibles
6. Requiere flujo propio para credenciales o aprobaciones

Con esas respuestas puedes decidir si necesitas:

- una query general
- una mutation de ownership
- una mutation administrativa
- permisos por modulo
- permisos mas finos por accion
