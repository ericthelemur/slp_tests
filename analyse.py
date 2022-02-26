import argparse
import csv
from glob import glob
import random
import re
import struct

# Cmd line args Parser
parser = argparse.ArgumentParser("analyse")
parser.add_argument("filename", help="filename of Cooja radio log to analyse", type=str)
parser.add_argument("target", help="Node ID of node to treat as target", type=int)
parser.add_argument("--follow-rpl", "-r", action='store_true')
parser.add_argument("--start-time", "-s", type=int, default=0)
args = parser.parse_args()

# Program state
hunter_pos = 1
target = args.target
messages, moves, broadcasts = 0, 0, 0
recieved = set()

# Converts log's hex string to ASCII string
def hexdec(data):
    d = bytes.fromhex((data.split(": ")[1]  # Remove leading length
                    )[2:]               # Remove leading 0x
                    .replace(" ", "")   # Removes spaces
                    .lower())           # Lowercase
    return d

def hexstr(data):
    # if isinstance(data, str): data = hexdec(data)
    return "".join([chr(c) if str.isalnum(chr(c)) else "." for c in data])    # Filter non-alphanumeric characters


def read_header(fmt, data):
    size = struct.calcsize(fmt)
    print(size, data)
    info = struct.unpack(fmt, data[:size-1])
    return data[size:], info

def main():
    global hunter_pos, messages, moves, broadcasts
    with open(args.filename) as log:
        lines = csv.reader(log, delimiter="\t")
        for line in lines:
            messages += 1
            # Extract log line data
            time, _, _, data = line
            if time < args.start_time: continue

            # dest = [] if dest == "-" else list(map(int, dest.split(",")))
            # send = int(send)
            data = hexdec(data)
            if (len(data) < 13): continue
            dest, src = int(data[5]), int(data[13])

            # srcip, destip, datalen, _, prot, srcport, destport, datalen, csum = struct.unpack("LLBBHHHHH", data[:28])
            # data, (srcip, destip, _, pr, length) = read_header("LLBBH", data)
            # print(f"{src=} {dest=} {data=}")

            # print(list(map(int(data[:4]))))

            # Move if transmission detected
            if hunter_pos == dest:
                if args.follow_rpl or "hello" in hexstr(data):
                    print(f"{time=} {hunter_pos=} {src=} {dest=} {target=} {hexstr(data)=}")
                    move(time, src, dest, data)
            output()

            # Count broadcasts from source
            if "hello" in hexstr(data) and src == target:
                broadcasts += 1

            # Check if hunter reached target
            if hunter_pos == target:
                complete()
                break


def move(time, src, dest, data):
    global hunter_pos, moves

    print(f"\tMove {hunter_pos} to {src}")
    hunter_pos = src
    moves += 1

def output():
    # print(f"Hunter at {hunter_pos}")
    pass

def complete():
    print(f"Hunter found the target with {messages=} {moves=} and {broadcasts=}")


if __name__ == "__main__":
    main()



    # if args.ignoredups:
        # if data in recieved:
        #     return
        # if m := re.match("hello.(\d+)", data):
        #     numb = int(m.group(1))
        #     if numb in recieved: return
        #     else: recieved.add(numb)
        # print(recieved)