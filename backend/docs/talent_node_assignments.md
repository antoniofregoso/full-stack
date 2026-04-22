# Talent Node Assignments

Este documento explica la nueva ubicacion de las asignaciones humanas sobre la taxonomia.

Guia practica complementaria:

- [Guia de uso de asignaciones](/home/antoniofregoso/Desarrollo/full_stack/cj-backend/docs/assignment_usage_guide.md)

## Objetivo

Antes, varios nodos de `core` guardaban:

- `user_id`
- `users_ids`

Eso mezclaba estructura base del sistema con relaciones humanas de trabajo.

Ahora esa responsabilidad vive en `talent_node_assignments`.

## Idea central

`core` define la taxonomia:

- system
- team
- module
- entity
- feature
- action

`talent` define quienes trabajan o son responsables de cada nodo.

## Modelo

Tabla:

- `talent_node_assignments`

Campos principales:

- `user_id`
- `node_type`
- `node_id`
- `job_title`
- `description`
- `is_ai_agent`
- `is_primary`
- `active`

## Formato de `job_title`

`job_title` ahora es un JSON multilenguaje.

Ejemplo:

```json
{
  "es_MX": "Responsable",
  "en_US": "Owner"
}
```

Si no se envia valor, se guarda como `{}`.

## Formato de `description`

`description` tambien es JSON multilenguaje y sirve para documentar responsabilidades.

Ejemplo:

```json
{
  "es_MX": "Define metas del modulo y da seguimiento al equipo",
  "en_US": "Defines module goals and follows up with the team"
}
```

Si no se envia valor, se guarda como `{}`.

## Equivalencia con el esquema anterior

- `user_id` antiguo
  - ahora se representa con una asignacion `is_primary = true`

- `users_ids` antiguo
  - ahora se representa con multiples filas en `talent_node_assignments`

## Tipos de nodo soportados

- `SYSTEM`
- `TEAM`
- `MODULE`
- `ENTITY`
- `FEATURE`
- `ACTION`

## Queries

```graphql
query {
  getAllTalentNodeAssignments {
    id
    userId
    nodeType
    nodeId
    jobTitle
    description
    isAiAgent
    isPrimary
    active
  }
}
```

```graphql
query {
  getTalentNodeAssignmentsByUser(userId: 10) {
    id
    nodeType
    nodeId
    isPrimary
  }
}
```

```graphql
query {
  getTalentNodeAssignmentsByNode(nodeType: MODULE, nodeId: 3) {
    userId
    jobTitle
    description
    isAiAgent
    isPrimary
  }
}
```

## Mutations

```graphql
mutation {
  createTalentNodeAssignment(
    payload: {
      userId: 10
      nodeType: MODULE
      nodeId: 3
      jobTitle: {
        es_MX: "Responsable"
        en_US: "Owner"
      }
      description: {
        es_MX: "Responsable de resultados y roadmap"
        en_US: "Responsible for outcomes and roadmap"
      }
      isAiAgent: false
      isPrimary: true
      active: true
    }
  ) {
    id
    userId
    nodeType
    nodeId
    jobTitle
    description
    isAiAgent
    isPrimary
  }
}
```

Respuesta ejemplo:

```json
{
  "data": {
    "createTalentNodeAssignment": {
      "id": 1,
      "userId": 10,
      "nodeType": "MODULE",
      "nodeId": 3,
      "jobTitle": {
        "es_MX": "Responsable",
        "en_US": "Owner"
      },
      "description": {
        "es_MX": "Responsable de resultados y roadmap",
        "en_US": "Responsible for outcomes and roadmap"
      },
      "isAiAgent": false,
      "isPrimary": true
    }
  }
}
```

## Regla de primaria

Si una asignacion nueva o actualizada llega con `isPrimary = true`, el sistema limpia la bandera primaria de las demas asignaciones del mismo nodo.

## Jerarquia lista para graficar

Para pintar el organigrama funcional con personas asignadas puedes usar:

- `getTalentHierarchy(includeInactive: false)`

La respuesta viene en forma de arbol:

- `SYSTEM`
- `TEAM`
- `MODULE`
- `ENTITY`

Cada nodo incluye:

- metadatos del nodo (`code`, `name`, `description`, `active`)
- `assignments` del nodo (`jobTitle`, `description`, `isAiAgent`, `isPrimary`)
- `children` con sus descendientes

## Impacto arquitectonico

- `core` queda mas limpio y mas estable
- `talent` absorbe la semantica laboral u organizacional
- RBAC sigue separado
- `core_user_assignments` sigue separado para alcance funcional y landing path
