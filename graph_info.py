
# python3.9 graph_info.py 100m -n 100
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

def chain(*args):
    for arg in args:
        for item in arg:
            yield item

def plot(ax, data, title):
    ax.get_shared_x_axes().remove(ax)
    ax.get_shared_x_axes().remove(ax)
    print("v", data.values())
    print("c", list(chain(data.values())))
    print("r", np.array(list(chain(data.values()))))
    vals = np.array(chain(data.values()))
    vbot = np.percentile(vals, 1)
    vtop = np.percentile(vals, 99)
    vpad = 0.2*(vtop - vbot)
    vmin = vbot - vpad
    vmax = vtop + vpad

    bp = ax.boxplot(data.values(), meanline=True)
    ax.set_xticklabels([f"{2*n+1}x{2*n+1}" for n in data.keys()])
    ax.set_title(title)
    ax.set_ylim([vmin, vmax])
    return bp

plot(ax[0, 0], msgs, "Messages")
plot(ax[1, 0], moves, "Hunter Moves until Capture")
plot(ax[0, 1], bdcsts, "Source Broadcasts")
plot(ax[1, 1], rec, "Sink Recieves")

cap_rat = {k: float(c)/total[k] for k, c in caps.items()}
plot(ax[1, 2], cap_rat, "Capture Ratio")

# cap_rat = {k: float(c)/total[k] for k, c in caps.items()}
# ax[1, 2].boxplot(cap_rat.values())
# ax[1, 2].set_xticklabels(labels)
# ax[1, 2].set_title("Capture Ratio")

# del_rat = {k: float(rec[k])/bdcsts[k] for k in rec.keys()}
# ax[1, 2].boxplot(rec.values())
# ax[1, 2].set_xticklabels(labels)
# ax[1, 2].set_title("Delivery Ratio")

plt.show()
