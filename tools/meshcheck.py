#!/usr/bin/env python3
"""Mass properties and watertightness for exported STLs.

    python tools/meshcheck.py build/model/*.stl

Two things this does deliberately:

1. IT COMPUTES EVERYTHING TWICE. Volume, centre of mass and watertightness are
   derived from a hand-rolled divergence-theorem sum over the triangles AND from
   trimesh, and the two are compared. They must agree to 1e-6 relative or the
   file says so. A previous round of this project shipped a defect because a
   mass property was read out of a tool and believed; agreement between two
   independent implementations is cheap insurance.

2. IT SHOUTS ABOUT THE COORDINATE FRAME. A centre of mass is meaningless
   without knowing which frame it is in. Exporting a part in PRINT orientation
   and then reading its CoM as if it were in MODEL coordinates is a defect that
   actually shipped here. Pass --frame to label the file, and the report repeats
   the label on every line so it cannot be mistaken.

Volume of a closed triangle mesh, by the divergence theorem:
    V   = (1/6) * sum over triangles of  a . (b x c)
    C   = (1/24) * sum of (a+b) x-terms ... integrated per axis, / V
Both reduce to a sum over triangles with no meshing assumptions beyond
"closed and consistently wound".
"""
import glob
import struct
import sys

import numpy as np


def read_stl(path):
    """Read binary or ASCII STL -> (n,3,3) float64 array of triangle vertices."""
    with open(path, "rb") as f:
        head = f.read(84)
        if len(head) < 84:
            raise ValueError(f"{path}: too short to be an STL")
        # ASCII STLs start with 'solid' but so do some binary ones; trust the
        # declared triangle count against the real file length instead.
        n = struct.unpack("<I", head[80:84])[0]
        f.seek(0, 2)
        size = f.tell()
        if size == 84 + n * 50:
            f.seek(84)
            buf = np.frombuffer(f.read(n * 50), dtype=np.uint8).reshape(n, 50)
            tris = buf[:, 12:48].copy().view("<f4").reshape(n, 3, 3)
            return tris.astype(np.float64)
    # ASCII fallback
    verts = []
    with open(path, "r", errors="replace") as f:
        for line in f:
            s = line.strip()
            if s.startswith("vertex"):
                verts.append([float(x) for x in s.split()[1:4]])
    if len(verts) % 3:
        raise ValueError(f"{path}: ASCII vertex count {len(verts)} not a multiple of 3")
    return np.asarray(verts, dtype=np.float64).reshape(-1, 3, 3)


def props(tris):
    """Volume (mm^3) and centre of mass (mm) by the divergence theorem."""
    a, b, c = tris[:, 0, :], tris[:, 1, :], tris[:, 2, :]
    cross = np.cross(b, c)
    sixv = np.einsum("ij,ij->i", a, cross)       # 6 * signed volume of tetra
    vol = sixv.sum() / 6.0
    if abs(vol) < 1e-12:
        return 0.0, np.zeros(3)
    # centroid of each tetra (0,a,b,c) is (a+b+c)/4, weighted by its signed volume
    cent = (a + b + c) / 4.0
    com = (cent * sixv[:, None]).sum(axis=0) / sixv.sum()
    return vol, com


def watertight(tris, tol=1e-6):
    """Every edge used exactly twice, in opposite directions -> closed & oriented."""
    q = np.round(tris.reshape(-1, 3) / tol).astype(np.int64)
    _, idx = np.unique(q, axis=0, return_inverse=True)
    idx = idx.reshape(-1, 3)
    e = np.vstack([idx[:, [0, 1]], idx[:, [1, 2]], idx[:, [2, 0]]])
    keyed = np.sort(e, axis=1)
    uniq, counts = np.unique(keyed, axis=0, return_counts=True)
    bad_count = int((counts != 2).sum())
    # orientation: each undirected edge should appear once each way
    fwd = set(map(tuple, e))
    rev = sum(1 for u, v in fwd if (v, u) not in fwd)
    return bad_count == 0 and rev == 0, bad_count, rev, len(uniq)


