
# python3 scripts/generategrid.py -t square5 -r 5 -n 25
from math import floor, log10
import random
import argparse
import os

# Cmd line arguments
parser = argparse.ArgumentParser("generategrid")
parser.add_argument("--target-folder", "-t", type=str, default="", help="Target directory for output")
parser.add_argument("--radius", "-r", type=int, default=3, help="Radius of grid, result will be (2r+1) square, centred on server")
parser.add_argument("--separation", "-s", type=float, default=40, help="Separation between nodes")
parser.add_argument("--number", "-n", type=int, default=10, help="Number of cases to generate")
parser.add_argument("--output-name", "-o", type=str, default="ex", help="Prefix on generated files")
parser.add_argument("--template", type=str, default="template.csc", help="Template file for .csc")
parser.add_argument("--node-template", type=str, default="nodetemplate.csc", help="Template file per node in .csc")
parser.add_argument("--script-template", type=str, default="templatescript.js", help="Template test script to generate with")
parser.add_argument("--pcap-name", "-p", type=str, default="{{TITLE}}", help="Prefix of the pcap file. Final files will be <p><case no>.pcap for combined and <p><case no>_<node id>.pcap per node")
parser.add_argument("--init-numb", "-i", type=int, default=1, help="Number to start numbering from -- useful if generating extra test examples")


args = parser.parse_args()

SERVER_POS = (0, 0)
zeroes = floor(log10(args.init_numb + args.number)) + 1

os.makedirs(os.path.join("gen", args.target_folder), exist_ok=True)

# Read template files
with open(args.template) as f:
    template = f.read()

with open(args.node_template) as f:
    node_template = f.read() + "\n"

# Create files
for file_no in range(args.init_numb, args.init_numb + args.number):
    # file_no += 1
    broad_id = random.randrange(1, (args.radius*2 + 1) ** 2)
    nodes = ""

    # Write nodes
    id = 1
    for i in range(-args.radius, args.radius+1):
        for j in range(-args.radius, args.radius+1):
            if (i, j) == SERVER_POS: continue   # Server pos (0, 0) already written
            id += 1
            # Replace placeholders in template
            nodes += (node_template.replace("{{X}}", str(i * args.separation))
                                   .replace("{{Y}}", str(j * args.separation))
                                   .replace("{{ID}}", str(id))
                                   .replace("{{TYPE}}", 'broadcast' if id == broad_id else 'middle')
            )

    # Write to file
    pad_file_no = str(file_no).zfill(zeroes)
    title = f"{args.output_name}{pad_file_no}"
    fname = title + ".csc"
    with open(os.path.join("gen", args.target_folder, fname), "w") as file:
        file.write(
            # Replace placeholders in template
            template.replace("{{SEED}}", f"{random.randrange(1000000)}")
                    .replace("{{PCAP}}", os.path.join("out", args.target_folder, title, f"{args.pcap_name}"))
                    .replace("{{TITLE}}", title)
                    .replace("{{NODES}}", nodes)
        )

# Copy js script over
with open(os.path.join("gen", args.target_folder, "testscript.js"), "w") as opfile:
    with open(args.script_template) as infile:
        opfile.write(infile.read()
                        .replace("{{RADIUS}}", args.radius)
        )