find results/$1 -type f -name "*.pcap" | grep -v _ | xargs -L 1 python3 scripts/analyse_scapy.py -w
python3 scripts/graph_info.py $1 -n $1 -f results
