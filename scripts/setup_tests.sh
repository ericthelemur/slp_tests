source scripts/setup_env.sh

if ! [ -z "$1" ] ; then
    sed -i "s/#define SEND_INTERVAL .\+/#define SEND_INTERVAL (unsigned long) (CLOCK_SECOND \/ $1)/" "../contiki-ng/slp-tests/rpl-udp/project-conf.h"
fi

if ! [ -z "$2" ] ; then
    sed -i "s/#define RADIO_OFF_SLP .\+/#define RADIO_OFF_SLP RADOFF_SLP_$2/" "../contiki-ng/slp-tests/rpl-udp/project-conf.h"
fi

# Run prep to compile mote code (each test does not for efficiency)
java -jar ../cooja/dist/cooja.jar -nogui=prep.csc

function runtest() {
    echo "RUNNING gen/$1"

    mkdir -p "out/${1%%.*}"
    java -jar ../cooja/dist/cooja.jar -nogui=gen/$1 > "out/${1%%.*}/$(basename $1).log"

    # mv COOJA.log "out/${1%%.*}"
    # mv COOJA.testlog "out/${1%%.*}"
    echo "FINISHED gen/$1"
}

export -f runtest
echo "Setup complete"