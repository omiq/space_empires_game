#!/usr/bin/env python3
"""Space Battles: a terminal remake of the classic Super Star Trek.

Line based by design (plain input/print, 80 columns) so it runs over telnet
and inside a BBS door, not only in a local shell.

Milestone 1: galaxy generation, short-range scan, navigation, status, and the
win/lose checks. Combat and the support commands arrive in later milestones.
"""

import argparse
import math
import random
import sys

GALAXY_SIZE = 8
QUADRANT_SIZE = 8
SHIP_ENERGY_CAPACITY = 3000
TORPEDO_CAPACITY = 10
KLINGON_SHIELD_BASE = 200

DEVICE_NAMES = [
    "Warp engines",
    "Short-range sensors",
    "Long-range sensors",
    "Phaser control",
    "Photon tubes",
    "Damage control",
    "Shield control",
    "Library computer",
]

# Course vectors keyed 1-9 as (d_row, d_col). 9 wraps to 1, per phase_1 spec.
COURSE_VECTORS = {
    1: (0, 1),
    2: (-1, 1),
    3: (-1, 0),
    4: (-1, -1),
    5: (0, -1),
    6: (1, -1),
    7: (1, 0),
    8: (1, 1),
    9: (0, 1),
}

EMPTY = "   "
ENTERPRISE = "<*>"
KLINGON = "+K+"
STARBASE = ">!<"
STAR = " * "

ANSI_COLORS = {
    ENTERPRISE: "\033[1;36m",
    KLINGON: "\033[1;31m",
    STARBASE: "\033[1;32m",
    STAR: "\033[1;33m",
}
ANSI_RESET = "\033[0m"


class Klingon:
    def __init__(self, row, col, shield):
        self.row = row
        self.col = col
        self.shield = shield


