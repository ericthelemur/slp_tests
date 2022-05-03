#!/bin/bash
#
#SBATCH --job-name=no-slp  # Job name for tracking
#SBATCH --partition=desktop-batch  # Partition you wish to use (see above for list)
#SBATCH --cpus-per-task=6      # Number of CPU cores used by your job
#SBATCH --mem-per-cpu=5000     # RAM in MB needed per core (i.e. 3000MB * 1 cores = 3GB RAM)
#SBATCH --time=2-00:00:00      # Job time limit set to 2 days (48 hours), setting this lower may allow your job to run sooner
#
#SBATCH --mail-type=END,FAIL,TIME_LIMIT_80 # Events to send email on, remove if you don't want this
#SBATCH --output=slurm-%x_%j.out # Standard out from your job
#SBATCH --error=slurm-%x_%j.err  # Standard error from your job

export this_val=$val
echo "STARTING $this_val"
# find gen -type f -name "*.csc" -printf '%P\n' | ./scripts/run_all_tests.sh $this_val NONE "$label_$this_val"
find gen -type f -name "*.csc" -printf '%P\n' | grep -v square[1234]/ | ./scripts/run_all_tests.sh $this_val NONE "$label_$this_val"
echo "DONE WITH $this_val"