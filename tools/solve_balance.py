#!/usr/bin/env python3
"""Solve the two balance numbers from MEASURED geometry, not from estimates.

    python tools/solve_balance.py

Exports every printed part in MODEL coordinates, measures mass and centre of
mass, and reports:

  1. axis_z   — how far the tilt axis must sit ABOVE the payload's axis so the
                whole head balances on it. This one matters: gravity is
                perpendicular to the tilt axis, so any residual offset is a
                standing torque the motor has to hold all day.

  2. the pan-axis CoM offset — reported, deliberately NOT nulled. See the note
     at the bottom of the output for why.

MODEL COORDINATES, ALWAYS. A centre of mass read off a print-orientation export
is a rigid transform away from the frame every other number here is written in.
That mistake has already shipped in this project once.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from meshcheck import props, read_stl                     # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAD = os.path.join(ROOT, "docs", "cad")
OUT = os.path.join(ROOT, "build", "model")
OPENSCAD = os.environ.get("OPENSCAD", r"C:\Program Files\OpenSCAD\openscad.exe")
PETG = 1.27e-3          # g/mm^3
G = 9.81

PARTS = ["base_plate", "yoke", "cradle", "cradle_cap"]


def scad_value(name):
    """Read one derived value out of frame_params.scad via OpenSCAD itself, so
    this script can never disagree with the geometry."""
    probe = os.path.join(CAD, "_solve_probe.scad")
    with open(probe, "w") as f:
        f.write(f'include <frame_params.scad>\necho("VAL", {name});\ncube(1);\n')
    try:
        p = subprocess.run([OPENSCAD, "-o", os.devnull, "--export-format=asciistl", probe],
                           capture_output=True, text=True, timeout=120)
        for line in (p.stderr or "").splitlines():
            if line.startswith('ECHO: "VAL"'):
                return float(line.split(",")[-1].strip().rstrip('"'))
    finally:
        if os.path.exists(probe):
            os.remove(probe)
    raise RuntimeError(f"could not read {name}")


def export(part):
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, f"{part}.stl")
    subprocess.run([OPENSCAD, "-o", out, "-D", f'part="{part}"', "-D", 'orient="model"',
                    os.path.join(CAD, "frame.scad")],
                   capture_output=True, text=True, timeout=600)
    return out


def main():
    print("exporting in MODEL coordinates ...")
    m = {}
    for p in PARTS:
        vol, com = props(read_stl(export(p)))
        m[p] = {"mass": vol * PETG, "com": com}
        print(f"  {p:<12} {vol * PETG:7.3f} g   CoM ({com[0]:8.3f}, {com[1]:7.3f}, {com[2]:8.3f})")

    axis_z = scad_value("axis_z")
    payload_mass = scad_value("payload_mass")
    motor_mass = scad_value("motor_mass")
    out_face_x = scad_value("out_face_x")
    motor_len = scad_value("motor_len")
    bore_x = scad_value("bore_x")

    # ---------------- 1. the tilt axis ----------------
    # The printed head's geometry is defined relative to the SPLIT LINE, which
    # sits axis_z below the tilt axis. So its CoM height above the split line is
    # independent of axis_z, and the solve is a single step, not a fixed point.
    mp = m["cradle"]["mass"] + m["cradle_cap"]["mass"]
    zp_axis = (m["cradle"]["mass"] * m["cradle"]["com"][2]
               + m["cradle_cap"]["mass"] * m["cradle_cap"]["com"][2]) / mp
    zp_split = zp_axis + axis_z                      # above the split line
    mh = payload_mass                                # payload sits ON the split line
    solved = mp * zp_split / (mp + mh)

    head_mass = mp + mh
    resid = (mp * (zp_split - solved)) / head_mass    # CoM above the tilt axis, at `solved`
    resid_now = (mp * zp_axis + mh * (-axis_z)) / head_mass

    print(f"\n1. TILT AXIS")
    print(f"   printed head          {mp:7.3f} g, CoM {zp_split:.4f} mm above the split line")
    print(f"   payload               {mh:7.3f} g, on the split line")
    print(f"   axis_z should be      {solved:.4f} mm      (file says {axis_z:.4f})")
    print(f"   residual as built     {resid_now:+.4f} mm -> "
          f"{head_mass / 1000 * G * abs(resid_now) / 1000:.3e} N.m of standing tilt torque")
    if abs(solved - axis_z) > 0.02:
        print(f"   *** UPDATE axis_z TO {solved:.2f} IN frame_params.scad ***")
    else:
        print(f"   OK — within 0.02 mm")

    # ---------------- 2. the pan axis ----------------
    # Only what HANGS from the pan output counts: yoke, tilt motor, head.
    hang = [
        ("yoke",        m["yoke"]["mass"],        m["yoke"]["com"][0]),
        ("tilt motor",  motor_mass,               out_face_x - motor_len / 2),
        ("cradle",      m["cradle"]["mass"],      out_face_x + m["cradle"]["com"][0]),
        ("cradle_cap",  m["cradle_cap"]["mass"],  out_face_x + m["cradle_cap"]["com"][0]),
        ("payload",     payload_mass,             bore_x),
    ]
    tot = sum(w for _, w, _ in hang)
    mx = sum(w * x for _, w, x in hang)
    off = mx / tot
    print(f"\n2. PAN AXIS")
    for n, w, x in hang:
        print(f"   {n:<12} {w:7.3f} g  at x = {x:8.3f}")
    print(f"   hanging mass          {tot:7.3f} g")
    print(f"   CoM offset from the pan axis: {off:+.3f} mm")
    print(f"   -> bearing moment     {tot / 1000 * G * abs(off) / 1000:.4f} N.m")
    print(f"   -> pan HOLDING TORQUE  0.0000 N.m")
    print("""
   NOT NULLED, ON PURPOSE. The pan axis is vertical and gravity is parallel to
   it, so a CoM offset along X produces NO torque about the pan axis — the motor
   holds any heading with zero current whatever this number is. All the offset
   does is load the output bearing with the small moment above.

   Nulling it would mean pushing the arm out until the head sits over the pan
   axis, which costs roughly 7 mm of arm reach, a bigger bridge disc and ~12 g,
   to remove a bearing moment of about 0.013 N.m on a journal 46.6 mm across.
   That is a bad trade, so arm_reach is set by clearance and compactness instead
   and this number is reported rather than engineered away.

   (The TILT axis is a different story and is nulled: gravity is perpendicular
   to it, so any offset there IS a standing torque.)""")

    total = sum(v["mass"] for v in m.values())
    print(f"\nPRINTED TOTAL {total:.2f} g   (v7 was 177.06 g)")


if __name__ == "__main__":
    sys.exit(main())
