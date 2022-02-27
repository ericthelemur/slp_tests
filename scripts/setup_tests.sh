source ./setup_env.sh

if ! [ -z "$1" ] ; then
    sed -i "s/#define SEND_INTERVAL .\+/#define SEND_INTERVAL (unsigned long) (CLOCK_SECOND \/ $1)/" "../contiki-ng/slp-tests/rpl-udp/project-conf.h"
fi

# Run prep to compile mote code (each test does not for efficiency)
java -jar ../cooja/dist/cooja.jar -nogui=prep.csc > /dev/null

function runtest() {
    echo "gen/$1"
    mkdir -p "out/${1%%.*}"
    java -jar ../cooja/dist/cooja.jar -nogui=gen/$1 > "out/${1%%.*}/$(basename $1).log"
}

export -f runtest
