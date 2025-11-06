# space_empires.events

Random or triggered events.

```python
"""space_empires.events"""
import random
from dataclasses import dataclass

@dataclass
class Event:
    name: str
    target: str
    effect: str

def generate_event():
    names = ["trade boom", "pirate raid", "epidemic"]
    return Event(random.choice(names), "unknown", "temporary")
```
