"""Rebuild docs/assets/site/scans/victoria-den.bin from the Victoria den pack.

The Home page's den scene (docs/assets/site/js/den-hero.js) draws the real
Victoria den scan. The design handoff did not include its victoria-den.bin, so
this script rebuilds an equivalent file from the source pack the handoff names,
local-2026-10-15-den-view-r1-v4 (owner's go-ahead, 2026-11-02):

    python tools/site/den_scan.py <pack>/points.ply docs/assets/site/scans/victoria-den.bin

Input: the pack's points.ply (binary little-endian, x y z float32 + intensity
uint8, Z-up metres, floor at z = 0), checked against the SHA-256 the pack's
content-pack.json records. Nothing else from the pack is read or published.

Output, in den-hero.js's own layout:
    uint32 M | float32 xyz * M | uint8 intensity * M | int8 normal * 3M

Steps, all deterministic:
  1. Crop to the den: inside the den walls quad that den-hero.js uses (WALLS),
     grown by MARGIN so the wall surfaces stay, and below CEILING_Z so the
     ceiling does not hide the room from den-hero's raised camera.
  2. Normals: the smallest principal axis of each point's neighbourhood (the
     points in its voxel and the 26 around it). den-hero lights one-sided
     (max(N.L, 0)), so normals are turned toward VIEW, a point above the middle
     of the den, where the virtual fixtures shine from.
  3. Keep at most MAX_POINTS (the count implied by den-hero's 11,494,964-byte
     fallback), then shuffle with a fixed seed: den-hero draws a prefix of the
     file on phones, so any prefix must be a uniform subset.

Needs numpy.
"""
import hashlib
import struct
import sys

import numpy as np

SOURCE_SHA256 = "632386351b3e7a0f035a9f8d8ec5847ab0b3d6ec8e3ea9ba17443ba5c1ac9c0a"
WALLS = np.array([[2.979687079, 0.666236254], [6.725373553, 0.717248738],
                  [6.645060137, 5.330365338], [2.899373664, 5.279352854]])
MARGIN = 0.15        # m outside the wall lines that is still kept
FLOOR_Z = -0.10      # m
CEILING_Z = 2.25     # m; the den's ceiling is at 2.39
VOXEL = 0.05         # m, neighbourhood cell for the normals
VIEW = np.array([4.81, 3.0, 1.8])
MAX_POINTS = (11494964 - 4) // 16
SEED = 20261015


def read_ply(path):
    data = open(path, "rb").read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != SOURCE_SHA256:
        sys.exit(f"{path}: SHA-256 {digest} is not the v4 pack's points.ply ({SOURCE_SHA256})")
    end = data.index(b"end_header\n") + len(b"end_header\n")
    header = data[:end].decode("ascii")
    expected = ["property float x", "property float y", "property float z", "property uchar intensity"]
    props = [ln for ln in header.splitlines() if ln.startswith("property")]
    if "binary_little_endian" not in header or props != expected:
        sys.exit("unexpected PLY layout:\n" + header)
    n = int(next(ln for ln in header.splitlines() if ln.startswith("element vertex")).split()[-1])
    rec = np.frombuffer(data, dtype=np.dtype([("x", "<f4"), ("y", "<f4"), ("z", "<f4"), ("i", "u1")]), count=n, offset=end)
    xyz = np.stack([rec["x"], rec["y"], rec["z"]], axis=1).astype(np.float64)
    return xyz, rec["i"].copy()


def inside_walls(xy):
    """True where a point lies inside the walls quad grown by MARGIN (convex, either winding)."""
    keep = np.ones(len(xy), dtype=bool)
    center = WALLS.mean(axis=0)
    for a, b in zip(WALLS, np.roll(WALLS, -1, axis=0)):
        edge = b - a
        normal = np.array([-edge[1], edge[0]]) / np.hypot(*edge)
        if np.dot(center - a, normal) < 0:
            normal = -normal                      # point the normal into the den
        keep &= (xy - a) @ normal > -MARGIN
    return keep


def normals(xyz):
    cells = np.floor(xyz / VOXEL).astype(np.int64)
    cells -= cells.min(axis=0) - 1                    # 1-based, so every neighbour index is >= 0
    span = cells.max(axis=0) + 2                      # ... and < span: keys never alias
    key = (cells[:, 0] * span[1] + cells[:, 1]) * span[2] + cells[:, 2]
    uniq, inv = np.unique(key, return_inverse=True)
    m = len(uniq)
    count = np.bincount(inv, minlength=m).astype(np.float64)
    s1 = np.stack([np.bincount(inv, xyz[:, k], m) for k in range(3)], axis=1)
    s2 = np.stack([np.bincount(inv, xyz[:, a] * xyz[:, b], m) for a in range(3) for b in range(3)], axis=1)
    n_tot, s1_tot, s2_tot = count.copy(), s1.copy(), s2.copy()
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                if dx == dy == dz == 0:
                    continue
                nb = uniq + (dx * span[1] + dy) * span[2] + dz
                j = np.searchsorted(uniq, nb)
                j = np.clip(j, 0, m - 1)
                hit = uniq[j] == nb
                n_tot[hit] += count[j[hit]]
                s1_tot[hit] += s1[j[hit]]
                s2_tot[hit] += s2[j[hit]]
    mean = s1_tot / n_tot[:, None]
    cov = s2_tot.reshape(-1, 3, 3) / n_tot[:, None, None] - mean[:, :, None] * mean[:, None, :]
    _, vecs = np.linalg.eigh(cov)
    cell_n = vecs[:, :, 0]                            # smallest eigenvalue's axis
    cell_n[n_tot < 3] = (0.0, 0.0, 1.0)               # too sparse for a plane
    n = cell_n[inv]
    flip = np.einsum("ij,ij->i", n, VIEW - xyz) < 0
    n[flip] *= -1
    return n


def main(src, out):
    xyz, inten = read_ply(src)
    keep = inside_walls(xyz[:, :2]) & (xyz[:, 2] > FLOOR_Z) & (xyz[:, 2] < CEILING_Z)
    xyz, inten = xyz[keep], inten[keep]
    nrm = normals(xyz)
    rng = np.random.default_rng(SEED)
    order = rng.permutation(len(xyz))[:MAX_POINTS]
    xyz, inten, nrm = xyz[order], inten[order], nrm[order]
    m = len(xyz)
    n8 = np.clip(np.round(nrm * 127), -127, 127).astype(np.int8)
    with open(out, "wb") as f:
        f.write(struct.pack("<I", m))
        f.write(xyz.astype("<f4").tobytes())
        f.write(inten.astype(np.uint8).tobytes())
        f.write(n8.tobytes())
    print(f"kept {keep.sum()} of {len(keep)} points inside the den; wrote {m} to {out} "
          f"({4 + m * 16} bytes); z {xyz[:, 2].min():.2f}..{xyz[:, 2].max():.2f} m")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
