
# freq=$1
# slp_pol=$2
# batch_name=$3

# ----------- SETUP ---------------

# Create directories
echo "b $freq $slp_pol $batch_name"
export prefix="$(date +%Y-%m-%d_%H%M%S)-$batch_name-$slp_pol"
testdir="$parent/$prefix/tests"
mkdir -p "$testdir"
resdir="$parent/$prefix/results/$freq"
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
}

export -f cptest
echo "$files" | parallel -j1 cptest {} $testdir $resdir $firmdir :::

# Set up firmware
cp ../firm-src/Makefile ../firm-src/project-conf.h ../firm-src/udp-client.c ../firm-src/udp-middle.c ../firm-src/udp-server.c $firmdir

sed -i "s/#define SEND_INTERVAL .\+/#define SEND_INTERVAL (unsigned long) (CLOCK_SECOND \/ $freq)/" "$firmdir/project-conf.h"
sed -i "s/#define RADIO_OFF_SLP .\+/#define RADIO_OFF_SLP RADOFF_SLP_$slp_pol/" "$firmdir/project-conf.h"

# If substitution defined outside, run once copied(here)
proj_conf_repl "$firmdir/project-conf.h";

sed -i "s#CONTIKI=../..#CONTIKI=../../../../../contiki-ng#" "$firmdir/Makefile"

echo "Files created"

(cd $firmdir; make TARGET=z1 || exit 420;  echo done) || exit 420

echo "Built"