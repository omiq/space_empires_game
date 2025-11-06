# space_empires.agents

Manages player and AI agents.

```python
"""space_empires.agents"""
import random
from dataclasses import dataclass, field

@dataclass
class Agent:
    id: int
    name: str
    role: str  # 'player', 'trader', 'pirate'
    credits: float
    cargo: dict[str, int] = field(default_factory=dict)
    location: int = 0

def ai_take_turn(agent, universe, economy):
    if agent.role == "trader":
        # Simplified logic
        if random.random() < 0.5:
            print(f"{agent.name} trades locally at system {agent.location}")
        else:
            agent.location = random.randint(0, len(universe.systems) - 1)
            print(f"{agent.name} travels to system {agent.location}")
```
