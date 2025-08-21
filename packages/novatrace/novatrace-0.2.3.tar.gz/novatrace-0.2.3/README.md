NovaTrace

NovaTrace is a tracing solution for AI projects and language models (LLMs)
 that enables detailed logging and persistent storage of sessions, projects, 
 and execution traces. It is ideal for monitoring and auditing AI API calls, 
 agents, and tools with metrics such as token usage, costs, response times, 
 and more.

Features
Manages sessions and projects to organize traces.

Persistent logging with SQLAlchemy (supports SQLite and other databases).

Supports multiple trace types: LLM, Agent, and Tool.

Easy-to-use decorators to instrument functions (@llm, @agent, @tool).

Automatic token and cost calculation per call based on configurable metadata.

Timezone-aware timestamps for accurate logging.

---------------------------------------------------------------------------------------------------------------------------------

NovaTrace

NovaTrace es una solución de trazabilidad para proyectos de inteligencia artificial 
y modelos de lenguaje (LLM) que permite registrar y almacenar logs detallados de 
sesiones, proyectos y trazas de ejecución. Ideal para monitorear y auditar llamadas 
a APIs de IA, agentes y herramientas con métricas como tokens usados, costos, tiempos 
de respuesta y más.

Características
Gestión de sesiones y proyectos para organizar trazas.

Registro persistente en base de datos con SQLAlchemy (compatible con SQLite y otros motores).

Soporte para diferentes tipos de trazas: LLM, agentes y herramientas (tools).

Decoradores para instrumentar funciones fácilmente (@llm, @agent, @tool).

Cálculo automático de tokens y costos por llamada basados en metadata configurable.

Manejo de zonas horarias para registros con timestamps precisos.

Extensible y adaptable a distintos proveedores de modelos y entornos.