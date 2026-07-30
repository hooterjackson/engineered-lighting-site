# RMD-L-5005 ("S" variant) — dimensions read out of the vendor STEP

Source: `ref/RMD-L-5005-S.STEP`, the file MyActuator/Dings' ship as
`RMD-L-5005-S.STEP`. AP214, written by SolidWorks 2012 on 2019-11-06, original
filename `RMD-L-5005.STEP`. It is the motor itself — 7 solid bodies, 296 faces,
166 cylindrical surfaces — not a simplified envelope.

Everything on this page is measured out of that file by resolving
`ADVANCED_FACE` -> bounds -> edges -> `VERTEX_POINT`, so every number is a real
face boundary. **Surface placement points were deliberately not used**: a STEP
`AXIS2_PLACEMENT_3D` for a cylinder sits anywhere on the infinite axis, and
reading those as positions is what produces impossible values like x = -70 or
x = +499021 on a 23.9 mm part.

Parser: `ref/step_dump.py` in this repo. Re-run it to check any of this.

## Coordinate convention used here

The motor's axis is **X** in the file. Every one of the 166 cylindrical surfaces
is coaxial with X, so there is no ambiguity.

- **x = 0.000 is the OUTPUT face** (the end that turns).
- **x = 23.900 is the REAR face** (the end that bolts to your frame).
- Total length 23.900 mm, body Ø49.000 mm.

The output end is identified by the 4 × Ø2.5 tapped holes on a Ø25 bolt circle
starting at x = 0; the rear end by the 4 × Ø2.05 holes on the 20 × 20 square.

## The three numbers that kept getting guessed

### 1. Is there a raised boss on the output face? — **NO.**

The output face is a **flat annulus at x = 0.000**, running from **Ø10.10**
(the mouth of the bore chamfer) out to **Ø47.00**. Beyond Ø47 a 45° chamfer
takes it out to Ø49 over the first 1.00 mm.

There is no boss, no spigot and no register of any kind. The face at x = 0 is
the frontmost plane of the entire model — nothing on the motor sits in front of
it.

### 2. How far does it stand proud of the front face? — **0.000 mm.**

There is nothing to stand proud. The output face *is* the front face.

This confirms the RMD-L manual's RMD-50 drawing, which shows no circle between
Ø25 and Ø48 while explicitly dimensioning bosses on the RMD-90 and RMD-120.
The drawing was right and the guesses were wrong.

**Consequence for the design:** a printed plate lands flat on the annulus
between Ø10.1 and Ø47. There is no boss to register on, so the four M3 screws
are the only thing locating the part — the plate needs its own spigot or a
close-fitting counterbore if you want a register.

### 3. How far does the side connector protrude past the Ø49 body? — **0.000 mm.**

**The maximum radius of any vertex anywhere in the model is exactly R24.5000,
i.e. Ø49.0000.** Nothing on this motor protrudes past its own barrel, at any
axial position. Checked band by band along the whole 23.9 mm length.

The connectors are **recesses cut into** the casting, not parts standing out of
it. The deepest connector cavity reaches only R23.16 (Ø46.32) — inside the
barrel.

> **UNVERIFIED, and it matters:** the STEP contains the motor only. The mating
> cable plug is not modelled. A plug pushed into those cavities *will* stand
> out, and so will the cable's bend radius. That protrusion is not published
> anywhere I can reach and is not in this file. **Do not design a part that
> assumes zero radial clearance at the connector azimuth** — the frame here
> keeps a stated radial gap at that azimuth and says so, rather than pretending
> the number is known.

## Output end — the rotating body

The output rotor is a **separate solid body** in the file (`shell#14857`,
x = 0.000 .. 5.000) from the stationary housing ring (`shell#15032`,
x = 3.000 .. 12.500). So the whole Ø47 front face turns.

| feature | value | axial position |
|---|---|---|
| Output face, flat annulus | **Ø10.10 → Ø47.00** | x = 0.000 |
| Outer chamfer, 45° | Ø47.00 → Ø49.00 | x = 0.000 → 1.000 |
| Bore mouth chamfer, 45° | Ø8.10 → Ø10.10 | x = 0.000 → 1.000 |
| **Output bolts: 4 × M3 tapped** | **Ø2.50 drill, on Ø25.00 BC** | x = 0.000 → **2.500 deep** |
| Through bore ("S" variant) | **Ø8.10** | x = 1.000 → 3.400 |
| Rotor outer band | Ø49.00 | x = 1.000 → 3.000 |
| Internal counterbore | Ø17.00 | x = 2.500 → 3.400 |
| Rotor spigot inside housing | Ø46.60 / Ø44.20 | x = 3.000 → 5.000 |

**The stationary housing begins at x = 3.000.** A printed part that lands on the
output face must not touch anything at or beyond x = 3.000 — that is the number
that decides whether a part clamps the motor solid. A plate sitting flat on the
face has 3.00 mm of axial room at full Ø49 before it fouls the stator.

## Rear end — the mounting body

| feature | value | axial position |
|---|---|---|
| **Rear bolts: 4 × M2.5 tapped** | **Ø2.05 drill, on a 20 × 20 mm square** (Ø28.284 BC at 45°) | x = 13.200 → 23.900 |
| Rear face | flat | x = 23.900 |
| Motor's own cover screws, M2.5 SHCS | Ø4.50 heads on Ø44.0 BC | heads x = 21.100 → **23.600** |

The cover-screw heads sit **0.300 mm below the rear face** and reach R24.095
(Ø48.19), 0.405 mm inside the barrel. A plate bolted flat to the rear face
clears them — but only by 0.3 mm, so **do not put a raised pad or a boss on the
rear-facing side of a plate anywhere on the Ø44 circle.**

Those screws are how the motor is held together. They are not mounting points.

## Body

| | |
|---|---|
| Overall Ø | **49.000** |
| Overall length | **23.900** (x = 0.000 .. 23.900) |
| Relief bands | Ø48.00 at x 11.4–12.5 and 19.0–19.5; Ø47.00 at x 12.1–12.9 |
| Max radius anywhere | **R24.5000 exactly** |

## Cross-check against the manual

Five numbers in the manual are independently reproduced by the STEP, which is
why the rest of the file is trusted:

| | manual | STEP | |
|---|---|---|---|
| Body diameter | Ø49 | Ø49.000 | OK |
| Body length | 23.9 mm | 23.900 | OK |
| Output flange | 4 × M3 on Ø25 | 4 × Ø2.5 on Ø25.000 | OK |
| Rear mount | 4 × M2.5 on 20 × 20 | 4 × Ø2.05 at R14.142 = 20/√2 | OK |
| Through bore, "S" | Ø8.1 | Ø8.100 | OK |

## Still unverified after reading the STEP

- **Load ratings.** No bearing-load figure exists in the manual and a STEP file
  cannot carry one. The output bearing's permissible radial and moment load are
  unknown.
- **Connector plug protrusion**, as above.
- **Mass**: 92 g is the vendor's figure; the STEP has no material assigned.
