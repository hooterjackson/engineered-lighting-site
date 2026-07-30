#!/usr/bin/env python3
"""Read real dimensions out of an ASCII STEP file.

Written to settle the RMD-L-5005 output face, but it is general: point it at any
AP203/AP214 part whose features are coaxial with one axis.

    python ref/step_dump.py ref/RMD-L-5005-S.STEP

WHY IT DOES NOT JUST GREP CYLINDRICAL_SURFACE
---------------------------------------------
A `CYLINDRICAL_SURFACE` carries a radius and an `AXIS2_PLACEMENT_3D`. That
placement's location is a point on the surface's *infinite* axis and is under no
obligation to lie anywhere near the actual face. On the RMD-L file those points
land at x = -70.3 and x = +49.97 on a part that is 23.9 mm long. Reading them as
positions is how you invent a dimension.

So this walks the topology instead:

    ADVANCED_FACE -> FACE_OUTER_BOUND / FACE_BOUND -> EDGE_LOOP
                  -> ORIENTED_EDGE -> EDGE_CURVE -> VERTEX_POINT -> CARTESIAN_POINT

and takes the extent of a face from the vertices that actually bound it. It
deliberately ignores LINE and CONICAL_SURFACE base points for the same reason
(a LINE's origin is an arbitrary point on an unbounded line; a cone's apex can
be metres away).

Bodies are separated by CLOSED_SHELL, which is what tells you whether a face
belongs to the rotor or to the stator.
"""
import math
import re
import sys
from collections import Counter, defaultdict


def split_args(s):
    """Split a STEP argument list at top-level commas, respecting quotes/parens."""
    out, depth, cur, instr = [], 0, [], False
    i = 0
    while i < len(s):
        ch = s[i]
        if instr:
            cur.append(ch)
            if ch == "'":
                if i + 1 < len(s) and s[i + 1] == "'":
                    cur.append(s[i + 1]); i += 1
                else:
                    instr = False
        elif ch == "'":
            instr = True; cur.append(ch)
        elif ch == "(":
            depth += 1; cur.append(ch)
        elif ch == ")":
            depth -= 1; cur.append(ch)
        elif ch == "," and depth == 0:
            out.append("".join(cur).strip()); cur = []
        else:
            cur.append(ch)
        i += 1
    if cur:
        out.append("".join(cur).strip())
    return out


class Step:
    def __init__(self, path):
        src = open(path, "r", errors="replace").read()
        body = src[src.index("DATA;") + 5: src.rindex("ENDSEC;")]
        self.e = {int(m.group(1)): (m.group(2), m.group(3)) for m in
                  re.finditer(r"#(\d+)\s*=\s*([A-Z_0-9]+)\s*\((.*?)\)\s*;", body, re.S)}

    def ref(self, a):
        a = a.strip()
        return int(a[1:]) if a.startswith("#") else None

    def reflist(self, a):
        return [self.ref(x) for x in split_args(a.strip().lstrip("(").rstrip(")"))
                if x.strip().startswith("#")]

    def vec(self, eid):
        a = split_args(self.e[eid][1])
        c = [float(x) for x in split_args(a[1].strip().lstrip("(").rstrip(")"))]
        while len(c) < 3:
            c.append(0.0)
        return tuple(c)

    def placement(self, eid):
        a = split_args(self.e[eid][1])
        axis = self.vec(self.ref(a[2])) if len(a) > 2 and self.ref(a[2]) else (0., 0., 1.)
        return self.vec(self.ref(a[1])), axis

    def face_vertices(self, eid, acc=None, seen=None):
        """Vertices bounding a face - the only trustworthy source of extent."""
        acc = [] if acc is None else acc
        seen = set() if seen is None else seen
        if eid in seen or eid not in self.e:
            return acc
        seen.add(eid)
        t, args = self.e[eid]
        a = split_args(args)
        if t == "ADVANCED_FACE":
            for b in self.reflist(a[1]):
                self.face_vertices(b, acc, seen)
        elif t in ("FACE_OUTER_BOUND", "FACE_BOUND"):
            if self.ref(a[1]):
                self.face_vertices(self.ref(a[1]), acc, seen)
        elif t == "EDGE_LOOP":
            for x in self.reflist(a[1]):
                self.face_vertices(x, acc, seen)
        elif t == "ORIENTED_EDGE":
            if self.ref(a[3]):
                self.face_vertices(self.ref(a[3]), acc, seen)
        elif t == "EDGE_CURVE":
            for i in (1, 2):                       # start/end vertex only
                if self.ref(a[i]):
                    self.face_vertices(self.ref(a[i]), acc, seen)
        elif t == "VERTEX_POINT":
            acc.append(self.vec(self.ref(a[1])))
        return acc


