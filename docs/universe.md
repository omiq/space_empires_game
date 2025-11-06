# space_empires.universe

Handles star system generation, coordinates, and universe-wide updates.

```python
"""space_empires.universe"""
import random
from dataclasses import dataclass, field

@dataclass
class System:
    id: int
    name: str
    x: int
    y: int
    economy_type: str
    government_type: str
    population: int
    stability: int = 100
    allegiance: str = "neutral"
    description: str = ""

@dataclass
class Universe:
    seed: int
    systems: list[System] = field(default_factory=list)

    def generate(self, num_systems: int = 128):
        random.seed(self.seed)
        self.systems = [
            System(
                id=i,
                name=f"SYS-{i:03d}",
                x=random.randint(0, 255),
                y=random.randint(0, 255),
                economy_type=random.choice(["agricultural", "industrial", "mining"]),
                government_type=random.choice(["anarchy", "corporate", "democracy"]),
                population=random.randint(10**6, 10**9),
            )
            for i in range(num_systems)
        ]

    def distance(self, a: System, b: System) -> float:
        return ((a.x - b.x)**2 + (a.y - b.y)**2)**0.5
```
