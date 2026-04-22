# getMyLandingPath

Este documento explica como usar el landing path calculado del usuario autenticado.

Guia practica complementaria:

- [Guia de uso de asignaciones](/home/antoniofregoso/Desarrollo/full_stack/cj-backend/docs/assignment_usage_guide.md)

## Objetivo

`getMyLandingPath` sirve para obtener la ruta inicial a la que debe navegar el frontend despues del login.

La resolucion se hace con base en las asignaciones del usuario en `core_user_assignments`.

## Como se calcula

La prioridad actual es:

1. `entity_id`
2. `module_id`
3. `team_id`
4. `system_id`

Si el usuario tiene varias asignaciones, se toma la mas especifica.

Si no existe una asignacion util o no se puede resolver una entidad destino, la respuesta sera `null`.

## Formato de salida

La respuesta es un `String` o `null`.

Ejemplo:

```text
/system/comercial/team/ventas/module/cotizaciones/entity/quote
```

## Opcion 1: query directa

Puedes consultar la query:

- `getMyLandingPath`

Ejemplo:

```graphql
query GetMyLandingPath {
  getMyLandingPath
}
```

Respuesta:

```json
{
  "data": {
    "getMyLandingPath": "/system/comercial/team/ventas/module/cotizaciones/entity/quote"
  }
}
```

## Opcion 2: campo calculado dentro de `me`

Tambien puedes pedir el campo calculado `landingPath` dentro de `me`.

Ejemplo:

```graphql
query Me {
  me {
    id
    email
    landingPath
  }
}
```

Respuesta:

```json
{
  "data": {
    "me": {
      "id": 1,
      "email": "admin@company.com",
      "landingPath": "/system/comercial/team/ventas/module/cotizaciones/entity/quote"
    }
  }
}
```

## Recomendacion para frontend

Si el frontend ya consulta `me` al iniciar sesion, conviene usar `me.landingPath` para evitar una query adicional.

Si prefieres separar autenticacion de navegacion, puedes usar `getMyLandingPath` como query independiente despues del login.

## Flujo sugerido despues del login

1. El usuario hace login y obtiene token.
2. El frontend consulta `me { landingPath }` o `getMyLandingPath`.
3. Si existe valor, hace redirect a esa ruta.
4. Si el valor es `null`, usa una ruta fallback como dashboard, home o selector de modulo.

## Archivos relacionados

- `app/core/graphql/query.py`
- `app/core/service/core_user_assignment.py`
- `app/auth/graphql/types.py`
- `app/auth/service/auth_user.py`
