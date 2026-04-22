# RBAC por modulo en GraphQL

Este proyecto controla acceso con RBAC (Role Based Access Control) usando roles y permisos, no con un campo `role` directo en `AuthUser`.

## Modelo de datos

Relaciones usadas:

- `AuthUser` -> usuario
- `AuthUserRole` -> relacion usuario-rol
- `AuthRole` -> rol
- `AuthRolePermission` -> relacion rol-permiso
- `AuthPermission` -> permiso (codigo como `core.system.read`, `core.team.create`, `auth.admin`)

## Diagrama mental rapido

`HasModuleAccess` no busca una tabla `usuario_modulo`.

La relacion real es:

```text
auth_users
   -> auth_user_roles
   -> auth_roles
   -> auth_role_permissions
   -> auth_permissions.code = "modulo.accion" o "modulo.recurso.accion"
```

Ejemplo:

```text
usuario 1
   -> rol admin_core
   -> permiso core.system.read
```

Si una query usa:

```python
HasModuleAccess("core", "read")
```

el sistema valida si el usuario tiene alguno de estos codigos:

- `core.read`
- `core.*`
- `*.*`

Si una query usa `HasScopedAccess("core", "system", "read")`:

- `core.system.read`
- `core.system.*`
- `core.*.read`
- `core.*.*`
- `*.*.*`

## Aclaracion importante: modulo RBAC vs modulo Core

Aqui `module` no significa una relacion fisica con la tabla de modulos funcionales de `core`.

En `HasModuleAccess("core", "read")`, la palabra `core` es solo una clave logica usada para construir permisos.

Por eso no existe una FK como:

- `auth_users.module_id`
- `auth_permissions.module_id`

El modulo RBAC vive dentro del texto de `auth_permissions.code`.
Tambien puede incluir recurso/modelo, por ejemplo `core.system.read`.

## Diferencia contra `core_user_assignments`

No mezclar estos dos conceptos:

- RBAC
  - responde: que puede hacer el usuario
  - usa `auth_user_roles`, `auth_role_permissions`, `auth_permissions`
  - ejemplo: `core.system.read`

- User assignments
  - responde: en que parte de la estructura participa el usuario
  - usa `core_user_assignments`
  - ejemplo: sistema, team, module o entity asignado

En resumen:

- `HasModuleAccess` / `HasScopedAccess` miran permisos
- `getMyLandingPath` mira asignaciones

Consulta principal de permisos:

- Archivo: `app/auth/repository/access_control.py`
- Metodo: `has_permission` / `has_any_permission`

La verificacion hace joins entre `auth_user_roles`, `auth_role_permissions`, `auth_permissions` y `auth_roles` para saber si un usuario tiene permiso activo.

## Flujo de autenticacion y autorizacion

1. Login (`app/auth/service/authentication.py`):
   - Se valida email/password.
   - Se genera JWT con:
     - `sub`: email
     - `uid`: id de usuario

2. Request GraphQL:
   - `HasModuleAccess(module, action)` en `app/infrastructure/JWTBearer.py`:
     - Lee `Authorization: Bearer <token>`.
     - Decodifica JWT.
     - Obtiene `user_id` (primero `uid`, fallback `sub` -> lookup por email).
     - Pregunta a `AccessControlService.has_module_permission(...)`.
   - Para granularidad por recurso/modelo:
     - `HasScopedAccess(module, resource, action)`.
     - Pregunta a `AccessControlService.has_scoped_permission(...)`.

3. Decision de acceso (`app/auth/service/access_control.py`):
   - Se construyen codigos validos en este orden:
     - `{module}.{action}` (ej. `core.read`)
     - `{module}.*` (ej. `core.*`)
     - `*.*` (global)
   - Si existe cualquiera de esos permisos para un rol del usuario -> acceso permitido.
   - Para permisos scoped (`HasScopedAccess`), se evalua:
     - `{module}.{resource}.{action}` (ej. `core.system.read`)
     - `{module}.{resource}.*`
     - `{module}.*.{action}`
     - `{module}.*.*`
     - `*.*.*`

Nota de migracion: desde abril 2026 se removio la compatibilidad legacy en `has_scoped_permission`.
Para `core` ya no aplican fallbacks de 2 segmentos (`core.read`, `core.*`, `*.*`).

## Como se aplica en Core

- Queries de `core` usan `HasScopedAccess("core", recurso, "read")`
- Mutations de `core` usan `HasScopedAccess("core", recurso, "create|update|delete")`
- Archivos:
  - `app/core/graphql/query.py`
  - `app/core/graphql/mutation.py`

Recursos usados por los resolvers de core:

- `system`
- `team`
- `module`
- `entity`
- `feature`
- `action`
- `user_assignment`
- `country`
- `currency`
- `lang`
- `company`
- `company_system_link`
- `party`
- `app`
- `app_setting`
- `timezone`
- `page`

## Administracion de roles y permisos

Mutations disponibles en `app/auth/graphql/mutation.py`:

- `assign_role_to_user(user_id, role_name)`
- `assign_permission_to_role(role_name, permission_code)`
- `assign_module_permission_to_role(role_name, module, action)`
- `assign_scoped_permission_to_role(role_name, module, resource, action)`

Estas mutations requieren permiso `auth.admin`.

## Permisos recomendados por modulo

Para permisos por recurso/modelo:

- Lectura de system: `core.system.read`
- Escritura de team (custom): `core.team.write`
- Crear team (usado por GraphQL core): `core.team.create`
- Actualizar team (usado por GraphQL core): `core.team.update`
- Permiso global scoped en core: `core.*.*`
- Permiso global total: `*.*.*`

