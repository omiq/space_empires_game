# Beyond Klingons: de-IP and the entity model

Living design note. Bridges finished Phase 1 (`space_battles.py`) and the Space
Empires stretch. Two goals, deliberately tackled together because they touch the
same code:

1. Drop all Paramount / Star Trek IP and reskin into our own universe.
2. Replace the single "Enterprise vs Klingons" model with a data-driven set of
   entity kinds, so adding a new ship or enemy is a table edit, not a code change.

Status: planned, not yet implemented. Phase 1 is committed and playable.

## 1. Why both at once

The current code hardcodes two things that block expansion:

- Display glyphs are stored *in the grid* and combat compares against them
  (`cell == KLINGON`). That dead-ends at a second enemy type.
- IP names are scattered as literals (`ENTERPRISE`, `KLINGON`, "Starfleet",
  "Federation", "photon torpedo", "stardate").

Fixing the entity model and the naming in one pass means we touch the grid,
combat loop, and constants once rather than twice.

## 2. De-IP naming table

Single source of truth for the reskin. Replacements are placeholders, swap for
your own lore. Keep the gameplay role identical; only names change.

| Role / current IP term | Replacement (proposed) | Notes |
|------------------------|------------------------|-------|
| Enterprise (player ship) | TBD flagship name | player `kind` |
| Klingon (enemy) | Raider / Corsair | hostile `kind` |
| Federation (player faction) | TBD | faction id |
| Starfleet (authority/voice) | TBD command | message flavour |
| Photon torpedo | Torpedo / Lance | keep generic |
| Phasers | Beam / Phaser (generic ok) | generic term is fine |
| Stardate | Cycle / Stardate (generic ok) | generic term is fine |
| Starbase | Station / Depot | resupply node |
| Quadrant / Sector | keep | generic grid terms |

Action: once names are chosen, every user-facing string pulls from a `THEME`
dict, so a future reskin is a one-place edit.

## 3. Entity dataclass

Promote the one-off `Klingon` class to a general entity. Stats do not live on
subclasses; they come from the content table (section 4) keyed by `kind`.

```python
from dataclasses import dataclass

@dataclass
class Entity:
    kind: str             # key into ENTITY_KINDS, e.g. "player", "raider"
    faction: str          # key into the hostility matrix
    row: int
    col: int
    shield: float = 0.0
    hull: float = 0.0     # for future multi-hit player/enemies
    alive: bool = True
```

Grid change: cells store an `Entity | None` (or `None` for empty), not a glyph
string. Rendering maps `entity.kind` to a glyph at print time (the colour path
already works this way).

## 4. Content table (data-driven kinds)

The heart of "more than Klingons". Add a row to add a thing.

```python
ENTITY_KINDS = {
    "player":   {"glyph": "<*>", "shield": 0,   "hostile_voice": False},
    "raider":   {"glyph": "+R+", "shield": 200, "fires": True},
    "corsair":  {"glyph": "+C+", "shield": 320, "fires": True},
    "trader":   {"glyph": "(=)", "shield": 60,  "fires": False, "tradeable": True},
    "station":  {"glyph": ">!<", "shield": 0,   "resupply": True},
    "star":     {"glyph": " * ", "blocks": True},
}
```

Open: shield ranges, weapon damage, AI aggressiveness, point value for scoring,
spawn weights for generation. Add columns as combat/economy grow.

## 5. Hostility matrix

Who fires on whom. Adding a faction is a table edit, not a code branch.

| Attacker \ Target | player | raiders | traders | authority |
|-------------------|--------|---------|---------|-----------|
| player            | -      | yes     | choice  | no        |
| raiders           | yes    | no      | yes     | yes       |
| traders           | no     | flee    | no      | no        |
| authority         | no     | yes     | no      | -         |

Combat loop becomes: for each entity that `fires`, target the nearest entity its
faction is hostile toward (today that is always the player, this generalises it).

## 6. Glyph and theme map

`kind -> glyph` is section 4. Colour already maps glyph -> ANSI in
`space_battles.py` (`ANSI_COLORS`). After the refactor, colour should key off
`kind` or faction instead of the glyph string, so reskins do not break colour.

## 7. Migration checklist (against current code)

In rough dependency order:

- [ ] Add `Entity` dataclass; convert `Klingon` usages.
- [ ] Grid stores `Entity | None`; add a render step mapping `kind` to glyph.
- [ ] Replace `cell == KLINGON` style checks with `entity.kind` / `entity.blocks`.
- [ ] Generalise enemy fire: iterate entities where `fires` is true, pick target
      via the hostility matrix (player-only today).
- [ ] Pull all IP strings into a `THEME` dict; apply the naming table.
- [ ] Move stats (shield ranges, etc.) out of generation code into `ENTITY_KINDS`.
- [ ] Update generation to place entities by `kind` with spawn weights.
- [ ] Re-key `ANSI_COLORS` off `kind`/faction rather than glyph.

Keep each step a separate small commit so Phase 1 stays a clean rollback point.

## 8. Open questions

- Do neutral entities (traders) move on their turn, or stay put for now?
- Can the player dock with or trade at friendly entities (ties into the economy
  stretch), or is interaction combat-only at first?
- Multiple player ships / a fleet later, or stay single-ship for Phase 1.5?
- Scoring: keep the single efficiency rating, or per-kind point values?
- How much of this anticipates the full Space Empires economy vs stays minimal?

## 9. Relationship to Space Empires

This is the smallest step that points at the bigger spec without committing to it.
The `Entity` + faction + data-table approach is the same shape the Space Empires
agent and fleet systems will want (see `docs/agents.md`, `docs/fleet.md`), so work
done here is not throwaway. We are not building the empire sim yet, just stopping
the Phase 1 model from being a dead end.
