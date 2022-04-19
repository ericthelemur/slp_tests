# ./scripts/run_all_tests.sh <send freq> <slp: NONE, RAND, CUMUL_RAND, COUNTER, RANDINT_COUNTER> [batch name]

freq=$1
slp_pol=$2
batch_name=$3
# Take input from stdin if existing, otherwise find in gen
[ ! -t 0 ] && files=$(cat -) || files=$(find gen -type f -name "*.csc" -printf '%P\n')

suffix="$batch_name-$slp_pol-$(date +%Y-%m-%d_%H%M)"
gendir="gen-$suffix"
mkdir -p "$gendir"
resdir="results-$suffix/$freq"
mkdir -p "$resdir"

echo "$gendir $resdir"

# Set up project-conf.h
sed -i "s/#define SEND_INTERVAL .\+/#define SEND_INTERVAL (unsigned long) (CLOCK_SECOND \/ $freq)/" "../contiki-ng/slp-tests/rpl-udp/project-conf.h"
sed -i "s/#define RADIO_OFF_SLP .\+/#define RADIO_OFF_SLP RADOFF_SLP_$slp_pol/" "../contiki-ng/slp-tests/rpl-udp/project-conf.h"
cp ../contiki-ng/slp-tests/rpl-udp/project-conf.h $resdir

# Create Test files
function cptest() {
    mkdir -p "$(dirname "$2/$1")"
    cp "gen/$1" "$2/$1"
    cp -u "$(dirname "gen/$1")/testscript.js" "$(dirname "$2/$1")/testscript.js"
    sed -i "s#<pcap_file EXPORT=\"discard\">out#<pcap_file EXPORT=\"discard\">$3#" "$2/$1"
}
export -f cptest
echo "$files" | parallel -j1 cptest {} $gendir $resdir :::

echo "Files created"

# Runs an empty test to compile node code
java -jar ../cooja/dist/cooja.jar -nogui=prep.csc

# Run function
function runtest() {
    echo "RUNNING $2/$1"
    mkdir -p "$3/${1%%.*}"
    java -jar ../cooja/dist/cooja.jar -nogui=$2/$1 > "$3/${1%%.*}/$(basename $1).log"
    echo "FINISHED $2/$1"
}

export -f runtest
echo "Setup complete, running tests"

# Run tests 4 at a time (change -j#)
echo "$files" | parallel --lb -j2 --joblog "$resdir/jobs.log" --memfree 2G --load 200% runtest {} $gendir $resdir ::: 

sleep 3