def main(path):
    s = Step(path)
    print(f"{len(s.e)} entities from {path}")

    # dominant axis, from the cylinders
    axes = Counter()
    for eid, (t, args) in s.e.items():
        if t != "CYLINDRICAL_SURFACE":
            continue
        _, ax = s.placement(s.ref(split_args(args)[1]))
        n = math.hypot(*ax) or 1
        u = tuple(round(c / n, 6) for c in ax)
        for c in u:                                 # collapse +/-
            if abs(c) > 1e-9:
                if c < 0:
                    u = tuple(-x for x in u)
                break
        axes[u] += 1
    MAIN = axes.most_common(1)[0][0]
    ai = max(range(3), key=lambda i: abs(MAIN[i]))
    print(f"main axis {MAIN}  ({len(axes)} distinct cylinder axes)")

    def A(p): return p[ai]
    def R(p): return math.sqrt(sum(p[i] ** 2 for i in range(3) if i != ai))

    faces = {eid: s.face_vertices(eid) for eid, (t, _) in s.e.items() if t == "ADVANCED_FACE"}
    surf = {eid: s.ref(split_args(s.e[eid][1])[2]) for eid in faces}

    shells = {eid: s.reflist(split_args(args)[1])
              for eid, (t, args) in s.e.items() if t == "CLOSED_SHELL"}

    print("\n=== SOLID BODIES ===")
    order = []
    for sh, fl in shells.items():
        pts = [p for f in fl for p in faces.get(f, [])]
        if pts:
            order.append((min(A(p) for p in pts), sh, len(fl), max(A(p) for p in pts),
                          max(R(p) for p in pts)))
    for a0, sh, nf, a1, rmax in sorted(order):
        print(f"  shell#{sh:<6} faces={nf:<4} axial {a0:+8.3f}..{a1:+8.3f}"
              f"  Rmax={rmax:7.3f}  D={2 * rmax:7.3f}")

    print("\n=== COAXIAL SURFACES, BY BODY (true vertex-bounded extents) ===")
    for a0, sh, nf, a1, rmax in sorted(order):
        print(f"\n  --- shell#{sh}  axial {a0:+.3f}..{a1:+.3f}  Dmax={2 * rmax:.3f} ---")
        rows = set()
        for f in shells[sh]:
            su, pts = surf.get(f), faces.get(f, [])
            if not pts or su not in s.e:
                continue
            t, args = s.e[su]
            a = split_args(args)
            fa = [A(p) for p in pts]
            fr = [R(p) for p in pts]
            if t == "CYLINDRICAL_SURFACE":
                loc, ax = s.placement(s.ref(a[1]))
                n = math.hypot(*ax) or 1
                if abs(ax[ai] / n) > 0.999:
                    rows.add(("CYL", round(2 * float(a[2]), 4), round(min(fa), 4),
                              round(max(fa), 4), round(R(loc), 4)))
            elif t == "PLANE":
                loc, ax = s.placement(s.ref(a[1]))
                n = math.hypot(*ax) or 1
                if abs(ax[ai] / n) > 0.999 and max(fa) - min(fa) < 0.01:
                    rows.add(("PLANE", round(2 * max(fr), 4), round(min(fa), 4),
                              round(max(fa), 4), round(2 * min(fr), 4)))
            elif t == "CONICAL_SURFACE":
                loc, ax = s.placement(s.ref(a[1]))
                n = math.hypot(*ax) or 1
                if abs(ax[ai] / n) > 0.999:
                    rows.add(("CONE", round(2 * max(fr), 4), round(min(fa), 4),
                              round(max(fa), 4), round(2 * min(fr), 4)))
        for kind, d, x0, x1, extra in sorted(rows, key=lambda r: (r[2], -r[1])):
            tag = {"CYL": "axis offset", "PLANE": "inner D", "CONE": "other D"}[kind]
            print(f"    {kind:<6} D={d:8.3f}  axial {x0:+8.3f}..{x1:+8.3f}"
                  f" (len {x1 - x0:6.3f})  {tag}={extra:.3f}")

    allv = [s.vec(s.ref(split_args(args)[1]))
            for eid, (t, args) in s.e.items() if t == "VERTEX_POINT"]
    print(f"\n=== ENVELOPE ({len(allv)} vertices) ===")
    print(f"  axial {min(A(p) for p in allv):+.4f} .. {max(A(p) for p in allv):+.4f}"
          f"   length {max(A(p) for p in allv) - min(A(p) for p in allv):.4f}")
    print(f"  Rmax  {max(R(p) for p in allv):.4f}   D {2 * max(R(p) for p in allv):.4f}")

    print("\n=== RADIAL MAX BY AXIAL BAND (does anything stand out of the barrel?) ===")
    band = defaultdict(list)
    for p in allv:
        band[math.floor(A(p))].append(R(p))
    for x in sorted(band):
        print(f"  {x:+4d}..{x + 1:<4d} n={len(band[x]):4d}  Rmax={max(band[x]):8.4f}"
              f"  D={2 * max(band[x]):8.4f}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "ref/RMD-L-5005-S.STEP")
