
# python3 scripts/graph_info.py "results/none/0.1" --title "No Disable Policy (0.1msg/s)" -b 0.1 -s
from glob import glob
import ast
import matplotlib.pyplot as plt
import argparse
from collections import defaultdict
from math import inf
from json import dumps
from os import path
import natsort

# Parse args
parser = argparse.ArgumentParser("analyse")
parser.add_argument("folder", type=str)
parser.add_argument("--title", "-t", type=str, default=None)
# parser.add_argument("--folder", "-f", type=str, default="out")
parser.add_argument("--violin", "-v", action='store_true')
# parser.add_argument("--safety-periods-file", type=str, default=None)
parser.add_argument("--safety-factor", type=float, default=1.5)
parser.add_argument("--save_data", "-s", action='store_true')
parser.add_argument("--no-window", "-w", action='store_true')
parser.add_argument("--bc-freq", "-b", type=float, default=None)
args = parser.parse_args()

if args.title is None: args.title = f"SLP Properties of Standard RPL with {args.n}msg/s"

# Default factory for the following dicts
def default(fac=list):
    # d = defaultdict(fac, {i: fac() for i in range(1, 7+1)})
    d = defaultdict(fac, {})
    return d

messages, moves, broadcasts, recieved = [default() for _ in range(4)]
start_time, found_time, end_time = [default() for _ in range(3)]

total, found = [default(lambda: 0) for _ in range(2)]

# Find and order subdirs
folders = glob(path.join(args.folder, "*"))
folders = natsort.realsorted(folders, key=lambda p: p.split("-"))

# Extract each case
for d in folders:
    n = path.basename(d)
    # Chop down square00off formats
    off = n.endswith("off")
    if off: n = n[:-3]
    if n.startswith("square"): 
        r = int(n[6:]) * 2 + 1
        n = f"{r}x{r}"
    if off: n += "o"
    
    for f in glob(d + "/*.json"):
        with open(f) as file:
            contents = file.read()
        try:    # Extract info
            data = ast.literal_eval(contents)
            if data["target"] is not None:
                # Register info
                broadcasts[n].append(data["broadcasts"])
                recieved[n].append(data["recieved"])
                start_time[n].append(data["start_time"])
                end_time[n].append(data["end_time"])
                total[n] += 1
                if bool(data["found"]): # Register is found info
                    # Find safety period
                    freq = float(n) if args.bc_freq == -1 else args.bc_freq
                    sp = None if freq is None else args.safety_factor * data["flood_bcs"] / freq
                    # if args.verbose: print(n, data["flood_bcs"], freq, sp, data["found_time"] - data["start_time"])
                    # If found within safety period, add
                    if (sp is None) or (sp >= data["found_time"] - data["start_time"]):
                        messages[n].append(data["messages"])
                        moves[n].append(data["moves"])
                        found_time[n].append(data["found_time"] - data["start_time"])
                        found[n] += 1
            else: print(f, "Target none")
        except (ValueError, KeyError):
            print(f, contents)
            raise

# Different sets of graphs
just_ratios = 0
have_times = 0

# params = {'xtick.labelsize':'x-small'}
# plt.rcParams.update(params)

if just_ratios:
    fig, ax = plt.subplots(1, 2)
    fig.set_figwidth(8)
    fig.set_figheight(5)
else: 
    fig, ax = plt.subplots(2, 3 + have_times)
    fig.set_figwidth(15 if have_times else 12)
    fig.set_figheight(9)
plt.suptitle(args.title, y=1.0)

# Plots overlaying boxplot
def plot_call(ax, data):
    return ax.boxplot(data.values(), showmeans=True, meanprops={"marker": "x", "color": "black"})

# Plot violin plot
def plot_call_violin(ax, data):
    ax.violinplot(data.values(), widths=0.9, showextrema=False)
    return ax.boxplot(data.values(), showmeans=True,
            meanprops=dict(marker='o',
                           markersize=10, zorder=3))

# Plot boxplot
def plot_box(ax, data, title):
    for k, l in data.items():
        if not l: l.append(0)
    if not data: return None, None
    ax.get_shared_x_axes().remove(ax)
    ax.get_shared_y_axes().remove(ax)

    bp = plot_call(ax, data)

    ax.set_title(title)
    # labels = [f"{2*n+1}x{2*n+1}" for n in data.keys()]
    labels = data.keys()
    ax.set_xticklabels(labels)

    # Get avgs
    medians = {k: l.get_ydata()[0] for k, l in zip(labels, bp['medians'])}
    means = {k: l.get_ydata()[0] for k, l in zip(labels, bp['means'])}
    print(title, f"\n\t{means=}\n\t{medians=}")
    return means, medians

if args.violin: plot_call = plot_call_violin

# Plot bar chart
def plot_bar(ax, data, title):
    ax.get_shared_x_axes().remove(ax)
    ax.get_shared_y_axes().remove(ax)

    bp = ax.bar(data.keys(), data.values())

    ax.set_ylim([0.0, 1.0])

    ax.set_title(title)
    vals = data
    
    print(title, vals)
    return vals

# Plot box/violin charts
if not just_ratios:
    cap_time_mean, cap_time_med = plot_box(ax[0, have_times], found_time, "Time until Capture")
    moves_mean, moves_med = plot_box(ax[0, have_times+1], moves, "Hunter Path Length until Capture")
    bc_mean, bc_med = plot_box(ax[1, have_times], broadcasts, "Source Broadcasts")
    rec_mean, rec_med = plot_box(ax[1, have_times+1], recieved, "Sink Recieves")

# Calc and plot cap ratio then del ratio
cap_ax = ax[0] if just_ratios else ax[0, have_times+2]
cap_rat = {k: float(c)/total[k] if total[k] else 0 for k, c in found.items()}
cap_rat = plot_bar(cap_ax, cap_rat, "Capture Ratio")

del_ax = ax[1] if just_ratios else ax[1, have_times+2]
del_rat = {k: 0 if not sum(broadcasts[k]) else (float(sum(recieved[k]))/sum(broadcasts[k])) for k in recieved.keys()}
del_rat = plot_bar(del_ax, del_rat, "Delivery Ratio")

# Draw and rotate axis to fit
plt.draw()
for a in ax:
    for tick in a.get_xticklabels():
        tick.set_rotation(25)

# 
if args.save_data: 
    # Save info
    with open(f"{args.folder}/avgs.json", "w") as f:
        if not just_ratios: 
            data = {"capture_time_mean": cap_time_mean, "capture_time_median": cap_time_med, "capture_ratio": cap_rat, "delivery_ratio": del_rat,
                    "moves_mean": moves_mean, "bc_mean": bc_mean, "rec_mean": rec_mean
            }
        else: data = {"capture_ratio": cap_rat, "delivery_ratio": del_rat}
        f.write(dumps(data, indent=4))
    plt.savefig(f"{args.folder}/{args.folder.split('/')[-1]}graph.png")

if not args.no_window:
    plt.show()
