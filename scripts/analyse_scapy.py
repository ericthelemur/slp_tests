
# find results/1 -type f -name "*.pcap" | grep -v _ | xargs -L 1 python3 scripts/analyse_scapy.py -w
from scapy.all import *
from scapy.config import conf
import argparse

ip2str = Net6.int2ip
conf.dot15d4_protocol = "sixlowpan"

# Cmd line args Parser
parser = argparse.ArgumentParser("analyse")
parser.add_argument("filename", help="filename of Cooja radio log to analyse", type=str)
parser.add_argument("--target", "-t", help="Node ID of node to treat as target", type=int, default=None)
parser.add_argument("--start-time", "-s", type=float, default=0)
parser.add_argument("--duration", "-d", type=float, default=None)
parser.add_argument("--write-outfile", "-w", action='store_true')
args = parser.parse_args()

if args.target:
    if ":" in args.target: args.target = "::c10c:0:0:" + args.target    # Target can be node index or full IP
    args.target = Net6.ip2int(args.target)
else: args.target = None

sink = Net6.ip2int("::c10c:0:0:1")

print(args.filename)

class Analyser:
    def __init__(self, hunter_start, target, start_time, duration, packets):
        self.hunter_pos = hunter_start
        self.target = target
        self.messages, self.moves, self.broadcasts, self.recieved = 0, 0, 0, 0
        self.broadcast_start_time = None
        self.packets = packets
        self.iterator = enumerate(packets)

        time = -1
        for i, p in self.iterator:
            # If no given target, assume src of 1st UDP packet
            if self.target is None and UDP in p: 
                self.target = p[Dot15d4Data].src_addr
                self.broadcast_start_time = p.time
            if self.broadcast_start_time is None: continue  # Skip packets until started

            # Skip until start time, and end at end time
            time = p.time - self.broadcast_start_time
            if time < start_time: continue
            if duration and time > start_time + duration: break

            self.hunter_move(i, p)

            if self.hunter_pos == self.target:    # Target found check
                print(f"Hunter found the target with {self.messages=} {self.moves=} {self.broadcasts=} {self.recieved=}")
                self.result_write()
                return
        
        if duration and time > start_time + duration: print(f"PCAP exhausted before duration")
        print(f"Target not found in alloted time")
        self.result_write(False)


    def hunter_move(self, index, p):
        self.messages += 1

        # Follow UDP only
        if UDP in p:
            src = p[Dot15d4Data].src_addr
            dest = p[Dot15d4Data].dest_addr
            print(p.time - self.broadcast_start_time, f"hunter {ip2str(self.hunter_pos)} src {ip2str(src)} dest {ip2str(dest)} target {ip2str(self.target)}")
            if dest == self.hunter_pos:     # If recived at hunter pos, follow
                time = p.time - self.broadcast_start_time
                print(f"Hunter to {ip2str(src)}")
                self.hunter_pos = src
                self.moves += 1
        
            if src == self.target: self.broadcasts += 1  # Count broadcasts (once per bc at target)
            if dest == sink: self.recieved += 1  # Count recieved (once per bc at sink)


    def result_write(self, found=True):
        outfile = os.path.join(os.path.split(args.filename)[0], "out.json")
        content = {"found": found, "messages": self.messages, "moves": self.moves, "broadcasts": self.broadcasts, "recieved": self.recieved}
        print(outfile, content)
        if not args.write_outfile: return
        with open(outfile, "w") as f:
            f.write(str(content))

analyser = Analyser(sink, args.target, args.start_time, args.duration, PcapReader(args.filename))
