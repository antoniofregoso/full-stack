# Core Page JSON por GraphQL

## Objetivo

Permitir que `core_page` devuelva un `JSON` consultable desde GraphQL.

La idea es exponer configuraciones de página o vistas dinámicas para el frontend, por ejemplo:

- `home`
- `dashboard`
- `landing`
- configuraciones por `name`
- configuraciones por `keys`

## Enfoque recomendado

No meter la lógica de negocio dentro del modelo `CorePage`.

La estructura recomendada es:

1. `CorePage`
   - almacena el contenido en base de datos
   - campos útiles actuales:
     - `name`
     - `keys`
     - `view`
     - `public`

2. `repository`
   - consulta la página por `id`, `name` o `keys`

3. `service`
   - devuelve el `JSON` crudo o arma un `JSON` enriquecido

4. `graphql`
   - expone una query que regresa `JSON`

## Opciones de implementación

### Opción 1. Devolver `view` tal como está en BD

Uso:

- guardar en `core_pages.view` el JSON de la página
- consultar por GraphQL y devolver ese mismo objeto

Caso ideal cuando:

- el frontend ya sabe interpretar el JSON
- no hace falta transformación adicional

Ejemplo conceptual:

```python
@strawberry.field(permission_classes=[CoreReadAccess])
async def get_page_view_by_name(self, name: str) -> JSON | None:
    return await PageService.get_view_by_name(name)
```

## Opción 2. Armar JSON dinámico en service

Uso:

- tomar la data guardada en `CorePage`
- combinarla con lógica adicional
- devolver un JSON final al frontend

Caso ideal cuando:

- la página necesita composición dinámica
- quieres mezclar configuración, permisos, contexto o valores calculados

Ejemplo conceptual:

```python
class PageService:
    @staticmethod
    async def get_page_payload(name: str) -> dict | None:
        page = await PageRepository.get_by_name(name)
        if page is None:
            return None

        return {
            "name": page.name,
            "keys": page.keys,
            "view": page.view,
        }
```

## Recomendación para mañana

Empezar simple:

- crear una query nueva en GraphQL
- buscar la página por `name`
- devolver `page.view` como `JSON`

Después, si hace falta:

- agregar una segunda query por `keys`
- enriquecer el payload desde `service`

## Posible nombre de queries

- `getPageViewByName(name: str): JSON`
- `getPageViewByKeys(keys: JSON): JSON`
- `getPagePayloadByName(name: str): JSON`

## Nota importante

En Python/GraphQL aquí no sería `gson`, sino `JSON`.

En este proyecto ya se usa `JSON` de `strawberry.scalars`.

## Próximo paso sugerido

Mañana implementar:

1. método en `PageService`
2. query nueva en `app/core/graphql/query.py`
3. retorno `JSON`
4. prueba con una página como `home` o `dash`
