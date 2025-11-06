# Space Empires System Breakdown (Specification v0.2)

## 1. Universe System
**Purpose:** Generate, store, and manage all star systems, planets, and interstellar relationships.

### Data Model
```yaml
System:
  id: int
  name: string
  coordinates: {x: int, y: int}
  star_type: string
  economy_type: string
  government_type: string
  population: int
  stability: int
  allegiance: string
  resources: {ore: int, gas: int}
  market: Market
  facilities:
    starport: bool
    shipyard: bool
    defense: int
  description: string
```

### Core Functions
```
generate_universe(seed, num_systems)
distance(system_a, system_b)
update_system(system)
```
---

## 2. Economy System
**Purpose:** Simulate production, consumption, and trading between systems.

### Data Model
```yaml
Market:
  goods: list[Good]

Good:
  name: string
  base_price: float
  base_quantity: int
  gradient: float
  mask: int
  units: string
  current_price: float
  quantity: int
```

### Core Functions
```
generate_market(system, fluct)
update_market(system)
trade_buy(agent, system, good, amount)
trade_sell(agent, system, good, amount)
```
---

## 3. Agent System
**Purpose:** Represent all active actors (player and AI).

### Data Model
```yaml
Agent:
  id: int
  name: string
  faction: string
  role: [player, trader, pirate, governor]
  credits: float
  home_system: int
  current_system: int
  ships: list[Ship]
  cargo: {good: int}
  fuel: float
  reputation: {faction: int}
```

### Core Logic
```
update_agents(universe)
ai_take_turn(agent)
```
---

## 4. Fleet and Ship System
**Purpose:** Handle movement, upgrades, combat readiness, and construction.

### Data Model
```yaml
Ship:
  id: int
  name: string
  type: string
  hull: int
  shields: int
  weapons: list[Weapon]
  cargo_capacity: int
  fuel_capacity: float
  engine_level: int
  owner: int
  location: int
  build_progress: float
  status: [active, damaged, under_construction]

Weapon:
  name: string
  damage: int
  accuracy: float
  range: int
```

### Core Functions
```
travel(ship, destination_system)
build_ship(system, blueprint)
upgrade_ship(ship, upgrade)
repair_ship(ship)
```
---

## 5. Combat System
**Purpose:** Resolve encounters between fleets.

### Data Model
```yaml
Combat:
  attackers: list[Ship]
  defenders: list[Ship]
  location: int
  round: int
```

### Core Functions
```
resolve_combat(combat)
apply_damage(ship, target)
remove_destroyed_ships()
```
---

## 6. Construction & Upgrade System
**Purpose:** Manage building and upgrades for ships and infrastructure.

### Data Model
```yaml
ConstructionProject:
  id: int
  type: [ship, starbase, upgrade]
  blueprint_id: int
  owner_id: int
  system_id: int
  progress: float
  cost: float
  completion_time: int
```

### Core Functions
```
start_construction(owner, system, blueprint)
advance_construction(project)
complete_construction(project)
```
---

## 7. Politics & Rebellion System
**Purpose:** Model allegiance, unrest, and political control.

### Data Model
```yaml
Faction:
  id: int
  name: string
  attitude_toward: {faction_id: int}
  treasury: float
  systems_owned: list[int]

System.stability: int (0–100)

RebellionEvent:
  system_id: int
  cause: string
  rebel_faction_id: int
  progress: float
```

### Core Logic
```
update_politics(universe)
calc_stability(system)
start_rebellion(system)
```
---

## 8. Event System
**Purpose:** Spawn random or triggered events that affect systems or factions.

### Core Functions
```
generate_event()
apply_event_to_system(event, system)
expire_event(event)
```
---

## 9. Save / Load System
**Purpose:** Serialize and restore full game state.

### Core Functions
```
save_game(universe, filename)
load_game(filename)
```
---

## 10. Game Loop Integration
**Main Loop:**
```
while game_running:
    update_market()
    update_agents()
    resolve_combat()
    update_politics()
    update_construction()
    check_and_spawn_events()
    process_player_input()
    autosave()
```
---

## 11. Extensibility Hooks
| Hook | Purpose |
|------|----------|
| on_system_generated(system) | Custom lore or names |
| on_ai_turn(agent, universe) | Swap AI logic modules |
| on_trade_completed(agent, system, good) | Analytics or missions |
| on_battle_end(winner, loser) | Diplomacy effects |
| on_rebellion(system) | Trigger story or news events |
