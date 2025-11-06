# space empires game
Recreating the classic super star trek into a space empire building game


## PHASE 1 LOGIC
```
START GAME
    Initialize global constants:
        - SHIP_ENERGY_CAPACITY = 3000
        - TORPEDO_CAPACITY = 10
        - KLINGON_SHIELD_STRENGTH_BASE = 200
        - DIRECTIONS = array of 9 vectors for movement:
            1: [0, 1]   (east)
            2: [-1, 1] (northeast)
            3: [-1, 0] (north)
            4: [-1, -1](northwest)
            5: [0, -1] (west)
            6: [1, -1] (southwest)
            7: [1, 0]  (south)
            8: [1, 1]  (southeast)
            9: [0, 1]  (same as 1 for wrap-around)

    Initialize game state:
        - Set random seed based on time
        - Ship position:
            QUADRANT = [random integer 0–7, 0–7]
            SECTOR = [random integer 0–7, 0–7]
        - ENERGY = 3000
        - SHIELDS = 0
        - TORPEDOES = 10
        - DAMAGE_STATUS = array of 8 devices, each set to 0 (fully functional)
        - MISSION_DURATION = random integer between 25 and 34
        - START_DATE = random integer between 2000 and 3900 (step 100)
        - KLINGONS_REMAINING = 0
        - STARBASES_REMAINING = 0

    Display welcome message:
        "Your mission: Destroy all Klingon ships before Stardate (START_DATE + MISSION_DURATION)."

    Generate galaxy map:
        For each of the 8 rows (x) and 8 columns (y):
            Assign Klingons:
                - Generate random float r between 0 and 1
                - If r > 0.98 → 3 Klingons
                - Else if r > 0.95 → 2 Klingons
                - Else if r > 0.80 → 1 Klingon
                - Else 0 Klingons
                Add this count to KLINGONS_REMAINING

            Assign starbases:
                - Generate random float r between 0 and 1
                - If r > 0.96 → 1 starbase
                Increment STARBASES_REMAINING if added

            Assign stars:
                - STARS = 1 + random integer 0–7

        Ensure at least one starbase exists:
            If STARBASES_REMAINING = 0:
                Add a starbase to the Enterprise's starting quadrant

    Populate initial quadrant:
        - Place Enterprise in assigned sector
        - For each Klingon:
            1. Find an empty sector (random search until empty found)
            2. Assign Klingon shields = KLINGON_SHIELD_STRENGTH_BASE * (0.5 + random float 0–1)
        - For each starbase:
            Find empty sector and place starbase
        - For each star:
            Find empty sector and place star

MAIN GAME LOOP
    While KLINGONS_REMAINING > 0 and CURRENT_DATE <= START_DATE + MISSION_DURATION:
        
        Display short-range scan:
            - Print 8x8 grid with:
                <*> = Enterprise
                +K+ = Klingon
                >!< = Starbase
                 *  = Star
            - Print status:
                Stardate: CURRENT_DATE
                Shields: SHIELDS
                Energy: ENERGY
                Torpedoes: TORPEDOES
                Klingons remaining: KLINGONS_REMAINING
        
        Prompt for command:
            Valid commands: NAV, SRS, LRS, PHA, TOR, SHE, DAM, COM, XXX

        PROCESS COMMAND:
            CASE NAV (Navigate):
                Request course (1–9):
                    If 9 → wrap around to 1
                    Calculate direction vector:
                        dx = linear interpolate between adjacent directions based on decimal course input
                        dy = similar to dx
                Request warp factor (0.1–8):
                    If warp > 0.2 and engines damaged → limit warp to 0.2
                Calculate movement:
                    For i in range(steps = warp * 8):
                        New x = old x + dx
                        New y = old y + dy
                        If new position hits obstacle:
                            Stop movement
                        If crosses quadrant boundary:
                            Adjust quadrant accordingly
                Calculate energy cost:
                    ENERGY -= (steps + 10)
                    If ENERGY < 0:
                        If shields > steps - energy and shields operational:
                            Transfer from shields
                        Else:
                            Display "Out of energy. Ship stranded."
                            End game
                Update quadrant if necessary

            CASE SRS (Short-Range Scan):
                Display local 8x8 grid of current quadrant

            CASE LRS (Long-Range Scan):
                Display 3x3 grid of neighboring quadrants:
                    For each:
                        Print three-digit code (e.g., 210 = 2 Klingons, 1 base, 0 stars)

            CASE PHA (Fire Phasers):
                Request energy to allocate:
                    Validate energy ≤ available energy
                    For each Klingon:
                        Distance = sqrt((kx - sx)² + (ky - sy)²)
                        Damage = (energy_per_klingon / distance) * (random float 1–3)
                        Klingon shield -= Damage
                        If Klingon shield ≤ 0:
                            Mark Klingon destroyed
                            KLINGONS_REMAINING -= 1
                    Deduct energy used from reserves
                    Trigger enemy fire phase

            CASE TOR (Fire Photon Torpedoes):
                Request firing course (1–9):
                    Calculate trajectory:
                        Position = current sector
                        While within 8x8 bounds:
                            Move by dx, dy based on course
                            If hit Klingon:
                                Destroy Klingon
                                KLINGONS_REMAINING -= 1
                                Stop torpedo
                            If hit starbase:
                                Destroy starbase
                                STARBASES_REMAINING -= 1
                                Stop torpedo
                            If hit star:
                                Star absorbs torpedo
                                Stop torpedo
                    Deduct one torpedo
                    Trigger enemy fire phase

            CASE SHE (Shield Control):
                Request shield allocation:
                    Validate allocation ≤ total energy + shields
                    Adjust shield/energy values accordingly

            CASE DAM (Damage Control):
                Print each device’s repair state
                If docked at starbase:
                    Calculate repair time = sum of damage * random delay
                    Increment damage stats toward 0
                    Increment stardate by repair time

            CASE COM (Computer):
                Offer options:
                    1. Galaxy map (charted info only)
                    2. Status report (remaining Klingons, time, and bases)
                    3. Photon torpedo targeting data (directions and distances)
                    4. Starbase navigation (direction/distance to nearest base)
                    5. Distance calculator (input 2 points and calculate):
                        Distance = sqrt((x2 - x1)² + (y2 - y1)²)
                        Direction calculated using trigonometric rules

            CASE XXX (Resign Command):
                Print resignation message
                End game immediately

        ENEMY FIRE PHASE:
            For each Klingon in the current quadrant (if not destroyed):
                Calculate distance:
                    distance = sqrt((kx - sx)² + (ky - sy)²)
                Calculate damage:
                    damage = (klingon_shield / distance) * (random float 1–3)
                Apply damage to Enterprise shields:
                    SHIELDS -= damage
                If SHIELDS < 0:
                    Print "Enterprise destroyed."
                    End game
                With 60% probability if damage > 20:
                    Randomly damage one ship device

        CHECK GAME STATUS:
            If KLINGONS_REMAINING = 0:
                Print victory message
                End game
            If CURRENT_DATE > START_DATE + MISSION_DURATION:
                Print failure message (time expired)
                End game
            If ENERGY = 0 and STARBASES_REMAINING = 0:
                Print "Ship stranded without energy."
                End game

GAME END:
    If victory:
        Calculate rating:
            rating = 1000 * (KLINGONS_DESTROYED / (CURRENT_DATE - START_DATE))²
        Print success message with rating
    If failure:
        Print cause of mission failure
    Offer to play again:

```
        If input = 'AYE':
            Restart game
        Else:
            Exit

END PROGRAM

