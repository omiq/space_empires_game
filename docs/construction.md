# space_empires.construction

Ship and infrastructure building management.

```python
"""space_empires.construction"""
from dataclasses import dataclass

@dataclass
class ConstructionProject:
    id: int
    type: str
    cost: float
    progress: float = 0.0

def advance_construction(project: ConstructionProject, rate: float = 0.1):
    project.progress += rate
    return project.progress >= 1.0
```
