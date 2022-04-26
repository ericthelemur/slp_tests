#!/bin/bash
#
#SBATCH --job-name=slp-0.1-cuml-rand-0.1  # Job name for tracking
#SBATCH --partition=desktop-batch  # Partition you wish to use (see above for list)
#SBATCH --cpus-per-task=6      # Number of CPU cores used by your job
#SBATCH --mem-per-cpu=5000     # RAM in MB needed per core (i.e. 3000MB * 1 cores = 3GB RAM)
#SBATCH --time=2-00:00:00      # Job time limit set to 2 days (48 hours), setting this lower may allow your job to run sooner
#
#SBATCH --mail-type=END,FAIL,TIME_LIMIT_80 # Events to send email on, remove if you don't want this
#SBATCH --output=slurm-%x_%j.out # Standard out from your job
#SBATCH --error=slurm-%x_%j.err  # Standard error from your job

# export label="cuml_rand"
# export base=0.1
# export mult=0.01

# # 0.01 done

# # for base in 0.01 0.02 0.05 0.1
# # do
#     for mult in 1.01 1.02 1.05 1.1
#     do  
#         echo "STARTING $base $mult"

#         function proj_conf_repl() {
#             sed -i "s/#define OFF_TIMER_BASE_PROB .\+/#define OFF_TIMER_BASE_PROB $base/" "$1"
#             sed -i "s/#define OFF_TIMER_MULTIPLIER .\+/#define OFF_TIMER_MULTIPLIER $mult/" "$1"
#             echo "Replacing with $base $mult"
#         }
#         export -f proj_conf_repl

#         find gen -type f -name "*.csc" -printf '%P\n' | grep --color=never "square7/" | ./scripts/run_all_tests.sh 0.1 CUMUL_RAND "$label_$base_$mult"
#         echo "DONE WITH $mult"
#         sleep 5
#     done
# # done

export label="cuml_rand"

export base=0.02
export mult=1.01

echo "STARTING $base $mult"

function proj_conf_repl() {
    sed -i "s/#define OFF_TIMER_BASE_PROB .\+/#define OFF_TIMER_BASE_PROB $base/" "$1"
    sed -i "s/#define OFF_TIMER_MULTIPLIER .\+/#define OFF_TIMER_MULTIPLIER $mult/" "$1"
    echo "Replacing with $base $mult"
}
export -f proj_conf_repl

find gen -type f -name "*.csc" -printf '%P\n' | grep --color=never "square7/" | ./scripts/run_all_tests.sh 0.1 CUMUL_RAND "$label_$base_$mult"
echo "DONE WITH $mult"
sleep 5

export label="cuml_rand"



base=0.05
mult=1.01

echo "STARTING $base $mult"

function proj_conf_repl() {
    sed -i "s/#define OFF_TIMER_BASE_PROB .\+/#define OFF_TIMER_BASE_PROB $base/" "$1"
    sed -i "s/#define OFF_TIMER_MULTIPLIER .\+/#define OFF_TIMER_MULTIPLIER $mult/" "$1"
    echo "Replacing with $base $mult"
}
export -f proj_conf_repl

find gen -type f -name "*.csc" -printf '%P\n' | grep --color=never "square7/" | ./scripts/run_all_tests.sh 0.1 CUMUL_RAND "$label_$base_$mult"
echo "DONE WITH $mult"
sleep 5


base=0.05
mult=1.02

echo "STARTING $base $mult"

function proj_conf_repl() {
    sed -i "s/#define OFF_TIMER_BASE_PROB .\+/#define OFF_TIMER_BASE_PROB $base/" "$1"
    sed -i "s/#define OFF_TIMER_MULTIPLIER .\+/#define OFF_TIMER_MULTIPLIER $mult/" "$1"
    echo "Replacing with $base $mult"
}
export -f proj_conf_repl

find gen -type f -name "*.csc" -printf '%P\n' | grep --color=never "square7/" | ./scripts/run_all_tests.sh 0.1 CUMUL_RAND "$label_$base_$mult"
echo "DONE WITH $mult"
sleep 5