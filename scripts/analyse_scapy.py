
# find results-std-NONE-2022-04-09_0106 -type f -name "*.pcap" | grep -P ex[0-9]+.pcap$ --color=never | xargs -L 1 python3 scripts/analyse_scapy.py -w
from scapy.all import *
from scapy.layers.dot15d4 import Dot15d4Data, Dot15d4, Dot15d4FCS, Dot15d4Ack
from scapy.layers.inet import UDP
from scapy.config import conf
import argparse
from math import inf
from enum import Enum
import re

from typing import Set, Tuple

ip2str = Net6.int2ip
conf.dot15d4_protocol = "sixlowpan"

# Cmd line args Parser
parser = argparse.ArgumentParser("analyse")
parser.add_argument("filename", help="filename of Cooja radio log to analyse", type=str)
parser.add_argument("--target", "-t", help="Node ID of node to treat as target", type=int, default=None)
parser.add_argument("--start-delay", "-s", type=float, default=0)
parser.add_argument("--duration", "-d", type=float, default=inf)
parser.add_argument("--cleanup-time", "-c", type=float, default=1.0)
parser.add_argument("--write-outfile", "-w", action='store_true')
parser.add_argument("--verbose", "-v", action='store_true')
parser.add_argument("--overwrite", "-o", action='store_true')
args = parser.parse_args()

outpath = os.path.join(os.path.split(args.filename)[0], "out.json")
if not args.overwrite and os.path.exists(outpath):
    raise Exception(f"File {outpath} already exists. Use --overwrite to ignore")

if args.target:
    if ":" in args.target: args.target = "::c10c:0:0:" + args.target    # Target can be node index or full IP
    args.target = Net6.ip2int(args.target)
else: args.target = None

sink = Net6.ip2int("::c10c:0:0:1")

print(args.filename)

# Phase of hunter
class Phase(Enum):
    BeforeBaseline = 0  # Baseline is first data packet -- wait until network established to begin
    BeforeStart = 1     # Waits args.start_delay after baseline to start hunting
    Hunting = 2         # Actively following messages
    Found = 3           # Once hunter has found target, wait a little longer to finish delivery of this data (for bc stats)
    End = 4             # Search has ended with no capture

