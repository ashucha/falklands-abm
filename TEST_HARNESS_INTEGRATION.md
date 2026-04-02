# Test Harness Integration Workflow

## Overall Architecture

The test harness is a **Python script** that drives the NetLogo simulation as an external engine. Rather than running inside NetLogo's GUI, the harness launches NetLogo in **headless mode**, feeds inputs via command-line/API calls, and collects outputs from CSV files.

---

## Step-by-Step Pipeline

### **Step 1: Prepare Input Data**

```
inputs.csv (trial metadata)
├─ trial_id (int): unique run identifier
├─ ground_battle_start (string): "May 21 1982 - 00:00"
├─ ships_data (JSON/string): [[id, x, y, destruction_time], ...]
├─ battalions_landing (list): [true, true, false, true, false]
├─ ngfs_base_fire_interval (int): 8
└─ ngfs_ship_range (int): 15
```

**Example row:**

```
trial_id,ground_battle_start,ships_data,battalions_landing,ngfs_base_fire_interval,ngfs_ship_range
1,"May 21 1982 - 00:00","[[1,10,5,""],[2,12,6,""""]]","[true,true,true,false,false]",8,15
```

---

### **Step 2: Launch NetLogo & Load Model**

```python
# Pseudocode
import netlogo

nl = netlogo.NetLogoWorkspace()
nl.open_model("main_ground_model.nlogox")
```

---

### **Step 3: Set Global Variables (Per Trial)**

For each row in `inputs.csv`:

```python
# Set trial-specific inputs
nl.command(f'set trial-id {row["trial_id"]}')
nl.command(f'set ground-battle-start-string "{row["ground_battle_start"]}"')
nl.command(f'set ships-data {convert_ships_json(row["ships_data"])}')
nl.command(f'set battalions-landing {convert_list(row["battalions_landing"])}')
nl.command(f'set ngfs-base-fire-interval {row["ngfs_base_fire_interval"]}')
nl.command(f'set ngfs-ship-range {row["ngfs_ship_range"]}')
```

**What each global controls:**

- `trial-id` → Seeds the RNG; ensures deterministic per-trial behavior
- `ground-battle-start-string` → Initializes date tracking and conflict clock
- `ships-data` → Defines NGFS positions and destruction timelines
- `battalions-landing` → Filters which British units spawn
- `ngfs_*` → Configures naval gunfire strike system

---

### **Step 4: Initialize Simulation**

```python
nl.command("setup")
```

**What happens inside NetLogo:**

1. `random-seed trial-id` → Deterministic randomness
2. `parse-ground-battle-start-date` → Parse "May 21 1982 - 00:00" → cur-month=5, cur-day=21, cur-year=1982, etc.
3. `initialize-ships` → Validate ships-data, populate ships-alive list
4. `initialize-battalions` → Ensure 5-element landing list
5. `initialize-patch-state` → Terrain, bunkers, terrain_map.png
6. `initialize-troop-state` → Spawn Argentine (random) + British (filtered by battalions-landing)
7. `initialize-global-state` → Zero out analytics counters
8. `reset-ticks` → ticks = 0

---

### **Step 5: Run Simulation to Completion**

```python
nl.command("run-battle")
```

**Loop inside NetLogo (`run-battle` procedure):**

```
while [not simulation-over?] {
  go-step:
    + advance-time 360     (6 hours)
    + update-date-string
    + run-argentine-troops (movement, cover-seeking, combat)
    + run-british-troops   (movement, engagement)
    + run-ngfs-phase       (strike targeting & damage)
    + tick                 (increment tick counter)
}

[After battle ends]
output-final-results:
  + Compute: duration_days, outcome, british_killed, argentine_killed, surrendered
  + Write to: battle_results.csv (append)
```

**Simulation Termination:** Battle ends when:

- No British troops remain, **OR**
- No Argentine troops remain

**Duration:** Typically **~84 ticks** (21 days at 6 hours/tick)

---

### **Step 6: Collect Results**

