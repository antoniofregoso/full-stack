# Taxonomia empresarial de referencia

Este documento propone una taxonomia funcional base para organizar el backend como nucleo de multiples webapps.

La idea no es imponer una estructura rigida, sino definir un lenguaje comun para modelar:

- sistemas
- equipos
- modulos
- entidades
- features
- acciones
- permisos

Tambien se propone un lenguaje comun para evaluar el estado de avance de cada proceso empresarial respecto a su objetivo.

## Jerarquia recomendada

1. `Sistema`
2. `Equipo`
3. `Modulo`
4. `Entidad`
5. `Feature`
6. `Accion`

## Definiciones

### Sistema

Es un dominio grande del negocio.

Debe responder a una funcion mayor dentro de la empresa.

Ejemplos:

- `comercial`
- `finanzas`
- `operaciones`

### Equipo

Es una agrupacion funcional u organizacional dentro de un sistema.

Representa responsabilidad operativa.

Ejemplo:

- sistema `comercial`
- equipos `marketing`, `ventas`, `experiencia_cliente`

### Modulo

Es una unidad funcional de software o negocio que ya tiene sentido propio.

No suele ser el nivel minimo.

Debajo del modulo todavia pueden existir:

- entidades
- features
- procesos
- reglas
- acciones

## Estados operacionales

`core_system`, `core_team` y `core_module` representan procesos empresariales en distintos niveles de agregacion.

Por eso comparten un estado operacional basado en su relacion con el objetivo esperado.

Estados propuestos:

- `AHEAD`: adelantado respecto al objetivo. Color sugerido `azul`.
- `ON_TRACK`: en tiempo y forma. Color sugerido `verde`.
- `AT_RISK`: con desviacion o atraso recuperable. Color sugerido `amarillo`.
- `CRITICAL`: con atraso severo o incumplimiento relevante. Color sugerido `rojo`.

Estas opciones viven en infraestructura como seleccion compartida del sistema:

- `app/infrastructure/selections.py`

Lectura de negocio:

- `AHEAD`: va por encima del ritmo esperado.
- `ON_TRACK`: cumple lo esperado en tiempo y forma.
- `AT_RISK`: muestra senales de atraso o desalineacion, pero sigue siendo recuperable.
- `CRITICAL`: requiere intervencion prioritaria.

### Entidad

Es el objeto de datos principal dentro de un modulo.

Ejemplos:

- `lead`
- `quote`
- `invoice`
- `employee`

### Feature

Es una capacidad funcional concreta dentro de una entidad o del modulo que la contiene.

En frontend normalmente se representa como:

- seccion
- tab
- boton
- accion visible en pantalla

Ejemplos dentro de `quote`:

- `approval`
- `pdf_export`
- `clone`
- `versioning`

### Accion

Es la operacion permitida sobre un modulo o una entidad.

Ejemplos:

- `read`
- `create`
- `update`
- `delete`
- `approve`
- `export`

## Sistemas de referencia

### 1. Comercial

Objetivo:

- generar demanda
- convertir oportunidades
- sostener relacion con clientes

Equipos sugeridos:

- `marketing`
- `ventas`
- `experiencia_cliente`

Modulos comunes:

- `campaigns`
- `leads`
- `opportunities`
- `quotes`
- `orders`
- `customer_success`

Features posibles dentro de `quotes`:

- `approval`
- `pdf_export`
- `clone`
- `versioning`

Entidades tipicas:

- `campaign`
- `lead`
- `opportunity`
- `quote`
- `order`
- `customer_case`

### 2. Finanzas

Objetivo:

- registrar, controlar y analizar recursos economicos

Equipos sugeridos:

- `contabilidad`
- `tesoreria`
- `planeacion_financiera`

Modulos comunes:

- `invoicing`
- `accounts_receivable`
- `accounts_payable`
- `banking`
- `budgets`
- `tax`

Entidades tipicas:

- `invoice`
- `payment`
- `expense`
- `bank_statement`
- `budget`

### 3. Operaciones

Objetivo:

- ejecutar la entrega de valor diaria del negocio

Equipos sugeridos:

- `produccion`
- `logistica`
- `servicio`
- `calidad`

Modulos comunes:

- `work_orders`
- `inventory`
- `warehouse`
- `shipments`
- `maintenance`
- `quality_control`

Entidades tipicas:

- `work_order`
- `stock_move`
- `shipment`
- `service_ticket`
- `inspection`

### 4. Talento

Objetivo:

- gestionar personas, estructura y desarrollo humano

Equipos sugeridos:

- `reclutamiento`
- `desarrollo_humano`
- `nomina`
- `administracion_personal`

Modulos comunes:

- `candidates`
- `employees`
- `payroll`
- `attendance`
- `performance`
- `training`

Entidades tipicas:

- `candidate`
- `employee`
- `payroll_run`
- `attendance_record`
- `performance_review`

### 5. Informacion

Objetivo:

- gobernar datos, reportes y conocimiento organizacional

Equipos sugeridos:

- `bi`
- `documentacion`
- `gobierno_datos`

Modulos comunes:

- `dashboards`
- `reports`
- `documents`
- `knowledge_base`
- `master_data`

Entidades tipicas:

- `report`
- `dashboard`
- `document`
- `dataset`
- `master_record`

Nota:

Este sistema debe mantenerse separado de `Sistemas`.

- `Informacion` trata datos, conocimiento y analitica
- `Sistemas` trata software, infraestructura e integraciones

### 6. Tecnología

Objetivo:

