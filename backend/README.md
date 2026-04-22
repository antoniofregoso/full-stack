# Backend API

Este proyecto es un backend moderno construido con **FastAPI**, **Strawberry GraphQL**, **SQLModel** y **PostgreSQL**.

## 🚀 Inicio Rápido con Docker (Recomendado)

Esta es la forma más fácil de ejecutar el proyecto, ya que configura la base de datos y la aplicación automáticamente.

1.  **Construir y levantar contenedores:**
    ```bash
    docker-compose up --build
    ```
    La API estará disponible en: [http://localhost:8000/graphql](http://localhost:8000/graphql)

2.  **Detener contenedores:**
    ```bash
    docker-compose down
    ```

---

## 🗄️ Inicialización de Base de Datos (Salida de la caja)

Este repositorio actualmente **no incluye migraciones versionadas** en `migrations/versions/`.  
Para una base de datos nueva, el flujo recomendado es crear tablas con `SQLModel` y luego cargar seeds.

> [!IMPORTANT]
> `scripts/init_db.py` intenta crear la base de datos automáticamente (a partir de `DB_CONFIG`) conectándose primero a `postgres`.
> Si el usuario de PostgreSQL no tiene permiso `CREATEDB`, crea la base manualmente con:
> ```bash
> psql -h localhost -U odoo -d postgres -c "CREATE DATABASE app_db;"
> ```

### 🐳 Usando Docker

Con contenedores arriba (`docker-compose up -d`), crea tablas y seeds así:

```bash
docker-compose exec web python3 scripts/init_db.py
```

### 💻 Ejecución Local (Sin Docker)

Si prefieres ejecutarlo en tu máquina (requiere Python 3.10+ y una base de datos PostgreSQL/SQLite corriendo):

1.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configurar entorno:**
    Crea un archivo `.env` basado en las variables requeridas en `settings.py` (DB_CONFIG, SECRET_KEY, etc).

3.  **Crear tablas y cargar seeds:**
    ```bash
    python3 scripts/init_db.py
    ```

4.  **Ejecutar servidor:**
    ```bash
    uvicorn main:app --reload
    ```

## 🛠️ Stack Tecnológico
*   **Framework**: FastAPI
*   **GraphQL**: Strawberry
*   **ORM**: SQLModel (SQLAlchemy + Pydantic)
*   **DB Schema Init**: SQLModel `create_all()`
*   **Auth**: JWT + Argon2
*   **Settings**: Pydantic Settings

## 📝 Logging y Observabilidad

El backend cuenta con un sistema de logging estructurado. Puedes controlar el nivel de detalle mediante la variable de entorno `LOG_LEVEL`.

**Niveles Disponibles:**
*   `DEBUG`: Máximo detalle (para desarrollo local).
*   `INFO`: Información general del funcionamiento (Recomendado por defecto).
*   `WARNING`: Solo advertencias (ej. intentos de login fallidos).
*   `ERROR`: Solo errores críticos.

**Cómo cambiarlo:**
*   **Docker**: Edita `docker-compose.yml` y cambia `LOG_LEVEL=INFO`.
*   **Local**: Añade `LOG_LEVEL=DEBUG` a tu archivo `.env`.

**Registro en archivo**
Puedes especificar una ruta para que los logs también se escriban en un archivo de texto. Ajusta la variable `LOG_FILE` en tu .env o en el entorno del contenedor. Si queda vacía o no existe, sólo se usará la consola.

```env
LOG_FILE=/var/log/miapp.log
```

## 🌱 Seeds iniciales

El proyecto carga datos base al arrancar la aplicación desde [main.py](/home/antoniofregoso/Desarrollo/full_stack/cj-backend/main.py), ejecutando:

```python
await seed_auth_users()
await seed_auth_roles()
await seed_auth_permissions()
await seed_auth_role_permissions()
await seed_core_langs()
await seed_core_currencies()
await seed_core_countries()
await seed_core_pages()
await seed_core_systems()
await seed_core_user_assignments()
```

Tambien puedes ejecutarlos manualmente sin levantar toda la API usando [seed.py](/home/antoniofregoso/Desarrollo/full_stack/cj-backend/seed.py).

### Ubicación

- Bootstrap de seeds: [app/core/service/core_bootstrap.py](/home/antoniofregoso/Desarrollo/full_stack/cj-backend/app/core/service/core_bootstrap.py)
- Seed de usuarios auth: [app/auth/data/auth_user.json](/home/antoniofregoso/Desarrollo/full_stack/cj-backend/app/auth/data/auth_user.json)
- Seed de roles auth: [app/auth/data/auth_role.json](/home/antoniofregoso/Desarrollo/full_stack/cj-backend/app/auth/data/auth_role.json)
- Seed de permisos auth: [app/auth/data/auth_permission.json](/home/antoniofregoso/Desarrollo/full_stack/cj-backend/app/auth/data/auth_permission.json)
- Seed de rol-permiso auth: [app/auth/data/auth_role_permission.json](/home/antoniofregoso/Desarrollo/full_stack/cj-backend/app/auth/data/auth_role_permission.json)
- Seed de idiomas: [app/core/data/core_lang.json](/home/antoniofregoso/Desarrollo/full_stack/cj-backend/app/core/data/core_lang.json)
- Seed de monedas: [app/core/data/core_currency.json](/home/antoniofregoso/Desarrollo/full_stack/cj-backend/app/core/data/core_currency.json)
- Seed de países y estados: [app/core/data/core_country.json](/home/antoniofregoso/Desarrollo/full_stack/cj-backend/app/core/data/core_country.json)
- Seed de páginas: [app/core/data/core_page.json](/home/antoniofregoso/Desarrollo/full_stack/cj-backend/app/core/data/core_page.json)
- Seed de sistemas y equipos: [app/core/data/core_system.json](/home/antoniofregoso/Desarrollo/full_stack/cj-backend/app/core/data/core_system.json)
- Seed de asignaciones de usuario: [app/core/data/core_user_assignment.json](/home/antoniofregoso/Desarrollo/full_stack/cj-backend/app/core/data/core_user_assignment.json)
- Runner manual: [seed.py](/home/antoniofregoso/Desarrollo/full_stack/cj-backend/seed.py)

### Ejecución manual

En local:

```bash
python3 seed.py
python3 seed.py all
python3 seed.py auth
python3 seed.py permissions
python3 seed.py langs
python3 seed.py currencies
python3 seed.py countries
python3 seed.py pages
python3 seed.py systems
python3 seed.py user_assignments
```

Con Docker:

```bash
docker-compose exec web python3 seed.py
docker-compose exec web python3 seed.py all
docker-compose exec web python3 seed.py auth
docker-compose exec web python3 seed.py permissions
docker-compose exec web python3 seed.py langs
docker-compose exec web python3 seed.py currencies
docker-compose exec web python3 seed.py countries
docker-compose exec web python3 seed.py pages
docker-compose exec web python3 seed.py systems
docker-compose exec web python3 seed.py user_assignments
```

### Orden recomendado para base nueva

Si acabas de recrear la base de datos:

```bash
python3 scripts/init_db.py
```

### Cómo funcionan las relaciones

Los seeds no dependen de ids fijos de base de datos.

- Las monedas se resuelven por `code`, por ejemplo `MXN`, `USD`, `EUR`.
- Los países se resuelven por `code`, por ejemplo `MX`, `US`, `FR`.
- Los estados se resuelven por la combinación `country_id + code`.

Durante la carga:

1. Se insertan o actualizan monedas por `code`.
2. Cada país usa `currency_code` y el bootstrap busca su `currency_id` real en base de datos.
3. Cada estado queda vinculado al país usando el `id` real del país, resuelto a partir de `country.code`.

Esto permite borrar y recrear la base de datos sin romper referencias entre monedas, países y estados.

### Formato de `core_country.json`

Cada país puede incluir sus estados anidados:

```json
[
  {
    "code": "MX",
    "name": {
      "es_MX": "Mexico",
      "en_US": "Mexico"
    },
    "phone_code": "+52",
    "currency_code": "MXN",
    "states": [
      {
        "code": "JAL",
        "name": {
          "es_MX": "Jalisco",
          "en_US": "Jalisco"
        }
      }
    ]
  }
]
```

### Formato de `auth_user.json`

Cada usuario auth puede incluir `avatar_url` de forma opcional:

```json
[
  {
    "name": "Administrator",
    "email": "admin@local.dev",
    "avatar_url": "https://example.com/avatars/admin.png",
    "password": "admin",
    "active": true,
    "theme": "system",
    "user_type": "HUMAN"
  }
]
```

### Reglas importantes

- `core_country.name` debe ser un objeto JSON con traducciones.
- `core_country_state.name` debe ser un objeto JSON con traducciones.
- `currency_code` debe existir previamente en `core_currency.json` o en la tabla `core_currencies`.
- Si un seed ya se ejecutó, no volverá a correr porque se registra en `core_seed_runs`.

Si quieres volver a ejecutar un seed ya marcado como ejecutado, tendrás que borrar su fila correspondiente en `core_seed_runs` o cambiar la clave de versión dentro de `core_bootstrap.py`.
