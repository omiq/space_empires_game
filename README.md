# Space Empires

A modular, extensible **space trading and empire simulation** designed for single-player procedural play and later adaptation into a persistent multiplayer universe.

---

## Overview

**Space Empires** is built around a deterministic simulation loop inspired by classic games such as *Elite* and *Star Trek*, with additional systems for construction, politics, and AI-driven economy.  
The single-player version doubles as a *world generator* for a future shared-universe multiplayer build.

---

## Current Version
Specification: v0.2  
Modules: Universe, Economy, Agents, Fleet, Combat, Construction, Politics, Events, Persistence, Loop.

---

## Repository Structure

```
/docs                 # Markdown specifications and code skeletons
    universe.md
    economy.md
    agents.md
    fleet.md
    combat.md
    construction.md
    politics.md
    events.md
    persistence.md
    loop.md

/specs
    space_empires_spec_v0_2.md
    space_empires_system_breakdown_v0_2.md

.gitignore
README.md
```

---

## Getting Started

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```

2. Initialize the repository:

   ```bash
   git init
   git add .
   git commit -m "Initial commit - Space Empires v0.2"
   ```

3. Start building:
   - Implement classes from `/docs` into `/space_empires/` Python modules.
   - Use procedural generation to produce your first universe JSON.
   - Add CLI or REPL to interact with agents and markets.

---

## Roadmap

- [x] High-level design specification  
- [x] System breakdown and modular docs  
- [ ] Class implementation skeletons (next phase)  
- [ ] Single-player simulation loop  
- [ ] Construction and rebellion layers  
- [ ] Multiplayer server backend (FastAPI + PostgreSQL)

---

## License
To be decided (suggested: MIT or AGPL depending on multiplayer goals).

---

© 2025 Space Empires Project
