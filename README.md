# SLP Tests
`/scripts` provides all the scripted behaviour
`/gen` contains example tests, 100 per size 
`/test-batches` contains some of the (messy) code used to dispatch batch compute jobs
The `template*` files are used to generate examples

## Installation
1. In an empty directory (in this example `/home/owen/rpl`), clone this repository and https://github.com/ericthelemur/contiki-slp
    - Should be `rpl/slp-tests` and `rpl/contiki-slp`
    - More information on requirements for Contiki-NG can be found at https://github.com/contiki-ng/contiki-ng/wiki/Toolchain-installation-on-Linux
2. Install Python 3.8, with packets `scapy`, `matplotlib`, `natsort`
3. Run `slp_tests/scripts/finish_install.sh` to complete installation (note not fully tested)
    - It will link cooja and firmware dir, and populate `~/.cooja.user.properties`. If this file already exists it may require manual testing

## Use
All these scripts have various settings, just that standard ones are shown here.

- To generate new tests: `python3 scripts/generategrid.py -t <folder> -r <radius> -n <number of cases>` (e.g. for 15x15 grids, radius is 7)
- To run all cases in `/gen` cases: `./scripts/run_all_tests.sh <broadcast freq> <slp policy (NONE)> <batch label>`
    - To run specific tests (e.g. all 15x15 grids) `find <test containing folder> -type f -name "*.csc" -printf '%P\n' | grep --color=never "square7/" | ...`
    - Data will be in `running` until completion, when it will be moved to `completed`
- To analyse cases in parallel, call `find <path> -type f -name "*.pcap" | parallel --lb --joblog "logs/analyse-jobs.log" python3.9 scripts/analyse_scapy.py -w -o {} :::`

### Visualizing
- To graph, the program requires a directory in the structure `root/category/ex000.json` 
    - each subdir contains a flat structure of test cases
    - each case labelled by it's name, not `out.json`
- Since this depends on the data and variables required, this is semi-manually done. An example Python script to do this follows:
```python
from pathlib import Path
import shutil, os, re

# Move **/ex000/out.json to **/ex000.json
for f in Path(".").rglob("out.json"):
    shutil.move(f, f.parent.parent / (f.parent.name + ".json"))

# Restructure directories
for f in Path(".").rglob("ex*.json"):
    sq = f.parent   # squarexx
    bc = sq.parent  # broadcast freq
    sq, bc = sq.name, bc.name   # Convert from path to string
    dest = Path(".") / bc / sq
    # Create folder and move file in
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(f, dest)
```
- Then simply run `python3 scripts/graph_info.py "<root dir>" --title "<policy desc>" -b <broadcast freq> -s`
    - The broadcast frequency is used to ensure the safety period is correctly compared.