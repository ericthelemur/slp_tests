#!/bin/bash
#
#SBATCH --job-name=slp-analyse  # Job name for tracking
#SBATCH --partition=cpu-batch  # Partition you wish to use (see above for list)
#SBATCH --time=0-01:00:00      # Job time limit set to 2 days (48 hours), setting this lower may allow your job to run sooner

#SBATCH --mail-type=END,FAIL,TIME_LIMIT_80 # Events to send email on, remove if you don't want this
#SBATCH --output=slurm-%x_%j.out # Standard out from your job
#SBATCH --error=slurm-%x_%j.err  # Standard error from your job

path="2022-04-25_1029-1.02-0.05-CUMUL_RAND"
source ../venv/bin/activate
find completed/$path -type f -name "*.pcap" | grep -P ex[0-9]+.pcap$ --color=never | parallel --lb --joblog "analyse-jobs-$path.log" python3.9 scripts/analyse_scapy.py -w -o {} :::