## Ejemplo rapido (flujo)

1. Asignar rol a usuario:

```graphql
mutation {
  assignRoleToUser(userId: 1, roleName: "admin_core")
}
```

2. Asignar permisos al rol:

```graphql
mutation {
  assignScopedPermissionToRole(
    roleName: "admin_core"
    module: "core"
    resource: "system"
    action: "read"
  )
}
```

3. Consumir queries/mutations de core con JWT del usuario.

## Nota operativa

Se requiere bootstrap inicial: al menos un usuario/rol con `auth.admin` para poder delegar accesos desde GraphQL.

## Frontend JavaScript vainilla con `graphql-request`

Recomendacion de libreria: `graphql-request` por ser ligera y directa para apps sin framework.

Instalacion:

```bash
npm install graphql-request graphql
```

### Cliente base con JWT y manejo RBAC

```js
import { GraphQLClient } from "graphql-request";

const GRAPHQL_URL = "http://localhost:8000/graphql";
const TOKEN_KEY = "cj_token";

function saveToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function createClient() {
  const token = getToken();
  return new GraphQLClient(GRAPHQL_URL, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
}

function normalizeGraphQLError(error) {
  const messages =
    error?.response?.errors?.map((e) => e.message) ??
    [error?.message ?? "Error desconocido"];

  const text = messages.join(" | ");
  const lower = text.toLowerCase();

  if (lower.includes("unauthorized") || lower.includes("auth")) {
    return { kind: "unauthorized", message: text };
  }
  if (lower.includes("forbidden") || lower.includes("permission")) {
    return { kind: "forbidden", message: text };
  }

  return { kind: "unknown", message: text };
}

async function gqlRequest(query, variables = {}) {
  try {
    const client = createClient();
    return await client.request(query, variables);
  } catch (error) {
    const normalized = normalizeGraphQLError(error);

    if (normalized.kind === "unauthorized") {
      clearToken();
      throw new Error("Sesion expirada o token invalido. Haz login nuevamente.");
    }
    if (normalized.kind === "forbidden") {
      throw new Error("No tienes permisos para esta operacion (RBAC).");
    }
    throw new Error(normalized.message);
  }
}
```

### Login real del backend (mutation `login`)

```js
const LOGIN_MUTATION = `
  mutation Login($email: String!, $password: String!) {
    login(login: { email: $email, password: $password }) {
      email
      token
    }
  }
`;

async function login(email, password) {
  const data = await gqlRequest(LOGIN_MUTATION, { email, password });
  saveToken(data.login.token);
  return data.login;
}
```

### Query protegida por `core.country.read`

```js
const GET_ALL_COUNTRIES = `
  query {
    getAllCountries {
      id
      code
      name
      phoneCode
      currencyId
    }
  }
`;

async function getCountries() {
  const data = await gqlRequest(GET_ALL_COUNTRIES);
  return data.getAllCountries;
}
```

### Mutation protegida por `core.country.create`

```js
const CREATE_COUNTRY = `
  mutation CreateCountry($payload: CountryInput!) {
    createCountry(payload: $payload) {
      id
      code
      name
      phoneCode
      currencyId
    }
  }
`;

async function createCountry(payload) {
  const data = await gqlRequest(CREATE_COUNTRY, { payload });
  return data.createCountry;
}
```

### Mutation protegida por `core.country.update`

```js
const UPDATE_COUNTRY = `
  mutation UpdateCountry($countryId: Int!, $payload: CountryInput!) {
    updateCountry(countryId: $countryId, payload: $payload) {
      id
      code
      name
      phoneCode
      currencyId
    }
  }
`;

async function updateCountry(countryId, payload) {
  const data = await gqlRequest(UPDATE_COUNTRY, { countryId, payload });
  return data.updateCountry;
}
```

### Ejecucion de ejemplo

```js
async function runExample() {
  try {
    await login("admin@demo.com", "123456");

    // Requiere permiso core.country.read
    const countries = await getCountries();
    console.log("Countries:", countries);

    // Requiere permiso core.country.create
    const created = await createCountry({
      code: "ZZ",
      name: "Pais Demo",
      phoneCode: "+999",
      currencyId: null,
    });
    console.log("Created:", created);

    // Requiere permiso core.country.update
    const updated = await updateCountry(created.id, {
      code: "ZZ",
      name: "Pais Demo Actualizado",
      phoneCode: "+999",
      currencyId: null,
    });
    console.log("Updated:", updated);
  } catch (e) {
    console.error(e.message);
  }
}

runExample();
```

### Permisos minimos esperados

- Para `getAllCountries`: `core.country.read` (o `core.country.*`, `core.*.read`, `core.*.*`, `*.*.*`)
- Para `createCountry`: `core.country.create` (o `core.country.*`, `core.*.*`, `*.*.*`)
- Para `updateCountry`: `core.country.update` (o `core.country.*`, `core.*.*`, `*.*.*`)
- Para `deleteCountry`: `core.country.delete` (o `core.country.*`, `core.*.*`, `*.*.*`)
- Para gestionar roles/permisos: `auth.admin`

## Demo real separado en archivos

Se incluyo una implementacion runnable en `demo/`:

- `demo/index.html`
- `demo/app.js`
- `demo/apiClient.js`
- `demo/auth.js`
- `demo/coreApi.js`
- `demo/storage.js`
- `demo/config.js`

Para probar rapido:

1. Levanta tu backend en `http://localhost:8000`.
2. Sirve la carpeta del proyecto con un servidor estatico (ejemplo):

```bash
python3 -m http.server 5500
```

3. Abre `http://localhost:5500/demo/index.html`.
