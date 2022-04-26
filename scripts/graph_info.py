
# python3 scripts/graph_info.py 1 -n 1 -f results -v
from glob import glob
import json
import ast
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
from collections import defaultdict
from math import inf
from pprint import pprint, pformat
from json import dumps

# Parse args
parser = argparse.ArgumentParser("analyse")
parser.add_argument("n", type=str)
parser.add_argument("--title", "-t", type=str, default=None)
parser.add_argument("--folder", "-f", type=str, default="out")
parser.add_argument("--violin", "-v", action='store_true')
# parser.add_argument("--safety-periods-file", type=str, default=None)
parser.add_argument("--safety-factor", type=float, default=1.5)
parser.add_argument("--save_data", "-s", action='store_true')
parser.add_argument("--no-window", "-w", action='store_true')
parser.add_argument("--bc-freq", "-b", type=int, default=None)
args = parser.parse_args()

# Fetch safety periods
# safety_periods = {}
# if args.safety_periods_file is not None:
#     with open(f"{args.folder}/{args.n}/{args.safety_periods_file}") as file:
#         contents = file.read()
#         data = ast.literal_eval(contents)
#         for i in range(1, 7+1):
#             safety_periods[i] = data["resulting_safety_periods"][f"{2*i+1}x{2*i+1}"]
#     print(safety_periods)

if args.title is None: args.title = f"SLP Properties of Standard RPL with {args.n}msg/s"

def default(fac=list):
    d = defaultdict(fac, {i: fac() for i in range(1, 7+1)})
    print(d)
    return d

messages, moves, broadcasts, recieved = [default() for _ in range(4)]
start_time, found_time, end_time = [default() for _ in range(3)]

total, found = [default(lambda: 0) for _ in range(2)]

for d in sorted(glob(f"{args.folder}/{args.n}/square*")):
    print(d)
    n = int(d[-1])
    for f in glob(d + "/*/out.json"):
        with open(f) as file:
            contents = file.read()
            try:
                data = ast.literal_eval(contents)
                if data["target"] is not None:
                    if data["broadcasts"] > 900: continue
                    broadcasts[n].append(data["broadcasts"])
                    recieved[n].append(data["recieved"])
                    start_time[n].append(data["start_time"])
                    end_time[n].append(data["end_time"])
                    total[n] += 1
                    if bool(data["found"]):
                        if args.bc_freq is None or (data["flood_bcs"] * args.bc_freq >= data["found_time"] - data["start_time"]):
                        # if n not in safety_periods or (n in safety_periods and safety_periods[n] >= data["found_time"] - data["start_time"]):
                            messages[n].append(data["messages"])
                            moves[n].append(data["moves"])
                            found_time[n].append(data["found_time"] - data["start_time"])
                            found[n] += 1
                else: print(f, "Target none")
            except (ValueError, KeyError):
                print(f, contents)
                raise
            
# print(f"{messages=}\n{moves=}\n{broadcasts=}\n{recieved=}\n{start_time=}\n{found_time=}\n{end_time=}\n{total=}\n{found=}")

have_times = 0

params = {'xtick.labelsize':'x-small'}
plt.rcParams.update(params)

fig, ax = plt.subplots(2, 3 + have_times)
fig.set_figwidth(15 if have_times else 12)
fig.set_figheight(9)
fig.suptitle(args.title)

def plot_call(ax, data):
    return ax.boxplot(data.values(), showmeans=True, meanprops={"marker": "x", "color": "black"})

def plot_call_violin(ax, data):
    ax.violinplot(data.values(), widths=0.9, showextrema=False)
    return ax.boxplot(data.values(), showmeans=True,
            meanprops=dict(marker='o',
                           markersize=10, zorder=3))

def plot_box(ax, data, title):
    for k, l in data.items():
        if not l: l.append(0)
    if not data: return None, None
    ax.get_shared_x_axes().remove(ax)
    ax.get_shared_y_axes().remove(ax)

    bp = plot_call(ax, data)

    ax.set_title(title)
    labels = [f"{2*n+1}x{2*n+1}" for n in data.keys()]
    ax.set_xticklabels(labels)

    medians = {k: l.get_ydata()[0] for k, l in zip(labels, bp['medians'])}
    means = {k: l.get_ydata()[0] for k, l in zip(labels, bp['means'])}
    print(title, f"\n\t{means=}\n\t{medians=}")
    return means, medians

if args.violin: plot_call = plot_call_violin

def plot_bar(ax, data, title):
    ax.get_shared_x_axes().remove(ax)
    ax.get_shared_y_axes().remove(ax)

    bp = ax.bar([f"{2*n+1}x{2*n+1}" for n in data.keys()], data.values())
    ax.set_ylim([0.0, 1.0])

    ax.set_title(title)
    vals = {f"{2*n+1}x{2*n+1}": v for n, v in data.items()}
    print(title, vals)
    return vals

# have_times = 1
# st_mean, st_med = plot_box(ax[0, 0], start_time, "Start Time")
# et_mean, et_med = plot_box(ax[1, 0], end_time, "End Time")

cap_time_mean, cap_time_med = plot_box(ax[0, have_times], found_time, "Time until Capture")
moves_mean, moves_med = plot_box(ax[0, have_times+1], moves, "Hunter Path Length until Capture")
bc_mean, bc_med = plot_box(ax[1, have_times], broadcasts, "Source Broadcasts")
rec_mean, rec_med = plot_box(ax[1, have_times+1], recieved, "Sink Recieves")

cap_rat = {k: float(c)/total[k] if total[k] else 0 for k, c in found.items()}
cap_rat = plot_bar(ax[0, have_times+2], cap_rat, "Capture Ratio")

del_rat = {k: 0 if not sum(broadcasts[k]) else (float(sum(recieved[k]))/sum(broadcasts[k])) for k in recieved.keys()}
del_rat = plot_bar(ax[1, have_times+2], del_rat, "Delivery Ratio")

if args.save_data: 
    if args.safety_periods_file is None:
        with open(f"{args.folder}/{args.n}/avgs.json", "w") as f:
            sps = {k: v*args.safety_factor for k, v in cap_time_mean.items()}
            data = {"capture_time_mean": cap_time_mean, "capture_time_median": cap_time_med, "capture_ratio": cap_rat, "delivery_ratio": del_rat, "resulting_safety_periods": sps,
                    # "st_mean": st_mean, "et_mean": et_mean, 
                    "moves_mean": moves_mean, "bc_mean": bc_mean, "rec_mean": rec_mean
            }
            f.write(dumps(data, indent=4))
        plt.savefig(f"{args.folder}/{args.n}/graphs{args.n}.png")
    else:

        with open(f"{args.folder}/{args.n}/sf.json", "w") as f:
            sps = {k: v*args.safety_factor for k, v in cap_time_mean.items()}
            data = {"capture_ratio": cap_rat, "delivery_ratio": del_rat
            }
            f.write(dumps(data, indent=4))
        plt.savefig(f"{args.folder}/{args.n}/graphs{args.n}sf.png")

if not args.no_window: plt.show()