- habilitar y operar la plataforma tecnologica

Equipos sugeridos:

- `desarrollo`
- `infraestructura`
- `seguridad`
- `soporte`

Modulos comunes:

- `applications`
- `integrations`
- `deployments`
- `monitoring`
- `identity_access`
- `support_desk`

Entidades tipicas:

- `application`
- `integration`
- `deployment`
- `incident`
- `access_policy`

### 7. Direccion y control

Objetivo:

- definir rumbo, alinear ejecucion y supervisar resultados

Equipos sugeridos:

- `direccion_general`
- `planeacion`
- `control_gestion`

Modulos comunes:

- `strategy`
- `okr`
- `governance`
- `management_reports`
- `portfolio`

Entidades tipicas:

- `strategic_goal`
- `initiative`
- `okr`
- `committee_decision`

Nota:

Este nombre se recomienda sobre `comando y control` por ser mas claro y menos ambiguo en contexto empresarial moderno.

### 8. Legal, cumplimiento y riesgo

Objetivo:

- proteger a la organizacion en lo juridico, regulatorio y de control

Equipos sugeridos:

- `legal`
- `compliance`
- `riesgo`
- `auditoria`

Modulos comunes:

- `contracts`
- `compliance_cases`
- `risk_register`
- `policies`
- `audits`

Entidades tipicas:

- `contract`
- `policy`
- `risk_item`
- `audit_finding`

## Como usar esta taxonomia en el backend

### Para naming

Conviene mantener nombres consistentes, en minusculas y orientados a dominio:

- sistema: `commercial`
- equipo: `sales`
- modulo: `quotes`
- entidad: `quote`
- feature: `approval`

### Para URLs

La URL base debe reflejar la taxonomia estructural del negocio, no toda la granularidad funcional.

Convencion recomendada:

```txt
/system/{system}/team/{team}/module/{module}/entity/{entity}
```

Ejemplo:

```txt
/system/comercial/team/marketing/module/ads/entity/facebook_ad
```

Regla:

- `system`, `team`, `module` y `entity` van en la URL
- `feature` y `action` se resuelven dentro de la pantalla de la entidad

Implementacion actual del nucleo:

- `core_systems`
- `core_teams`
- `core_modules`
- `core_entities`
- `core_features`
- `core_action`

### Para frontend

La entidad representa el punto de entrada funcional.

Dentro de esa pantalla:

- las `features` viven como secciones, tabs o botones
- las `actions` viven como operaciones concretas permitidas

Ejemplo en `facebook_ad`:

- entidad:
  - `facebook_ad`
- features en la pantalla:
  - `general`
  - `creative`
  - `audience`
  - `budget`
  - `publish`
- acciones:
  - `create`
  - `update`
  - `delete`
  - `publish`
  - `pause`

### Para permisos

Dos niveles posibles:

- simple por modulo
  - `core.read`
  - `core.update`
  - `auth.admin`

- especifico por dominio
  - `commercial.quotes.read`
  - `commercial.quotes.create`
  - `finance.invoicing.update`

### Para modelado de nuevas apps

Cada webapp puede vivir sobre uno o varios sistemas.

Ejemplos:

- app comercial
  - sistemas `comercial` e `informacion`
- app de people ops
  - sistemas `talento`, `informacion`, `sistemas`
- app directiva
  - sistemas `direccion_control`, `finanzas`, `informacion`

### Para asignar usuarios a la taxonomia

La pertenencia de usuarios no debe guardarse dentro de cada nodo.

En lugar de eso, usa una tabla pivote como:

- `core_user_assignments`

Con esa tabla puedes asignar un usuario a:

- un `system`
- un `team`
- un `module`
- un `feature`

Y mantener por separado:

- la estructura funcional
- la asignacion organizacional
- los permisos RBAC

### Para calcular donde inicia el usuario

El inicio del usuario debe resolverse al alcance mas especifico que tenga asignado, pero la URL final debe quedar a nivel `entity`.

Prioridad recomendada de resolucion:

1. `entity`
2. `feature`
3. `module`
4. `team`
5. `system`

Interpretacion:

- si un usuario ya tiene una asignacion directa a una entidad, inicia ahi
- si solo tiene `feature`, se resuelve la entidad padre de esa feature y se inicia ahi
- si solo tiene modulo, inicia en la entidad default de ese modulo
- si solo tiene equipo, inicia en el modulo y entidad default de ese equipo
- si solo tiene sistema, inicia en el modulo y entidad default de ese sistema

Para que esto funcione bien, despues conviene definir:

- entidad default por modulo
- modulo default por equipo
- modulo o entidad default por sistema

La implementacion actual ya expone `landing_path` calculado a nivel de `entity`.

## Regla de diseño practica

Cuando vayas a crear un nuevo modulo, intenta responder:

1. A que sistema pertenece
2. Que equipo lo opera
3. Cual es su modulo funcional
4. Cuales son sus entidades principales
5. Que acciones necesita
6. Si requiere ownership o administracion global

Con eso puedes decidir:

- modelos
- queries
- mutations
- permisos
- flujos administrativos

## Resumen corto

La estructura recomendada es:

- `Sistema` para dominio
- `Equipo` para responsabilidad
- `Modulo` para funcionalidad
- `Entidad` para datos
- `Accion` para permisos y operaciones

Y la taxonomia base propuesta es:

1. Comercial
2. Finanzas
3. Operaciones
4. Talento
5. Informacion
6. Sistemas
7. Direccion y control
8. Legal, cumplimiento y riesgo
