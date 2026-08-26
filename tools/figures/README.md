# Annotated photo figures — generators

One script per `docs/assets/photo-anno-*.jpg`. Each holds a `COORDS` dict of
pad/pin positions **in original-photo pixels** — the provenance for every ring
and wire the published figure draws — and composes the figure with Pillow.

Inputs are the clean camera originals in `C:\Claude\PrototypeImages`
(IMG_2449 = ESP32-C6, IMG_2450 = Valent X tape, IMG_2452 = PCA9685,
IMG_2456 = ULN2803A); output paths point at the session scratchpad they were
authored in. To regenerate, fix both path sets at the top of the script and
run `python <name>_gen.py` — then copy the render over the published asset.

| Script | Publishes |
|---|---|
| `two-hubs_gen.py` | `photo-anno-two-hubs.jpg` |
| `zone1-chain_gen.py` | `photo-anno-zone1-chain.jpg` |
| `uln-map_gen.py` | `photo-anno-uln-map.jpg` |
| `a0-bridge_gen.py` | `photo-anno-a0-bridge.jpg` |