class Game:
    def __init__(self, seed=None, color=True):
        self.rng = random.Random(seed)
        self.seed = seed
        self.color = color
        self.galaxy = [
            [(0, 0, 0) for _ in range(GALAXY_SIZE)] for _ in range(GALAXY_SIZE)
        ]
        self.charted = [
            [None for _ in range(GALAXY_SIZE)] for _ in range(GALAXY_SIZE)
        ]
        self.energy = SHIP_ENERGY_CAPACITY
        self.shields = 0
        self.torpedoes = TORPEDO_CAPACITY
        self.damage = [0] * len(DEVICE_NAMES)
        self.klingons_remaining = 0
        self.starbases_remaining = 0
        self.klingons_destroyed = 0
        self.docked = False
        self.destroyed = False

        self.qrow = self.rng.randint(0, GALAXY_SIZE - 1)
        self.qcol = self.rng.randint(0, GALAXY_SIZE - 1)
        self.srow = self.rng.randint(0, QUADRANT_SIZE - 1)
        self.scol = self.rng.randint(0, QUADRANT_SIZE - 1)

        self.mission_duration = self.rng.randint(25, 34)
        self.start_date = self.rng.randrange(2000, 4000, 100)
        self.stardate = float(self.start_date)

        self.grid = [[EMPTY] * QUADRANT_SIZE for _ in range(QUADRANT_SIZE)]
        self.klingons = []

        self._generate_galaxy()
        self._enter_quadrant()

    # Generation ---------------------------------------------------------

    def _generate_galaxy(self):
        for r in range(GALAXY_SIZE):
            for c in range(GALAXY_SIZE):
                kr = self.rng.random()
                if kr > 0.98:
                    klingons = 3
                elif kr > 0.95:
                    klingons = 2
                elif kr > 0.80:
                    klingons = 1
                else:
                    klingons = 0

                bases = 1 if self.rng.random() > 0.96 else 0
                stars = 1 + self.rng.randint(0, QUADRANT_SIZE - 1)

                self.galaxy[r][c] = (klingons, bases, stars)
                self.klingons_remaining += klingons
                self.starbases_remaining += bases

        if self.starbases_remaining == 0:
            k, _, s = self.galaxy[self.qrow][self.qcol]
            self.galaxy[self.qrow][self.qcol] = (k, 1, s)
            self.starbases_remaining = 1

    def _empty_sectors(self):
        return [
            (r, c)
            for r in range(QUADRANT_SIZE)
            for c in range(QUADRANT_SIZE)
            if self.grid[r][c] == EMPTY
        ]

    def _enter_quadrant(self):
        self.grid = [[EMPTY] * QUADRANT_SIZE for _ in range(QUADRANT_SIZE)]
        self.klingons = []
        klingons, bases, stars = self.galaxy[self.qrow][self.qcol]
        self.charted[self.qrow][self.qcol] = (klingons, bases, stars)

        self.grid[self.srow][self.scol] = ENTERPRISE

        for _ in range(stars):
            free = self._empty_sectors()
            if not free:
                break
            r, c = self.rng.choice(free)
            self.grid[r][c] = STAR

        for _ in range(bases):
            free = self._empty_sectors()
            if not free:
                break
            r, c = self.rng.choice(free)
            self.grid[r][c] = STARBASE

        for _ in range(klingons):
            free = self._empty_sectors()
            if not free:
                break
            r, c = self.rng.choice(free)
            shield = KLINGON_SHIELD_BASE * (0.5 + self.rng.random())
            self.grid[r][c] = KLINGON
            self.klingons.append(Klingon(r, c, shield))

        self._update_docked()

    def _update_docked(self):
        self.docked = False
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                r, c = self.srow + dr, self.scol + dc
                if 0 <= r < QUADRANT_SIZE and 0 <= c < QUADRANT_SIZE:
                    if self.grid[r][c] == STARBASE:
                        self.docked = True
                        return

    # Display ------------------------------------------------------------

    def short_range_scan(self):
        if self.damage[1] < 0:
            print("*** Short-range sensors are damaged ***")
            return
        print()
        klingons, bases, _ = self.galaxy[self.qrow][self.qcol]
        header = "-" * (QUADRANT_SIZE * 3 + 2)
        print(header)
        for r in range(QUADRANT_SIZE):
            row = "".join(self._render_cell(self.grid[r][c]) for c in range(QUADRANT_SIZE))
            line = "|" + row + "|"
            print(self._status_line(r, line))
        print(header)

    def _render_cell(self, token):
        if self.color and token in ANSI_COLORS:
            return ANSI_COLORS[token] + token + ANSI_RESET
        return token

    def _status_line(self, row_index, grid_line):
        labels = [
            f"Stardate   {self.stardate:8.1f}",
            f"Quadrant   {self.qrow + 1},{self.qcol + 1}",
            f"Sector     {self.srow + 1},{self.scol + 1}",
            f"Energy     {self.energy:8.0f}",
            f"Shields    {self.shields:8.0f}",
            f"Torpedoes  {self.torpedoes:8d}",
            f"Klingons   {self.klingons_remaining:8d}",
            f"Docked     {'yes' if self.docked else 'no'}",
        ]
        extra = labels[row_index] if row_index < len(labels) else ""
        return f"{grid_line}   {extra}"

    # Commands -----------------------------------------------------------

    def navigate(self):
        print("""

 ENTER A NUMBER       4  3  2
 BETWEEN 1 AND 9       . . .
                        ...
 DECIMALS MAY BE    5 ---*--- 1
 USED (EG. 8.57)        ...
                       . . .
                      6  7  8

        """)
        course = self._ask_float("Course (1-9)? ")
        if course is None:
            return
        if not (1 <= course <= 9):
            print("   Invalid course.")
            return

        max_warp = 8.0
        if self.damage[0] < 0:
            max_warp = 0.2
        warp = self._ask_float(f"Warp factor (0-{max_warp:g})? ")
        if warp is None:
            return
        if warp <= 0:
            return
        if warp > max_warp:
            print(f"   Warp engines damaged, limited to {max_warp:g}.")
            warp = max_warp

        d_row, d_col = self._course_vector(course)
        steps = int(round(warp * 8))
        energy_cost = steps + 10
        if energy_cost > self.energy + self.shields:
            print("   Insufficient energy for that maneuver.")
            return

        self._move(d_row, d_col, steps)

        self.energy -= energy_cost
        if self.energy < 0:
            shortfall = -self.energy
            self.energy = 0
            self.shields = max(0, self.shields - shortfall)

        self.stardate += max(1, steps) / 8.0
        was_docked = self.docked
        self._update_docked()
        if self.docked and not was_docked:
            self._resupply()
        elif self.klingons and not self.docked:
            self.klingons_fire()

    def _course_vector(self, course):
        low = int(course)
        high = low + 1 if low < 9 else 9
        frac = course - low
        lr, lc = COURSE_VECTORS[low]
        hr, hc = COURSE_VECTORS[high]
        return (lr + (hr - lr) * frac, lc + (hc - lc) * frac)

    def _move(self, d_row, d_col, steps):
        self.grid[self.srow][self.scol] = EMPTY
        row = float(self.srow)
        col = float(self.scol)
        for _ in range(max(1, steps)):
            row += d_row
            col += d_col
            r, c = int(round(row)), int(round(col))

            if not (0 <= r < QUADRANT_SIZE and 0 <= c < QUADRANT_SIZE):
                self._cross_quadrant(row, col)
                return

            if self.grid[r][c] != EMPTY:
                print(f"   Obstacle in sector {r + 1},{c + 1}. Stopped.")
                row, col = self.srow, self.scol
                break
            self.srow, self.scol = r, c

        self.grid[self.srow][self.scol] = ENTERPRISE

    def _cross_quadrant(self, row, col):
        nq_row = self.qrow + (1 if row >= QUADRANT_SIZE else -1 if row < 0 else 0)
        nq_col = self.qcol + (1 if col >= QUADRANT_SIZE else -1 if col < 0 else 0)

        self.qrow = max(0, min(GALAXY_SIZE - 1, nq_row))
        self.qcol = max(0, min(GALAXY_SIZE - 1, nq_col))
        self.srow = int(max(0, min(QUADRANT_SIZE - 1, round(row % QUADRANT_SIZE))))
        self.scol = int(max(0, min(QUADRANT_SIZE - 1, round(col % QUADRANT_SIZE))))
        self._enter_quadrant()
        print(f"   Now entering quadrant {self.qrow + 1},{self.qcol + 1}.")

    def long_range_scan(self):
        if self.damage[2] < 0:
            print("*** Long-range sensors are damaged ***")
            return
        print()
        print(f"Long-range scan, quadrant {self.qrow + 1},{self.qcol + 1}:")
        for dr in (-1, 0, 1):
            cells = []
            for dc in (-1, 0, 1):
                r, c = self.qrow + dr, self.qcol + dc
                if 0 <= r < GALAXY_SIZE and 0 <= c < GALAXY_SIZE:
                    k, b, s = self.galaxy[r][c]
                    self.charted[r][c] = (k, b, s)
                    cells.append(f"{k}{b}{s}")
                else:
                    cells.append("***")
            print("   " + "   ".join(cells))

    # Combat -------------------------------------------------------------

    def _distance(self, r1, c1, r2, c2):
        return ((r1 - r2) ** 2 + (c1 - c2) ** 2) ** 0.5

    def _destroy_klingon(self, k):
        self.grid[k.row][k.col] = EMPTY
        self.klingons.remove(k)
        self.klingons_remaining -= 1
        self.klingons_destroyed += 1
        self._adjust_quadrant_count(klingons_delta=-1)

    def _adjust_quadrant_count(self, klingons_delta=0, bases_delta=0):
        k, b, s = self.galaxy[self.qrow][self.qcol]
        k = max(0, k + klingons_delta)
        b = max(0, b + bases_delta)
        self.galaxy[self.qrow][self.qcol] = (k, b, s)
        self.charted[self.qrow][self.qcol] = (k, b, s)

    def fire_phasers(self):
        if self.damage[3] < 0:
            print("*** Phaser control is damaged ***")
            return
        if not self.klingons:
            print("   No enemy ships in this quadrant.")
            return
        amount = self._ask_float(f"Phaser energy to fire (you have {self.energy:.0f})? ")
        if amount is None or amount <= 0:
            return
        if amount > self.energy:
            print("   You do not have that much energy.")
            return

        self.energy -= amount
        per_target = amount / len(self.klingons)
        for k in list(self.klingons):
            dist = max(0.5, self._distance(self.srow, self.scol, k.row, k.col))
            hit = (per_target / dist) * self.rng.uniform(1, 3)
            k.shield -= hit
            print(
                f"   {hit:.0f} unit hit on Klingon at sector "
                f"{k.row + 1},{k.col + 1} (shield {max(0, k.shield):.0f})."
            )
            if k.shield <= 0:
                print(f"   *** Klingon at {k.row + 1},{k.col + 1} destroyed ***")
                self._destroy_klingon(k)

        self.klingons_fire()

    def fire_torpedo(self):
        if self.damage[4] < 0:
            print("*** Photon tubes are damaged ***")
            return
        if self.torpedoes <= 0:
            print("   No torpedoes left.")
            return
        course = self._ask_float("Torpedo course (1-9)? ")
        if course is None:
            return
        if not (1 <= course <= 9):
            print("   Invalid course.")
            return

        self.torpedoes -= 1
        d_row, d_col = self._course_vector(course)
        row, col = float(self.srow), float(self.scol)
        while True:
            row += d_row
            col += d_col
            r, c = int(round(row)), int(round(col))
            if not (0 <= r < QUADRANT_SIZE and 0 <= c < QUADRANT_SIZE):
                print("   Torpedo missed, left the quadrant.")
                break
            cell = self.grid[r][c]
            print(f"   Torpedo track {r + 1},{c + 1}")
            if cell == KLINGON:
                hit = next(k for k in self.klingons if k.row == r and k.col == c)
                print(f"   *** Klingon at {r + 1},{c + 1} destroyed ***")
                self._destroy_klingon(hit)
                break
            if cell == STARBASE:
                print("   *** You destroyed a starbase! Starfleet is furious. ***")
                self.grid[r][c] = EMPTY
                self.starbases_remaining -= 1
                self._adjust_quadrant_count(bases_delta=-1)
                break
            if cell == STAR:
                print(f"   Star at {r + 1},{c + 1} absorbed the torpedo.")
                break

        self.klingons_fire()

    def shield_control(self):
        if self.damage[6] < 0:
            print("*** Shield control is damaged ***")
            return
        pool = self.energy + self.shields
        print(f"   Shields {self.shields:.0f}, energy {self.energy:.0f} (combined {pool:.0f}).")
        target = self._ask_float("Set shields to? ")
        if target is None:
            return
        if target < 0 or target > pool:
            print("   Cannot allocate that amount.")
            return
        self.energy = pool - target
        self.shields = target
        print(f"   Shields now {self.shields:.0f}, energy {self.energy:.0f}.")

    def klingons_fire(self):
        if not self.klingons:
            return
        for k in self.klingons:
            dist = max(0.5, self._distance(self.srow, self.scol, k.row, k.col))
            hit = (k.shield / dist) * self.rng.uniform(1, 3)
            self.shields -= hit
            print(
                f"   {hit:.0f} unit hit from Klingon at "
                f"{k.row + 1},{k.col + 1} (shields {max(0, self.shields):.0f})."
            )
            if self.shields < 0:
                self.energy += self.shields
                self.shields = 0
            if self.energy <= 0:
                self.energy = 0
                self.destroyed = True
                print("   *** The Enterprise has been destroyed ***")
                return
            if hit > 20 and self.rng.random() < 0.6:
                self._random_device_damage()

    def _random_device_damage(self):
        device = self.rng.randint(0, len(DEVICE_NAMES) - 1)
        self.damage[device] = -self.rng.randint(1, 5)
        print(f"   *** {DEVICE_NAMES[device]} damaged ***")

    # Support ------------------------------------------------------------

    def _resupply(self):
        self.energy = SHIP_ENERGY_CAPACITY
        self.torpedoes = TORPEDO_CAPACITY
        print("   Docked at starbase. Energy and torpedoes replenished.")

    def damage_control(self):
        if self.damage[5] < 0 and not self.docked:
            print("*** Damage control is offline ***")
            return
        print()
        print("   Device status:")
        any_damage = False
        for i, name in enumerate(DEVICE_NAMES):
            state = "operational" if self.damage[i] >= 0 else f"damaged ({self.damage[i]})"
            if self.damage[i] < 0:
                any_damage = True
            print(f"     {name:<22} {state}")
        if not any_damage:
            print("   All systems operational.")
            return
        if self.docked:
            repair_time = sum(-d for d in self.damage if d < 0) * 0.1
            self.damage = [0] * len(DEVICE_NAMES)
            self.stardate += repair_time
            print(f"   Repairs complete at starbase (took {repair_time:.1f} stardays).")
        else:
            print("   Dock at a starbase to effect repairs.")

    def library_computer(self):
        if self.damage[7] < 0:
            print("*** Library computer is damaged ***")
            return
        print()
        print("   1. Galaxy map")
        print("   2. Status report")
        print("   3. Photon torpedo targeting")
        print("   4. Nearest starbase")
        print("   5. Distance calculator")
        choice = self._read("   Option? ")
        if choice == "1":
            self._com_galaxy_map()
        elif choice == "2":
            self._com_status_report()
        elif choice == "3":
            self._com_targeting()
        elif choice == "4":
            self._com_nearest_base()
        elif choice == "5":
            self._com_distance()
        else:
            print("   Cancelled.")

    def _com_galaxy_map(self):
        print("   Charted galaxy (Klingons / bases / stars):")
        for r in range(GALAXY_SIZE):
            cells = []
            for c in range(GALAXY_SIZE):
                known = self.charted[r][c]
                cells.append("%d%d%d" % known if known else "...")
            print("   " + " ".join(cells))

    def _com_status_report(self):
        remaining = self.start_date + self.mission_duration - self.stardate
        print(f"   Klingons remaining:  {self.klingons_remaining}")
        print(f"   Starbases remaining: {self.starbases_remaining}")
        print(f"   Stardays left:       {remaining:.1f}")

    def _com_targeting(self):
        if not self.klingons:
            print("   No enemy ships in this quadrant.")
            return
        for k in self.klingons:
            course = self._course_from_delta(k.row - self.srow, k.col - self.scol)
            dist = self._distance(self.srow, self.scol, k.row, k.col)
            print(
                f"   Klingon at {k.row + 1},{k.col + 1}: "
                f"course {course:.1f}, distance {dist:.1f}"
            )

    def _com_nearest_base(self):
        best = None
        for r in range(GALAXY_SIZE):
            for c in range(GALAXY_SIZE):
                if self.galaxy[r][c][1] > 0:
                    d = self._distance(self.qrow, self.qcol, r, c)
                    if best is None or d < best[0]:
                        best = (d, r, c)
        if best is None:
            print("   No starbases remain in the galaxy.")
            return
        _, r, c = best
        if (r, c) == (self.qrow, self.qcol):
            print("   A starbase is in your current quadrant.")
            return
        course = self._course_from_delta(r - self.qrow, c - self.qcol)
        print(
            f"   Nearest starbase in quadrant {r + 1},{c + 1}: "
            f"course {course:.1f}, distance {best[0]:.1f} quadrants."
        )

    def _com_distance(self):
        a = self._read("   From row,col? ")
        b = self._read("   To row,col? ")
        try:
            r1, c1 = (int(x) - 1 for x in a.split(","))
            r2, c2 = (int(x) - 1 for x in b.split(","))
        except (ValueError, AttributeError):
            print("   Enter coordinates as row,col (for example 3,4).")
            return
        course = self._course_from_delta(r2 - r1, c2 - c1)
        print(f"   Course {course:.1f}, distance {self._distance(r1, c1, r2, c2):.1f}.")

    def _course_from_delta(self, d_row, d_col):
        if d_row == 0 and d_col == 0:
            return 0.0
        angle = math.degrees(math.atan2(-d_row, d_col)) % 360
        return 1 + angle / 45.0

    # Loop ---------------------------------------------------------------

    def _ask_float(self, prompt):
        raw = self._read(prompt)
        if raw is None:
            return None
        try:
            return float(raw)
        except ValueError:
            print("   Please enter a number.")
            return None

    def _read(self, prompt):
        try:
            return input(prompt).strip()
        except EOFError:
            return None

    def play(self):
        print("=" * 60)
        print(" SPACE BATTLES")
        deadline = self.start_date + self.mission_duration
        print(
            f" Destroy {self.klingons_remaining} Klingon ships before "
            f"stardate {deadline}."
        )
        print(f" Starbases available: {self.starbases_remaining}")
        print("=" * 60)
        self.short_range_scan()

        commands = {
            "NAV": self.navigate,
            "SRS": self.short_range_scan,
            "LRS": self.long_range_scan,
            "PHA": self.fire_phasers,
            "TOR": self.fire_torpedo,
            "SHE": self.shield_control,
            "DAM": self.damage_control,
            "COM": self.library_computer,
        }

        while True:
            cmd = self._read("\nCommand (NAV SRS LRS PHA TOR SHE DAM COM XXX)? ")
            if cmd is None:
                print("\nConnection closed. Stand down.")
                return
            cmd = cmd.upper()

            if cmd == "XXX":
                print("Command resigned. The Federation is disappointed.")
                return
            action = commands.get(cmd)
            if action is None:
                print("   Unknown command.")
                continue
            action()

            result = self._check_status()
            if result is not None:
                self._endgame(result)
                return

    def _check_status(self):
        if self.destroyed:
            return "destroyed"
        if self.klingons_remaining <= 0:
            return "victory"
        if self.stardate > self.start_date + self.mission_duration:
            return "timeout"
        if self.energy <= 0 and not self.docked:
            return "stranded"
        return None

    def _endgame(self, result):
        print()
        if result == "victory":
            elapsed = max(1.0, self.stardate - self.start_date)
            rating = int(1000 * (self.klingons_destroyed / elapsed) ** 2)
            print("*** All Klingons destroyed. The galaxy is safe. ***")
            print(f"Your efficiency rating: {rating}")
        elif result == "destroyed":
            print("*** The Enterprise was lost with all hands. ***")
        elif result == "timeout":
            print("*** Time has run out. The mission is a failure. ***")
        elif result == "stranded":
            print("*** Out of energy with no starbase in reach. Stranded. ***")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Space Battles, a Super Star Trek remake.")
    parser.add_argument("--seed", type=int, default=None, help="seed for a reproducible galaxy")
    parser.add_argument("--no-color", action="store_true", help="disable ANSI colour (plain ASCII)")
    args = parser.parse_args(argv)

    while True:
        Game(seed=args.seed, color=not args.no_color).play()
        try:
            again = input("\nPlay again (y/N)? ").strip().lower()
        except EOFError:
            again = "n"
        if again != "y":
            print("Live long and prosper.")
            break


if __name__ == "__main__":
    main()
