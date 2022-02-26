
# python3 scripts/graph_info.py 1 -n 1 -f results
from glob import glob
import json
import ast
import numpy as np
import matplotlib.pyplot as plt
import argparse
from collections import defaultdict

parser = argparse.ArgumentParser("analyse")
parser.add_argument("set", type=str)
parser.add_argument("-n", type=int, default=-1)
parser.add_argument("--title", "-t", type=str, default=None)
parser.add_argument("--folder", "-f", type=str, default="out")
args = parser.parse_args()

if args.title is None: args.title = f"SLP Properties of Standard RPL with {args.n}msg/s"

msgs, moves, bdcsts, rec = defaultdict(lambda: list()), defaultdict(lambda: list()), defaultdict(lambda: list()), defaultdict(lambda: list())
total, caps = defaultdict(lambda: 0), defaultdict(lambda: 0)

for d in sorted(glob(f"{args.folder}/{args.set}/square*")):
    print(d)
    n = int(d[-1])
    for f in glob(d + "/*/out.json"):
        with open(f) as file:
            data = ast.literal_eval(file.read())
            # print(data)
            if "found" in data:
                bdcsts[n].append(data["broadcasts"])
                rec[n].append(data["recieved"])
                total[n] += 1
                if bool(data["found"]):
                    msgs[n].append(data["messages"])
                    moves[n].append(data["moves"])
                    caps[n] += 1
print(msgs, moves, bdcsts, rec)

fig, ax = plt.subplots(2, 3)
fig.suptitle(args.title)

# def get_all(args):
#     for arg in args:
#         if isinstance(arg, dict):
#             for x in arg.values():
#                 yield x
#         else: yield arg

def plot_box(ax, data, title):
    ax.get_shared_x_axes().remove(ax)
    ax.get_shared_x_axes().remove(ax)

    bp = ax.boxplot(data.values(), meanline=True)
    ax.set_title(title)
    ax.set_xticklabels([f"{2*n+1}x{2*n+1}" for n in data.keys()])
    # labels = [f"{2*n+1}x{2*n+1}" for n in data.keys()]
    # print(labels)
    # ax.set_xticklabels(labels)
    # ax.set_ylim([vmin, vmax])
    return bp

def plot_bar(ax, data, title):
    ax.get_shared_x_axes().remove(ax)
    ax.get_shared_x_axes().remove(ax)

    bp = ax.bar(data.keys(), data.values())

    ax.set_title(title)
    # ax.set_xticks(data.keys(), [f"{2*n+1}x{2*n+1}" for n in data.keys()])
    # labels = [f"{2*n+1}x{2*n+1}" for n in data.keys()]
    # print(labels)
    # ax.set_xticklabels(labels)
    # ax.set_ylim([vmin, vmax])
    return bp

plot_box(ax[0, 0], msgs, "Messages until Capture")
plot_box(ax[1, 0], moves, "Hunter Moves until Capture")
plot_box(ax[0, 1], bdcsts, "Source Broadcasts")
plot_box(ax[1, 1], rec, "Sink Recieves")

cap_rat = {k: float(c)/total[k] for k, c in caps.items()}
plot_bar(ax[0, 2], cap_rat, "Capture Ratio")

del_rat = {k: float(sum(rec[k]))/sum(bdcsts[k]) for k in rec.keys()}
plot_bar(ax[1, 2], del_rat, "Delivery Ratio")

plt.show()
