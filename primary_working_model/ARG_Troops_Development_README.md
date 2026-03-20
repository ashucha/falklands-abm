# ARG Troops Development README

## Purpose
This README is meant to be committed into the GitHub repo so an LLM can quickly understand the current direction of the Falklands War NetLogo model and continue development safely.

The focus of this file is:
- Argentine ground troops (`argentine-troops`)
- related defensive infrastructure (`bunker?`, `trench?`)
- interactions with British troops, terrain, and naval gunfire support (NGFS)
- preserving model logic that already exists while extending it in a clean, NetLogo-correct way

---

## Project Context
This is a NetLogo agent-based model of the Falklands War.

Current focus areas include:
- Argentine defensive troop behavior
- bunker and trench interactions
- terrain-aware movement and survivability
- British naval gunfire support (NGFS)
- battle outcome analytics

The model already uses:
- `breed [argentine-troops argentine-troop]`
- `breed [british-troops british-troop]`
- patch-level variables for bunkers, trenches, water, strike counts, and bunker strength/capacity
- turtle-level variables for troop strength, morale, entrenchment, suppression, and bunker targeting

---

## Current Coding Rules for Future Development
When extending the model, follow these rules:

1. **Do not rewrite working structure unless necessary.**
   - Prefer minimal edits to existing procedures and variable blocks.
   - Preserve existing globals, breeds, patch variables, and analytics unless there is a clear bug.

2. **Use correct NetLogo syntax only.**
   - No pseudocode in the actual model file.
   - Any new logic should be copy-paste ready.

3. **Respect current variable naming.**
   - Existing names like `bunker?`, `trench?`, `suppressed-ticks`, `bunker-target`, `panic-move?`, `strength`, `morale`, etc. should be reused.
   - Do not rename variables unless there is a strong reason.

4. **Keep behaviors explainable.**
   - Each major troop behavior should map to a clear state/decision rule.
   - Avoid hidden or overly complex logic that becomes hard to brief in class.

5. **Prefer modular procedures.**
   - Add focused procedures like:
     - `move-to-bunker`
     - `choose-bunker-target`
     - `resolve-ngfs-effects`
     - `check-surrender`
     - `apply-suppression`
   - Avoid stuffing too much logic into one `go` loop.

6. **Terrain and patch legality matter.**
   - Troops and bunkers should never spawn on invalid terrain.
   - Water must be treated as illegal for bunker placement and normal land troop spawning.

---

## Critical Rule to Add / Preserve
### Bunkers must never spawn on water
This came up in simulation testing: a bunker spawned in the water once.

Even if it is rare, the model needs an explicit rule preventing it.

### Required behavior
- A bunker patch must satisfy all of the following before a bunker is created:
  - `not water?`
  - valid land patch
  - not already occupied by another bunker unless intentional stacking is explicitly modeled

### Recommended safeguard
Wherever bunkers are created, use a filter like:
- only candidate patches with `not water?`
- ideally also exclude patches that are impossible or nonsensical defensive terrain if needed later

### Acceptance criterion
After repeated runs, no bunker should ever appear on a water patch.

---

## What We Talked About Yesterday for Future Development
This is the short memory of the recent development direction and should guide the next coding steps.

### 1. Improve Argentine troop movement to bunkers
We discussed adding/fixing logic so Argentine troops can:
- identify a bunker worth moving to
- move toward it correctly in NetLogo syntax
- enter it if capacity allows
- gain defensive benefit once inside

Important related variables already exist:
- `in-bunker?`
- `bunker-target`
- `panic-move?`

### 2. Bunkers should function as defensive strongpoints, not independent magic weapons
We discussed that bunkers should not just fire automatically as if the bunker itself is a combat agent.

Instead, the intended logic is:
- bunker effectiveness should depend on whether Argentine troops are occupying it
- troops inside bunkers should get a defensive bonus
- troops firing from bunkers should likely receive an accuracy / survivability bonus

### 3. Add or refine NGFS effects against Argentine troops and defenses
NGFS was identified as one of the highest-impact additions.

Intended logic:
- British ships fire on Argentine positions at intervals
- effects depend on target posture:
  - open = highest vulnerability
  - trench = medium vulnerability
  - bunker = lowest vulnerability
- NGFS should also interact with:
  - suppression
  - bunker damage
  - troop casualties
  - morale degradation

### 4. Strengthen suppression, surrender, and panic behavior
We discussed making Argentine troop degradation more realistic.

Desired behaviors:
- heavy bombardment or severe losses can cause suppression
- suppressed troops may temporarily stop firing or move poorly
- low morale / low strength can lead to surrender or panic movement
- panic movement may drive troops toward cover, bunkers, trenches, or retreat behavior

### 5. Preserve and expand analytics
The model already tracks useful analytics such as:
- NGFS strikes
- total damage
- total kills
- bunkers destroyed
- total surrenders
- Argentine strength loss total
- strike locations
- CSV export / heatmap-related values

Future changes should keep these analytics intact and expand them where useful.

