# ./scripts/run_all_tests.sh <send freq> <slp: NONE, RAND, CUMUL_RAND, COUNTER, RANDINT_COUNTER> [batch name]

freq=$1
slp_pol=$2
batch_name=$3
# Take input from stdin if existing, otherwise find in gen
[ ! -t 0 ] && files=$(cat -) || files=$(find gen -type f -name "*.csc" -printf '%P\n')

# ----------- SETUP ---------------
suffix="$batch_name-$slp_pol-$(date +%Y-%m-%d_%H%M)"
testdir="tests-$suffix"
mkdir -p "$testdir"
resdir="results-$suffix/$freq"
mkdir -p "$resdir"
firmdir="$testdir/firmware"
mkdir -p $firmdir

echo "$testdir $resdir $firmdir"

# Create Test files
function cptest() {
    dirn="$(dirname "$2/$1")"
    mkdir -p $dirn
    cp "gen/$1" "$2/$1"
    cp -u "$(dirname "gen/$1")/testscript.js" "$dirn/testscript.js"
    sed -i "s#<pcap_file EXPORT=\"discard\">out#<pcap_file EXPORT=\"discard\">$3#" "$2/$1"
    sed -i "s#\[CONTIKI_DIR\]/slp-tests/rpl-udp.udp-#[CONFIG_DIR]/../firmware/udp-#" "$2/$1"
    # Also update for prep.csc
}

export -f cptest
echo "$files" | parallel -j1 cptest {} $testdir $resdir $firmdir :::

# cp prep.csc $testdir
# sed -i "s#\[CONTIKI_DIR\]/slp-tests/rpl-udp.udp-#[CONFIG_DIR]/../firmware/udp-#" "$testdir/prep.csc"


# Set up firmware
cp ../firm-src/Makefile ../firm-src/project-conf.h ../firm-src/udp-client.c ../firm-src/udp-middle.c ../firm-src/udp-server.c $firmdir

sed -i "s/#define SEND_INTERVAL .\+/#define SEND_INTERVAL (unsigned long) (CLOCK_SECOND \/ $freq)/" "$firmdir/project-conf.h"
sed -i "s/#define RADIO_OFF_SLP .\+/#define RADIO_OFF_SLP RADOFF_SLP_$slp_pol/" "$firmdir/project-conf.h"

sed -i "s#CONTIKI=../..#CONTIKI=../../../contiki-ng#" "$firmdir/Makefile"

echo "Files created"

(cd $firmdir; make TARGET=z1; echo done)

echo "Built"
# exit 1


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
echo "$files" | parallel --lb -j2 --joblog "$resdir/jobs.log" --memfree 2G --load 200% runtest {} $testdir $resdir ::: 

sleep 3