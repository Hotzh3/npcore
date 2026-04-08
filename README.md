# NPCore

Motor simple de simulación basado en reglas probabilísticas para agentes (NPCs).

## Descripción

Este proyecto implementa un sistema de toma de decisiones para agentes basado en:

- Estados (`state`)
- Contexto (`context`)
- Reglas probabilísticas

Cada NPC toma decisiones dinámicas dependiendo de su estado actual y la información disponible en su contexto.

## Objetivo

Simular comportamientos de agentes de forma flexible y extensible, permitiendo modelar decisiones no deterministas en distintos escenarios.

---

## ¿Cómo funciona?

El sistema se basa en tres componentes principales:

### Brain
Define las reglas de decisión.  
Cada regla recibe un contexto y devuelve un diccionario de probabilidades:

```python
{"acción": probabilidad}
```

### NPC
Representa un agente con:
- un estado actual
- un contexto dinámico
- un `Brain` que determina sus acciones

### Environment
Permite ejecutar múltiples NPCs en un entorno compartido y simular pasos en el tiempo.

---

## Estructura del proyecto

```plaintext
src/npcore/
  brain.py          # Lógica de decisión
  npc.py            # Definición del agente
  environment.py    # Entorno de simulación
  probability.py    # Utilidades probabilísticas

tests/
  test_npc.py
  test_environment.py
  test_probability.py

notebooks/
  demo.ipynb
  demo2.ipynb
```

---

## Instalación

Se recomienda usar un entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Uso básico

```python
from npcore.brain import Brain
from npcore.npc import NPC
from npcore.environment import Environment

# Crear brain
brain = Brain()

def simple_rule(ctx):
    return {"idle": 0.5, "walk": 0.5}

brain.add_rule("default", simple_rule)

# Crear NPC
npc = NPC("Guard", brain)
npc.set_state("default")

# Crear entorno
env = Environment()
env.add_npc(npc)

# Simular
result = env.step()
print(result)
```

---

## Demo

El proyecto incluye notebooks con ejemplos:

- `demo.ipynb`: introducción básica
- `demo2.ipynb`: ejemplos avanzados con múltiples NPCs y simulaciones

Para ejecutarlos:

```bash
jupyter notebook notebooks/demo2.ipynb
```

---

## Pruebas

Para ejecutar los tests:

```bash
pytest
```

---

## Aplicaciones

Este tipo de sistema puede utilizarse en:

- desarrollo de videojuegos
- simulaciones educativas
- prototipos de inteligencia artificial ligera
- modelado de agentes autónomos

---

## Posibles extensiones

- memoria interna del NPC
- interacción directa entre agentes
- mapas o sistemas de posición
- eventos dinámicos del entorno
- estrategias adaptativas

---


    
