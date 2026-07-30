#!/usr/bin/env python3
"""Run docs/cad/checks.scad and report PASS/FAIL with volumes.

    python tools/run_checks.py

Every check is a boolean whose PASS condition is an EMPTY result. OpenSCAD
writes no file at all when a CSG result is empty, so "no file" is the success
signal — but "no file" is also what you get from a typo in the check name, so
this driver refuses to treat a missing file as a pass unless the check actually
ran and OpenSCAD reported an empty top-level object.

Two kinds of check:

  hole:*   a hole that MUST exist, probed by intersecting the ideal hole with
           the finished part. Empty means the material really was removed.
           Solid means the cut missed and the hole is not there — which is
           invisible in a render and costs nothing in mass, and is exactly the
           defect that shipped in v7's cradle and again in v8's first yoke.

  clash:*  two things that must not touch. Empty means clear.
"""
import os
import re
import subprocess
import sys

OPENSCAD = os.environ.get("OPENSCAD", r"C:\Program Files\OpenSCAD\openscad.exe")
CAD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "cad")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "build", "checks")

CHECKS = [
    "hole:cradle_out_bolts", "hole:cradle_wire",
    "hole:yoke_arm_bolts", "hole:yoke_arm_wire", "hole:yoke_bridge_bolts",
    "hole:plate_bolts", "hole:plate_wire", "hole:cap_screws",
    "clash:cradle_v_motor_0", "clash:cradle_v_motor_p90", "clash:cradle_v_motor_m90",
    "clash:cap_v_motor_0", "clash:cap_v_motor_p90", "clash:cap_v_motor_m90",
    "clash:cradle_v_yoke_0", "clash:cradle_v_yoke_p90", "clash:cradle_v_yoke_m90",
    "clash:cap_v_yoke_p90", "clash:cap_v_yoke_m90",
    "clash:payload_v_yoke_p90",
    "clash:cap_v_cradle",
    "clash:cradle_v_stator", "clash:yoke_v_pan_motor", "clash:plate_v_pan_motor",
    "clash:post_v_bridge", "clash:post_v_arm", "clash:lug_v_post_home",
]


def stl_volume(path):
    """Signed volume of a binary/ASCII STL, by the divergence theorem."""
    import struct
    import numpy as np
    with open(path, "rb") as f:
        head = f.read(84)
        n = struct.unpack("<I", head[80:84])[0]
        f.seek(0, 2)
        size = f.tell()
        if size == 84 + n * 50:
            f.seek(84)
            buf = np.frombuffer(f.read(n * 50), dtype=np.uint8).reshape(n, 50)
            t = buf[:, 12:48].copy().view("<f4").reshape(n, 3, 3).astype(np.float64)
        else:
            v = []
            f.seek(0)
            for line in f.read().decode("utf-8", "replace").splitlines():
                s = line.strip()
                if s.startswith("vertex"):
                    v.append([float(x) for x in s.split()[1:4]])
            t = np.asarray(v).reshape(-1, 3, 3)
    a, b, c = t[:, 0], t[:, 1], t[:, 2]
    return abs(float(np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6.0))


def run(check):
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, check.replace(":", "_") + ".stl")
    if os.path.exists(out):
        os.remove(out)
    p = subprocess.run(
        [OPENSCAD, "-o", out, "-D", f'check="{check}"',
         os.path.join(CAD, "checks.scad")],
        capture_output=True, text=True, timeout=600)
    err = p.stderr or ""
    ran = "Current top level object is empty" in err or os.path.exists(out)
    warns = [l for l in err.splitlines()
             if "WARNING" in l and "Ignoring unknown" in l]
    if warns:
        return ("ERROR", 0.0, f"{len(warns)} unknown-variable warnings: {warns[0][:90]}")
    if not ran:
        return ("ERROR", 0.0, "check did not run - is the name in checks.scad's dispatch?")
    if not os.path.exists(out):
        return ("PASS", 0.0, "empty (no file written)")
    vol = stl_volume(out)
    if vol < 1e-6:
        return ("PASS", vol, "empty")
    return ("FAIL", vol, f"{vol:.3f} mm^3 of material where there should be none")


PRINT_PARTS = ["base_plate", "yoke", "cradle", "cradle_cap",
               "tol_coupon", "fit_coupon", "bore_gauge"]


def bed_checks():
    """Every p_* orientation must land the part ON the bed: min Z exactly 0.

    Not asserted in the .scad - MEASURED off the exported STL. v7's p_cradle put
    the part 1.740 mm BELOW the bed (a slicer silently clips the keel's whole
    first-layer footprint) and bore_gauge floated its second half 16 mm in the
    air. Both files looked fine; only the exported bounding box says otherwise.
    """
    import numpy as np
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from meshcheck import read_stl
    out = os.path.join(os.path.dirname(OUT), "print")
    os.makedirs(out, exist_ok=True)
    print()
    print(f"{'part':<32} {'result':<7} detail")
    print("-" * 92)
    bad = 0
    for p in PRINT_PARTS:
        f = os.path.join(out, p + ".stl")
        subprocess.run([OPENSCAD, "-o", f, "-D", f'part="{p}"', "-D", 'orient="print"',
                        os.path.join(CAD, "frame.scad")],
                       capture_output=True, text=True, timeout=600)
        v = read_stl(f).reshape(-1, 3)
        zmin, zmax = float(v[:, 2].min()), float(v[:, 2].max())
        if abs(zmin) < 1e-6:
            print(f"bed:{p:<28} PASS    sits on z=0, {zmax:.2f} mm tall")
        else:
            bad += 1
            where = "BELOW the bed" if zmin < 0 else "FLOATING above the bed"
            print(f"bed:{p:<28} FAIL    min Z = {zmin:+.3f} mm — {where}")
    print("-" * 92)
    print(f"{len(PRINT_PARTS) - bad}/{len(PRINT_PARTS)} parts land on the bed")
    return bad


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    checks = [c for c in CHECKS if not only or only in c]
    print(f"running {len(checks)} boolean checks\n")
    print(f"{'check':<32} {'result':<7} detail")
    print("-" * 92)
    bad = 0
    for c in checks:
        status, vol, detail = run(c)
        if status != "PASS":
            bad += 1
        print(f"{c:<32} {status:<7} {detail}")
    print("-" * 92)
    kind = lambda p: sum(1 for c in checks if c.startswith(p))
    print(f"{len(checks) - bad}/{len(checks)} passed   "
          f"({kind('hole:')} hole checks, {kind('clash:')} clash checks)")
    if not only:
        bad += bed_checks()
    if bad:
        print()
        print("A FAILING hole: check means the hole is not in the part.")
        print("A FAILING clash: check means two parts occupy the same space.")
        print("A FAILING bed: check means the STL is not slice-ready.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