class Analyser:
    def __init__(self, hunter_start, target, start_delay, duration, cleanup_time, packets):
        self.hunter_pos = hunter_start
        self.target = target
        self.messages, self.moves, self.broadcasts, self.recieved = 0, 0, 0, 0
        self.time_baseline = None
        self.packets = packets
        self.iterator = enumerate(packets)

        self.end_time = None
        self.start_time = None

        self.phase = Phase.BeforeBaseline

        self.found_time = None
        self.last_payload = None
        self.init_time = None

        self.src_rec = set()
        for i, p in self.iterator:
            if self.init_time is None: self.init_time = p.time
            # if args.verbose: print(f"{p.time} {UDP in p} {p!r}")
            if args.verbose and UDP in p: 
                print(f"{p[UDP].payload!r}")

            # If no given target, assume src of 1st UDP packet
            if self.phase == Phase.BeforeBaseline:
                if UDP in p:    # Initialize baseline at first UDP packet
                    self.phase = Phase.BeforeStart
                    if self.target is None:
                        self.target = p[Dot15d4Data].src_addr
                    self.time_baseline = p.time
                    self.start_time = self.time_baseline + start_delay
                    self.end_time = self.start_time + duration
                    if args.verbose: print(f"\t{ip2str(self.target)=} {self.time_baseline=} {self.start_time=} {self.end_time=} {self.time_baseline == self.start_time=} {p.time >= self.start_time=}")
                else: continue

            # Skip until start time, and end at end time
            if self.phase == Phase.BeforeStart:
                if p.time >= self.start_time:
                    self.phase = Phase.Hunting
                else: continue  # Skip until past start time (usually instant)
            

            if self.phase == Phase.Hunting:
                if p.time > self.end_time:
                    break
                self.hunter_move(i, p)
                if self.hunter_pos == self.target:    # Target found check
                    self.phase = Phase.Found
                    print(f"Hunter found the target with {self.messages=} {self.moves=} {self.broadcasts=} {self.recieved=}")
                    self.found_time = p.time
                    self.last_payload = p[UDP].payload
                    self.end_time = min(self.end_time, self.found_time + cleanup_time)
                    if args.verbose: print(f"{self.found_time=} {self.last_payload=} {self.end_time=}")
                elif p.time > self.end_time:
                    self.phase = Phase.End
                    break
            
            elif self.phase == Phase.Found:
                # Finish delivery of message
                if UDP in p and p[UDP].payload == self.last_payload:
                    self.messages += 1
                    if p[Dot15d4Data].dest_addr == sink:
                        if p[UDP].payload.load not in self.src_rec:
                            self.src_rec.add(p[UDP].payload.load)
                            self.recieved += 1
                            if args.verbose: print(f"\t rc + 1 -> {self.recieved}")

                            # self.receiving[p[Dot15d4FCS].seqnum] = p.time
                            # if args.verbose: print("recieving", p[Dot15d4FCS].seqnum)

            if self.phase == Phase.Found or self.phase == Phase.End:
                if p.time > self.end_time:
                    break 

        if self.end_time == inf: self.end_time = p.time

        if self.phase != Phase.Found:
            print(f"PCAP exhausted before duration")
            self.result_write(False)
        else: self.result_write()

    def hunter_move(self, index, p):
        self.messages += 1

        # Follow UDP only
        if UDP in p:
            src = p[Dot15d4Data].src_addr
            dest = p[Dot15d4Data].dest_addr
            if args.verbose: print(p.time - self.time_baseline, f"hunter {ip2str(self.hunter_pos)} src {ip2str(src)} dest {ip2str(dest)} target {ip2str(self.target)}")

            if dest == self.hunter_pos:     # If recived at hunter pos, follow
                if args.verbose: print(f"Hunter to {ip2str(src)}")
                self.hunter_pos = src
                self.moves += 1
        
            if src == self.target: 
                self.broadcasts += 1  # Count broadcasts (once per bc at target)
                if args.verbose: print(f"\t bc + 1 -> {self.broadcasts}")
            if dest == sink:
                if p[UDP].payload.load not in self.src_rec:
                    self.src_rec.add(p[UDP].payload.load)
                    self.recieved += 1
                    if args.verbose: print(f"\t rc + 1 -> {self.recieved}")

    def est_flooding(self):
        if self.target is None:
            print("No target for", args.filename)
            return -1

        sink_str, target_str = Net6.int2ip(sink), Net6.int2ip(self.target)
        print(sink_str, target_str)
        if target_str == sink_str: return 0
        sink_x, sink_y = 0, 0
        r = int(re.search(r"square(\d+)/", args.filename)[1])

        i = target_id = int(target_str.split(":")[-1], 16)
        print(f"{r=} {target_id=}")
        f = lambda x, y: 2 + (2*r+1)*(x+r) + (y+r) - (x > sink_x or x == sink_x and y > sink_y)
        x = -r + (i-2 + (i > f(sink_x, sink_y))) // (2*r+1)
        y = -r + (i-2 + (i > f(sink_x, sink_y))) % (2*r+1)
        dist = abs(x) + abs(y)
        print(f"{dist=}")
        return dist

    def result_write(self, found=True):
        outfile = os.path.join(os.path.split(args.filename)[0], "out.json")
        content = {"found": found, "messages": self.messages, "moves": self.moves, "broadcasts": self.broadcasts, "recieved": self.recieved, "init_time": float(self.init_time),
                    "target": ip2str(self.target) if self.target else None,
                    "flood_bcs": self.est_flooding()}
        if self.start_time: content["start_time"] = float(self.start_time - self.init_time)
        if self.end_time: content["end_time"] = float(self.end_time - self.init_time)
        if self.found_time: content["found_time"] = float(self.found_time - self.init_time)
        if args.verbose: print(outfile, content)
        if not args.write_outfile: return
        with open(outfile, "w") as f:
            f.write(str(content))

analyser = Analyser(sink, args.target, args.start_delay, args.duration, args.cleanup_time, PcapReader(args.filename))
