#!/bin/bash
# ./scripts/run_all_tests.sh [--resume | -r] [--temp | -t] <send freq> <slp: NONE, RAND, CUMUL_RAND, COUNTER, RANDINT_COUNTER> [batch name]
# or ./scripts/run_all_tests.sh --resume <suffix> <frequency>

# If resume, skip setup
resume=""
case "$1" in 
    -r|--resume) 
        shift
        resume=" --resume"
        testdir="tests-$1"
        resdir="results-$1/$2"
    ;;
esac

# Set parent directory
# If ran with --temp, will place in temp/ instead of running/
echo $1
export parent="running/"
if [ "$1" = "-t" ] || [ "$1" = "--temp" ]; then
    parent="temp/"
    shift
fi

# Take input from stdin if existing, otherwise find in gen
[ ! -t 0 ] && files=$(cat -) || files=$(find gen -type f -name "*.csc" -printf '%P\n' sort)
echo files $files

# Run setup if not resuming
if [ -z "$resume" ] ; then
    source ./scripts/run_all_setup.sh || exit 420
fi

# ----------- RUNNING ---------------

function runtest() {
    echo "RUNNING $2/$1"
    mkdir -p "$3/${1%%.*}"
    java -jar ../cooja/dist/cooja.jar -nogui=$2/$1 > "$3/${1%%.*}/$(basename $1).log"
    echo "FINISHED $2/$1"
}

export -f runtest
echo "Setup complete, running tests"

# Run tests 4 at a time (change -j#)
# --load 500% -j6
echo "$files" | parallel --lb --joblog "$resdir/jobs.log"$resume --memfree 2G --delay 30 runtest {} $testdir $resdir ::: 

sleep 3

# Move to completed if not temp
[ parent != "temp/" ] && mv "running/$prefix" "completed/$prefix"