```python
import pandas as pd

results = pd.read_csv("battle_results.csv")
latest_trial = results.iloc[-1]  # Last row = current trial

print(f"Trial {latest_trial['trial_id']} ended on day {latest_trial['duration_days']}")
print(f"  British killed: {latest_trial['british_killed']}")
print(f"  Argentine killed: {latest_trial['argentine_killed']}")
print(f"  Argentine surrendered: {latest_trial['argentine_surrendered']}")
print(f"  Outcome: {latest_trial['outcome']} (1=British win, 0=Argentine survival)")
```

**Output CSV columns:**

```
trial_id, ground_battle_start, ground_battle_end, duration_days,
british_killed, argentine_killed, argentine_surrendered, outcome
```

**Example output row:**

```
1, "May 21 1982 - 00:00", "May 27 1982 - 12:00", 6, 2, 32, 5, 1
```

---

### **Step 7: Repeat for All Trials**

```python
for idx, row in pd.read_csv("inputs.csv").iterrows():
    # Steps 3-6: Set globals, setup, run-battle, collect results
    pass

# All results accumulate in battle_results.csv
```

---

## Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                      PYTHON TEST HARNESS                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  FOR EACH TRIAL:                                                    │
│                                                                      │
│  1. Read row from inputs.csv                                        │
│     (trial_id, start_date, ships, battalions, NGFS params)         │
│                         ↓                                            │
│  2. Launch NetLogo headless instance                                │
│     nl.open_model("main_ground_model.nlogox")                       │
│                         ↓                                            │
│  3. Set global variables via nl.command()                           │
│     • trial-id                                                      │
│     • ground-battle-start-string                                    │
│     • ships-data                                                    │
│     • battalions-landing                                            │
│     • ngfs parameters                                               │
│                         ↓                                            │
│  4. Initialize simulation                                           │
│     nl.command("setup")                                             │
│             ↓ (NetLogo internals)                                   │
│     ├─ random-seed trial-id (deterministic RNG)                     │
│     ├─ parse-ground-battle-start-date                               │
│     ├─ initialize-ships                                             │
│     ├─ initialize-battalions                                        │
│     ├─ initialize-patch-state (terrain, bunkers)                    │
│     ├─ spawn-argentine-battalions (4 units at random)               │
│     ├─ spawn-british-troops-filtered (up to 5 units, filtered)      │
│     └─ initialize-global-state (zero analytics)                     │
│                         ↓                                            │
│  5. Run battle to completion                                        │
│     nl.command("run-battle")                                        │
│             ↓ (NetLogo loop)                                        │
│     WHILE simulation-over? = false:                                 │
│      ├─ advance-time 360 minutes (6 hours per tick)                 │
│      ├─ update-date-string                                          │
│      ├─ run-argentine-troops (cover, retreat, combat)               │
│      ├─ run-british-troops (advance, engage)                        │
│      ├─ run-ngfs-phase (strike targeting, damage application)       │
│      └─ tick++                                                      │
│             ↓                                                        │
│     When simulation-over? = true (one side eliminated):             │
│     ├─ Compute outcomes (duration, kills, surrenders)               │
│     ├─ Write to battle_results.csv (append mode)                    │
│     └─ Return to Python                                             │
│                         ↓                                            │
│  6. Collect results                                                 │
│     results = pd.read_csv("battle_results.csv")                     │
│     latest = results.iloc[-1]                                       │
│                         ↓                                            │
│  7. Analyze & aggregate (optional)                                  │
│     • Statistical summaries (mean casualties, win rate, etc.)        │
│     • Compare scenarios (different ship counts, battalion mix)       │
│     • Plot distributions (outcome vs. input parameters)              │
│                         ↓                                            │
│  8. Next trial...                                                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Input/Output Contract

### **Inputs (Set Before Setup)**