PETG_DENSITY = 1.27e-3    # g/mm^3


def report(path, frame, density):
    tris = read_stl(path)
    vol, com = props(tris)
    ok, bad, rev, nedges = watertight(tris)
    lo = tris.reshape(-1, 3).min(axis=0)
    hi = tris.reshape(-1, 3).max(axis=0)

    # independent cross-check
    x_vol = x_com = None
    x_wt = None
    try:
        import trimesh
        # process=True (the default) MERGES duplicate vertices. STL stores every
        # triangle's corners independently, so without merging trimesh sees a
        # cloud of unconnected triangles and calls every watertight solid leaky.
        # Loading with process=False here produced a false "not watertight" on
        # all six parts, which is exactly the kind of believed-tool-output this
        # cross-check exists to catch.
        m = trimesh.load(path, process=True)
        x_vol, x_com, x_wt = float(m.volume), np.asarray(m.center_mass), bool(m.is_watertight)
    except Exception as exc:                       # noqa: BLE001
        x_note = str(exc)

    name = path.replace("\\", "/").split("/")[-1]
    print(f"\n=== {name}   [frame: {frame}] ===")
    print(f"  triangles      {len(tris)}")
    print(f"  watertight     {'YES' if ok else 'NO'}"
          + ("" if ok else f"   ({bad} edges not used exactly twice, {rev} unpaired directions)"))
    print(f"  volume         {vol:12.3f} mm^3")
    print(f"  mass @{density * 1000:.2f} g/cm3  {vol * density:9.3f} g")
    print(f"  centre of mass ({com[0]:8.3f}, {com[1]:8.3f}, {com[2]:8.3f})  [frame: {frame}]")
    print(f"  bbox           X {lo[0]:8.3f}..{hi[0]:8.3f}   Y {lo[1]:8.3f}..{hi[1]:8.3f}"
          f"   Z {lo[2]:8.3f}..{hi[2]:8.3f}")
    print(f"  size           {hi[0] - lo[0]:.2f} x {hi[1] - lo[1]:.2f} x {hi[2] - lo[2]:.2f} mm")

    if x_vol is not None:
        dv = abs(x_vol - vol) / max(abs(vol), 1e-9)
        dc = float(np.max(np.abs(x_com - com)))
        agree = dv < 1e-6 and dc < 1e-6 and x_wt == ok
        print(f"  cross-check    trimesh vol {x_vol:.3f} (rel diff {dv:.2e}), "
              f"CoM max diff {dc:.2e}, watertight {x_wt}  -> "
              + ("AGREE" if agree else "*** DISAGREE ***"))
    return {"file": name, "frame": frame, "volume": vol, "mass": vol * density,
            "com": com.tolist(), "watertight": ok,
            "bbox": [lo.tolist(), hi.tolist()]}


def main(argv):
    frame = "UNSTATED - say --frame model or --frame print"
    density = PETG_DENSITY
    paths = []
    i = 0
    while i < len(argv):
        if argv[i] == "--frame":
            frame = argv[i + 1]; i += 2
        elif argv[i] == "--density":
            density = float(argv[i + 1]); i += 2
        else:
            paths.extend(sorted(glob.glob(argv[i]))); i += 1
    if not paths:
        print(__doc__)
        return 1
    rows = [report(p, frame, density) for p in paths]
    tot_v = sum(r["volume"] for r in rows)
    print(f"\n=== TOTAL over {len(rows)} part(s) ===")
    print(f"  volume {tot_v:.1f} mm^3    mass {tot_v * density:.2f} g   [frame: {frame}]")
    leaky = [r["file"] for r in rows if not r["watertight"]]
    if leaky:
        print(f"  NOT WATERTIGHT: {', '.join(leaky)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
