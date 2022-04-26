#!/bin/bash
#
#SBATCH --job-name=slp-rand-0.1  # Job name for tracking
#SBATCH --partition=desktop-batch  # Partition you wish to use (see above for list)
#SBATCH --cpus-per-task=6      # Number of CPU cores used by your job
#SBATCH --mem-per-cpu=5000     # RAM in MB needed per core (i.e. 3000MB * 1 cores = 3GB RAM)
#SBATCH --time=1-00:00:00      # Job time limit set to 2 days (48 hours), setting this lower may allow your job to run sooner
#
#SBATCH --mail-type=END,FAIL,TIME_LIMIT_80 # Events to send email on, remove if you don't want this
#SBATCH --output=slurm-%x_%j.out # Standard out from your job
#SBATCH --error=slurm-%x_%j.err  # Standard error from your job

label="rand"
export val=0.0
for val in 0.01 0.02 0.05 0.1
do
    echo "STARTING $val"

    function proj_conf_repl() {
        sed -i "s/#define OFF_TIMER_PROB .\+/#define OFF_TIMER_PROB $val/" "$1"
        echo "Replacing with $val"
    }
    export -f proj_conf_repl

    # grep --color=never square2/ex0 "square7/"
    find gen -type f -name "*.csc" -printf '%P\n' | grep --color=never "square7/" | ./scripts/run_all_tests.sh 0.1 RAND "$label_$val"
    echo "DONE WITH $val"
    sleep 5
done