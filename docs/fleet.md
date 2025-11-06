# space_empires.fleet

Ships, travel, and upgrades.

```python
"""space_empires.fleet"""
from dataclasses import dataclass, field

@dataclass
class Ship:
    id: int
    name: str
    hull: int
    fuel: float
    cargo_capacity: int
    location: int

def travel(ship: Ship, destination_id: int, cost: float = 1.0):
    if ship.fuel >= cost:
        ship.fuel -= cost
        ship.location = destination_id
        return True
    return False
```
