# Guia de uso de asignaciones (`core` + `talent`)

Este documento explica como usar las asignaciones del sistema en la practica.

## Que resuelve cada tabla

- `core_user_assignments`
  - define alcance funcional para navegacion y contexto operativo.
  - se usa para resolver `landing_path`.
  - guarda: `assignment_role`, `is_manager`, `active`.

- `talent_node_assignments`
  - define responsabilidad humana o de agente sobre nodos de la taxonomia.
  - se usa para organigrama funcional, responsables y roles por nodo.
  - guarda: `job_title`, `description`, `is_ai_agent`, `is_primary`, `active`.

- `auth` (RBAC)
  - define que puede hacer el usuario (`read`, `create`, `update`, `delete`, etc.).
  - no define jerarquia organizacional.

## Regla rapida de decision

- Usa `core_user_assignments` cuando la pregunta sea:
  - en que parte del arbol trabaja este usuario para navegar o filtrar datos.

- Usa `talent_node_assignments` cuando la pregunta sea:
  - quien es responsable de este nodo.
  - quien es principal.
  - cual es su puesto y responsabilidades.
  - si el asignado es humano o agente IA.

## `core_user_assignments`: como usar

### Restriccion importante

Cada fila debe tener exactamente un alcance:

- `system_id` o
- `team_id` o
- `module_id` o
- `entity_id`

No se deben combinar en la misma fila.

### Ejemplo de seed (`core_user_assignment.json`)

```json
[
  {
    "user_email": "admin@local.dev",
    "team_code": "software-implementation",
    "assignment_role": "administrator",
    "is_manager": true,
    "active": true
  }
]
```

### Queries utiles

```graphql
query {
  getUserAssignmentsByUser(userId: 1) {
    id
    userId
    systemId
    teamId
    moduleId
    entityId
    assignmentRole
    isManager
    active
    landingPath
  }
}
```

```graphql
query {
  getMyLandingPath
}
```

### Mutations utiles

```graphql
mutation {
  createUserAssignment(
    payload: {
      userId: 1
      moduleId: 3
      assignmentRole: "owner"
      isManager: true
      active: true
    }
  ) {
    id
    userId
    moduleId
    isManager
    landingPath
  }
}
```

## `talent_node_assignments`: como usar

### Campos clave

- `jobTitle`: nombre del puesto (JSON multilenguaje).
- `description`: responsabilidades del puesto (JSON multilenguaje).
- `isAiAgent`: `true` si la asignacion corresponde a un agente IA.
- `isPrimary`: responsable principal del nodo.

### Crear asignacion humana

```graphql
mutation {
  createTalentNodeAssignment(
    payload: {
      userId: 1
      nodeType: MODULE
      nodeId: 3
      jobTitle: { es_MX: "Lider de modulo", en_US: "Module Lead" }
      description: {
        es_MX: "Responsable de resultados del modulo"
        en_US: "Responsible for module outcomes"
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

### Crear asignacion de agente IA

```graphql
mutation {
  createTalentNodeAssignment(
    payload: {
      userId: 1
      nodeType: ENTITY
      nodeId: 10
      jobTitle: { es_MX: "Agente QA", en_US: "QA Agent" }
      description: {
        es_MX: "Valida flujos y reporta hallazgos"
        en_US: "Validates flows and reports findings"
      }
      isAiAgent: true
      isPrimary: false
      active: true
    }
  ) {
    id
    nodeType
    nodeId
    isAiAgent
    isPrimary
  }
}
```

### Obtener responsables de un nodo

```graphql
query {
  getTalentNodeAssignmentsByNode(nodeType: MODULE, nodeId: 3) {
    userId
    jobTitle
    description
    isAiAgent
    isPrimary
    active
  }
}
```

### Obtener jerarquia lista para graficar

```graphql
query {
  getTalentHierarchy(includeInactive: false) {
    nodeType
    nodeId
    code
    name
    description
    active
    assignments {
      userId
      jobTitle
      description
      isAiAgent
      isPrimary
      active
    }
    children {
      nodeType
      nodeId
      code
      name
      assignments {
        userId
        isPrimary
      }
      children {
        nodeType
        nodeId
        code
      }
    }
  }
}
```

## Flujo recomendado de implementacion

1. Asigna alcance funcional con `core_user_assignments`.
2. Asigna responsables y puestos con `talent_node_assignments`.
3. Calcula redireccion inicial con `getMyLandingPath`.
4. Dibuja organigrama con `getTalentHierarchy`.
5. Controla permisos de accion con RBAC (`auth`).

## Errores comunes a evitar

- Duplicar relaciones en tablas `core_*` con `user_id` directo.
- Usar `core_user_assignments` para modelar puesto laboral.
- Usar `talent_node_assignments` para permisos de seguridad.
- Marcar multiples primarios manualmente para el mismo nodo.
