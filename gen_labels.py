import glob
import os
import re

for d in sorted(glob.glob("*/*")):
    if "old" in d: continue
    files = filter(lambda x: os.path.isfile(x) and "_1.pcap" not in x, glob.glob(f"{d}/*_*.pcap"))
    max_file = max(files, key=lambda x: os.stat(x).st_size)
    node_no = re.search("_(\d+).pcap$", max_file).group(1)
    print(d, max_file, node_no)
    with open(f"{d}/info.json", "w") as f:
        f.write(str({"broadcast": int(node_no), "sink": 1}))