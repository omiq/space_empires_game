# space_empires.politics

System stability, allegiance, and rebellion.

```python
"""space_empires.politics"""
from dataclasses import dataclass

@dataclass
class Faction:
    id: int
    name: str
    treasury: float

def calc_stability(system) -> int:
    base = system.population / 1e6 - 10
    return int(max(0, min(100, base)))
```
