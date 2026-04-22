# `auth_role_permissions`

`auth_role_permissions` es la tabla pivote que une:

- un rol
- con un permiso

Sirve para expresar: "este rol tiene este permiso".

## Relacion Entre Tablas

- `auth_roles`: define roles, por ejemplo `administrator`
- `auth_permissions`: define permisos, por ejemplo `core.system.read`, `core.team.create`, `auth.admin`
- `auth_role_permissions`: conecta un rol con uno o varios permisos

## Flujo Completo

1. Un usuario recibe uno o varios roles en `auth_user_roles`.
2. Cada rol recibe uno o varios permisos en `auth_role_permissions`.
3. Cuando el sistema valida acceso, revisa si alguno de los roles del usuario tiene el permiso requerido.

## Ejemplo Conceptual

Supongamos:

- usuario: `admin@local.dev`
- rol: `administrator`
- permisos del rol:
  - `core.system.read`
  - `core.team.create`
  - `core.team.update`
  - `core.team.delete`
  - `auth.admin`

Entonces el usuario `admin@local.dev` hereda esos permisos a traves del rol `administrator`.

## Como Se Usa En Este Proyecto

### Asignar un permiso a un rol

Ejemplo conceptual:

```python
assign_permission_to_role("administrator", "core.system.create")
```

Para permisos por modelo/recurso (3 segmentos), ejemplo:

```python
assign_scoped_permission_to_role("administrator", "core", "system", "read")
```

Nota: en GraphQL `core`, las acciones usadas por defecto son `read`, `create`, `update` y `delete`.

Eso provoca que el sistema:

1. Busque el rol `administrator`
2. Si no existe, lo cree
3. Busque el permiso `core.system.create`
4. Si no existe, lo cree
5. Cree la relacion entre ambos en `auth_role_permissions`

### Verificar permisos

Cuando se pregunta si un usuario tiene permiso:

1. se buscan sus roles en `auth_user_roles`
2. se buscan los permisos asociados a esos roles en `auth_role_permissions`
3. se valida si el permiso requerido esta presente

## Archivos Donde Se Usa

- Repositorio de acceso: [access_control.py](/home/antoniofregoso/Desarrollo/full_stack/cj-backend/app/auth/repository/access_control.py)
- Servicio de acceso: [access_control.py](/home/antoniofregoso/Desarrollo/full_stack/cj-backend/app/auth/service/access_control.py)

## Resumen Corto

- `auth_user_roles` responde: que roles tiene un usuario
- `auth_role_permissions` responde: que permisos tiene un rol

Combinadas, ambas tablas permiten responder:

"que puede hacer este usuario?"

## Ejemplo Mental Simple

Piensalo asi:

- usuario -> recibe rol
- rol -> recibe permisos
- usuario -> hereda permisos del rol

Entonces:

- no asignas permisos directamente al usuario
- asignas permisos al rol
- y asignas el rol al usuario

Eso hace que el sistema sea mas ordenado y escalable.
