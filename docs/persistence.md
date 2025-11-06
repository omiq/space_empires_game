# space_empires.persistence

Save/load and export utilities.

```python
"""space_empires.persistence"""
import json

def save_game(universe, filename):
    data = {"systems": [s.__dict__ for s in universe.systems]}
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def load_game(filename):
    with open(filename) as f:
        return json.load(f)
```
