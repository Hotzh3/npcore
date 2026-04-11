# npcore

**npcore** es una librería en Python para simular NPCs (Non-Player Characters) inteligentes en entornos dinámicos.  
Permite modelar comportamiento autónomo mediante reglas, memoria, emociones, aprendizaje, interacción social y navegación espacial.

---

## Descripción

npcore implementa un sistema modular para construir agentes que:

- toman decisiones basadas en reglas
- aprenden de experiencias pasadas
- reaccionan a eventos del entorno
- interactúan con otros NPCs
- cooperan en grupos
- navegan en mapas con obstáculos y costos
- generan narrativas de su comportamiento

Está diseñada como una base para simulaciones, videojuegos, sistemas multi-agente y experimentación en comportamiento emergente.

---

## Instalación

Instala la librería directamente con pip:

```bash
pip install npcore 

## Para google colabr
Correr la linea !pip install npcore

## Uso básico
from npcore.brain import Brain
from npcore.npc import NPC
from npcore.environment import Environment

# Crear cerebro
brain = Brain()

def idle_rule(context):
    return {"run": 1.0, "wait": 1.0}

brain.add_rule("idle", idle_rule)

# Crear NPC
npc = NPC("Guard", brain)
npc.set_state("idle")

# Crear entorno
env = Environment(width=8, height=6)
env.add_npc(npc)

# Ejecutar simulación
env.run(steps=5)

# Ver resumen
print(env.summary())

## Características principales

Sistema de decisiones
	•	Motor de reglas (Brain)
	•	Estados dinámicos (idle, group, react, etc.)
	•	Selección probabilística de acciones

Memoria y aprendizaje
	•	Memoria estructurada de eventos
	•	Prioridad de memoria
	•	Aprendizaje basado en éxito de acciones
	•	Ajuste dinámico de decisiones

Personalidad y emociones
	•	Traits: agresión, sociabilidad, miedo, lealtad
	•	Estados emocionales que afectan decisiones

Interacción social
	•	Relaciones entre NPCs
	•	Comunicación entre aliados
	•	Sistema de órdenes (líder → grupo)
	•	Compartición de objetivos y prioridades

Comportamiento grupal
	•	Seguimiento de líder
	•	Reagrupamiento
	•	Coordinación de destino
	•	Reacción a eventos compartidos

Movimiento y entorno
	•	Pathfinding con A*
	•	Obstáculos en el mapa
	•	Zonas con costos de movimiento
	•	Evaluación de riesgo local
	•	Movimiento hacia objetivos

Sistema de eventos
	•	Eventos globales y locales
	•	Reacciones basadas en reglas
	•	Integración con módulos del entorno

Visualización
	•	Render ASCII del entorno
	•	Visualización con matplotlib
	•	Simulación paso a paso

Narrativa
	•	Generación de historia basada en acciones
	•	Resumen automático de la simulación

## Ejemplo completo
from npcore.environment import Environment
from npcore.npc import NPC
from npcore.brain import Brain

env = Environment(width=8, height=6)
brain = Brain()

def rule(context):
    return {"run": 1.0, "wait": 0.5}

brain.add_rule("idle", rule)

npc1 = NPC("Captain", brain)
npc2 = NPC("Guard", brain)

npc1.set_state("idle")
npc2.set_state("idle")

env.add_npc(npc1)
env.add_npc(npc2)

env.run(steps=5)

print(env.summary())


## Estructura del sistema

npcore está compuesto por los siguientes módulos:
	•	NPC: agente principal con estado, memoria, emociones y comportamiento
	•	Brain: motor de decisiones basado en reglas
	•	Environment: entorno donde interactúan los NPCs
	•	pathfinding: navegación con A*
	•	probability: selección probabilística de acciones
	•	story_engine: generación de narrativa

⸻

Casos de uso
	•	simulación de comportamiento de agentes
	•	prototipos de IA para videojuegos
	•	sistemas multi-agente
	•	experimentación académica
	•	modelado de interacción social
	•	análisis de comportamiento emergente

## Para ejecutar los más de 100 test
Correr pytest