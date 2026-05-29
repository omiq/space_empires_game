# Space Battles

A faithful, modern remake of the classic *Super Star Trek* BASIC game, written in
Python for the terminal. It is deliberately line based (scrolling text, no
full-screen TUI) so it runs cleanly over telnet and inside a BBS door, not just in
a local shell.

You command the Enterprise across an 8x8 galaxy, hunting Klingons before the
stardate clock runs out. Navigate, scan, fire phasers and torpedoes, manage
shields and damage, and dock at starbases to repair and resupply.

## Status

Phase 1 in progress. The build target is the pseudocode in
`original specs/phase_1.md`, itself derived from the original
`reference/SUPERSTARTREK.bas`.

## Why line based

BBS doors and telnet sessions do not cope well with curses, cursor addressing, or
full-screen redraws. Keeping everything to plain `input()` and `print()` at 80
columns, with optional ANSI colour that can be turned off, means the same program
runs in a local terminal today and drops into a door or a telnet wrapper later
with no rewrite.

## Running

```bash
python3 space_battles.py
```

Optional flags:

```bash
python3 space_battles.py --seed 12345   # reproducible galaxy
python3 space_battles.py --no-color     # plain ASCII, no ANSI
```

## Commands

```
NAV  Navigate (course 1-9, warp factor)
SRS  Short-range scan of the current quadrant
LRS  Long-range scan of neighbouring quadrants
PHA  Fire phasers
TOR  Fire photon torpedoes
SHE  Shield control
DAM  Damage and repair report
COM  Library computer (maps, targeting, navigation)
XXX  Resign command
```

## Roadmap

Phase 1 is the only committed goal. Everything below it is a documented stretch
arc, not a promise.

- [x] Milestone 1: core loop (galaxy generation, short-range scan, navigation, status, win and lose checks)
- [x] Milestone 2: combat (phasers, torpedoes, enemy fire, shields, device damage)
- [x] Milestone 3: support commands (long-range scan, library computer, damage and shield control, docking and repair, end rating, replay)
- [x] Milestone 4: BBS and telnet polish (seed flag, ANSI toggle, clean EOF handling)

## Stretch: Space Empires

The original ambition was a full procedural space trading and empire simulation
(economy, agents, fleets, construction, politics, events) intended to seed a
persistent multiplayer universe. That design is preserved for reference and may be
built on later, but it is not the current focus.

- `original specs/` holds the v0.2 specification, system breakdown, and the
  earlier README.
- `docs/` holds per-module Python sketches for those future systems. They are
  notes, not active code.

## Layout

```
space_empires_game/
  space_battles.py        the Phase 1 game (Python, terminal)
  reference/              SUPERSTARTREK.bas, the original source
  original specs/         phase_1 build target and Space Empires v0.2 design
  docs/                   future Space Empires module sketches
```

## License

To be decided.
