from pathlib import Path
import shutil, os, re

# Move **/ex000/out.json to **/ex000.json
for f in Path(".").rglob("out.json"):
    shutil.move(f, f.parent.parent / (f.parent.name + ".json"))

for f in Path(".").rglob("ex*.json"):
    sq = f.parent
    th = sq.parent
    bc = th.parent
    sq, bc, th = sq.name, bc.name, th.name
    dest = Path(".") / bc / sq / th
    dest.mkdir(parents=True, exist_ok=True)
    shutil.move(f, dest / f.name)
    # shutil.move(f, f.parent.parent / (f.parent.name + ".json"))

