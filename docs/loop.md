# space_empires.loop

Main simulation loop orchestrating updates.

```python
"""space_empires.loop"""
import time

def main_loop(universe, agents):
    tick = 0
    while tick < 10:  # demo loop
        print(f"--- Tick {tick} ---")
        for agent in agents:
            print(f"Updating agent {agent.name}")
        time.sleep(0.1)
        tick += 1
```
