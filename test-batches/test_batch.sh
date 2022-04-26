#!/bin/bash
#
#SBATCH --job-name=slp-none-0.1  # Job name for tracking
#SBATCH --partition=desktop-batch  # Partition you wish to use (see above for list)
#SBATCH --cpus-per-task=6      # Number of CPU cores used by your job
#SBATCH --mem-per-cpu=5000     # RAM in MB needed per core (i.e. 3000MB * 1 cores = 3GB RAM)
#SBATCH --time=1-00:00:00      # Job time limit set to 2 days (48 hours), setting this lower may allow your job to run sooner
#
#SBATCH --mail-type=END,FAIL,TIME_LIMIT_80 # Events to send email on, remove if you don't want this
#SBATCH --output=joboutput_%j.out # Standard out from your job
#SBATCH --error=joboutput_%j.err  # Standard error from your job

cd ..
find gen -type f -name "*.csc" -printf '%P\n' | srun ./scripts/run_all_tests.sh 0.1 NONE none-test-run