### 6. Keep the code aligned with the old working version
A major point from yesterday was that new changes should be added into the **old working codebase** rather than replacing it with structurally different code that breaks syntax or behavior.

In practice, this means:
- patch in the new logic carefully
- do not invent a totally different architecture unless necessary
- prioritize working NetLogo over abstract redesign

---

## Priority Backlog
Suggested order for future implementation.

### Tier 1: Immediate fixes
1. Add explicit bunker spawn legality check so bunkers cannot spawn on water.
2. Fix / finish Argentine movement to bunkers using proper NetLogo syntax.
3. Ensure bunker occupancy, capacity, and troop bonuses work correctly.

### Tier 2: High-impact combat logic
4. Implement or refine NGFS posture-based damage model.
5. Add bunker damage and destruction from NGFS.
6. Add suppression effects from bombardment.

### Tier 3: Behavior realism
7. Add surrender logic tied to morale + strength thresholds.
8. Add panic movement / retreat-to-cover behavior.
9. Improve target selection logic between British troops, trenches, and bunkers.

### Tier 4: Model clarity and outputs
10. Improve analytics and CSV export fields for bunker occupancy, bunker kills/saves, and suppression events.
11. Improve visualization for struck patches, destroyed bunkers, and troop state.

---

## Desired Argentine Troop Behavior Model
At a high level, Argentine troops should behave like defensive infantry that:
- hold ground
- use trenches and bunkers when available
- engage nearby British units
- degrade under bombardment and attrition
- sometimes surrender or panic when badly damaged

### Recommended decision sequence per tick
1. Check if dead / routed / surrendered.
2. Update suppression state.
3. If not in bunker, look for valid nearby bunker or trench cover.
4. Move to cover if threat is high and cover is available.
5. Detect nearby British troops.
6. If target in range and able to fight, engage.
7. If under NGFS or extreme losses, reduce morale / strength and evaluate surrender or panic.

---

## Bunker Logic Requirements
### Bunker creation
- Must be on land.
- Must not be on water.
- Should preferably be on tactically sensible terrain.

### Bunker occupancy
- Use `bunker-capacity`.
- Troops should only enter if capacity not full.
- Occupied bunker status should matter for combat output.

### Bunker combat effect
When troops are inside a bunker, they should get some combination of:
- reduced incoming damage
- reduced casualty probability
- increased resistance to suppression
- improved firing survivability
- possibly improved hit chance, if desired for abstraction

### Bunker destruction
Bunkers should be destructible.
Potential drivers:
- repeated NGFS hits
- bunker strength reaching zero

When destroyed:
- patch loses bunker status
- occupants lose protection
- analytics increment `bunkers-destroyed`

---

## NGFS Logic Requirements
NGFS should model British naval fires as a periodic indirect-fire threat.

### Inputs already implied in the model
- `ngfs-range`
- `ngfs-fire-interval`
- `ngfs-last-fire-tick`
- `ngfs-mode`

### Recommended target effects
#### Argentine troop in open
- high hit probability
- high damage
- high suppression chance

#### Argentine troop in trench
- medium hit probability
- medium damage
- medium suppression chance

#### Argentine troop in bunker
- low hit probability
- low damage
- bunker may absorb part of effect

### Desired outputs
- troop strength loss
- morale reduction
- suppression ticks
- possible bunker damage
- analytics updates
- strike flash / strike count / heatmap support

---

## Known Model Risks / Things an LLM Should Avoid
- Do not spawn bunkers without checking `water?`.
- Do not use invalid NetLogo constructs or syntax copied from other languages.
- Do not replace the old working structure with a brand-new architecture unless asked.
- Do not make bunkers behave as magical autonomous turrets if the design intent is troop-occupied defense.
- Do not break analytics variables already being tracked.
- Do not ignore patch legality and terrain constraints.

---

## Good Next Coding Tasks for an LLM
If continuing development, the best next tasks are:

1. **Patch bunker spawn logic** so water patches are excluded.
2. **Implement bunker target selection + movement** for Argentine troops.
3. **Implement bunker entry/exit and capacity accounting**.
4. **Add troop bonuses while in bunker**.
5. **Implement NGFS posture-based effects** on open/trench/bunker troops.
6. **Add surrender and panic logic** tied to morale/strength/suppression.
7. **Expose useful switches/sliders/monitors** in the interface for bunker mode and NGFS tuning.

---

## Suggested Definition of Done
A good intermediate milestone is reached when all of the following are true:
- bunkers never spawn on water
- Argentine troops can correctly move to and occupy bunkers
- occupied bunkers provide measurable defensive benefit
- NGFS damages open troops more than entrenched or bunkered troops
- bombardment can suppress or break Argentine units
- analytics still run correctly
- code is copy-paste ready and syntactically valid in NetLogo

---

## Final Notes for Future Contributors
This model is being built for an academic project, so development should optimize for:
- correctness
- explainability
- presentation clarity
- historically grounded abstraction

Prefer clean, defensible rules over feature bloat.