| Global                       | Type            | Example                        | Purpose                                       |
| ---------------------------- | --------------- | ------------------------------ | --------------------------------------------- |
| `trial-id`                   | int             | `42`                           | RNG seed; unique trial identifier             |
| `ground-battle-start-string` | string          | `"May 21 1982 - 00:00"`        | Battle start datetime                         |
| `ships-data`                 | list of lists   | `[[1 10 5 ""] [2 12 6 ""]]`    | 13 max ships: [id, x, y, destruction_time]    |
| `battalions-landing`         | list of 5 bools | `[true true false true false]` | Filters 5 British spawn positions             |
| `ngfs-base-fire-interval`    | int             | `8`                            | Base ticks between NGFS strikes               |
| `ngfs-ship-range`            | int             | `15`                           | Detection/targeting radius per ship (patches) |

### **Outputs (Written to CSV)**

| Column                  | Type       | Example                 | Meaning                                     |
| ----------------------- | ---------- | ----------------------- | ------------------------------------------- |
| `trial_id`              | int        | `42`                    | Trial identifier (matches input)            |
| `ground_battle_start`   | string     | `"May 21 1982 - 00:00"` | Recorded start time                         |
| `ground_battle_end`     | string     | `"May 27 1982 - 12:00"` | Recorded end time                           |
| `duration_days`         | int        | `6`                     | Conflict duration in days                   |
| `british_killed`        | int        | `2`                     | British units destroyed                     |
| `argentine_killed`      | int        | `32`                    | Argentine units killed by NGFS              |
| `argentine_surrendered` | int        | `5`                     | Argentine units who surrendered             |
| `outcome`               | int (0\|1) | `1`                     | 1 = British victory, 0 = Argentine survival |

---

## Key Design Principles

### **Determinism**

Each trial is fully deterministic given its `trial-id`:

- `random-seed trial-id` ensures the same sequence of random numbers
- Same inputs → same outputs (validating reproducibility)

### **Single-Run Model**

- No internal loop or convergence logic
- Python harness controls iteration (1 harness invocation = 1 battle)
- Scales to thousands of trials via loop in Python

### **CSV Persistence**

- Results append to `battle_results.csv`, not overwrite
- Handles multi-trial runs without data loss
- Easy post-processing: load CSV, analyze with pandas, plot with matplotlib

### **Headless Execution**

- No GUI required; runs on servers/clusters
- Pure batch processing; suitable for parameter sweeps and sensitivity analysis

---

## Example Python Harness Script (Sketch)

```python
import pandas as pd
import netlogo

# Load input trials
trials = pd.read_csv("inputs.csv")

# Launch NetLogo once
nl = netlogo.NetLogoWorkspace()
nl.open_model("main_ground_model.nlogox")

# Run each trial
for idx, row in trials.iterrows():
    print(f"Running trial {row['trial_id']}...")

    # Set inputs
    nl.command(f'set trial-id {row["trial_id"]}')
    nl.command(f'set ground-battle-start-string "{row["ground_battle_start"]}"')
    nl.command(f'set ships-data {row["ships_data"]}')  # pre-formatted as NetLogo list
    nl.command(f'set battalions-landing {row["battalions_landing"]}')
    nl.command(f'set ngfs-base-fire-interval {row["ngfs_base_fire_interval"]}')
    nl.command(f'set ngfs-ship-range {row["ngfs_ship_range"]}')

    # Initialize and run
    nl.command("setup")
    nl.command("run-battle")

    # Collect result (appended to battle_results.csv by NetLogo)
    results = pd.read_csv("battle_results.csv")
    print(f"  → Ended day {results.iloc[-1]['duration_days']}, outcome: {results.iloc[-1]['outcome']}")

# Post-process results
results = pd.read_csv("battle_results.csv")
print(f"\nCompleted {len(results)} trials")
print(f"British victory rate: {results['outcome'].mean():.1%}")
print(f"Mean duration: {results['duration_days'].mean():.1f} days")
```

---

## Summary

This architecture enables **scalable, reproducible monte-carlo analysis** of the ground battle while keeping NetLogo focused on the domain logic (movement, combat, NGFS) and Python handling orchestration and analytics.
