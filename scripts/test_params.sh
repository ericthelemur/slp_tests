
for val in 0.01 0.02 0.05 0.1
do
    echo "STARTING $val"
    if ! [ -z "$val" ] ; then
        sed -i "s/#define OFF_TIMER_PROB .\+/#define OFF_TIMER_PROB $val/" "../contiki-ng/slp-tests/rpl-udp/project-conf.h"
    fi

    find gen -type f -name "*.csc" -printf '%P\n' | grep --color=never square7/ | ./scripts/run_all_tests.sh 0.1 RAND rnd_$val | grep -v "Nashorn"
    echo "DONE WITH $val"
    sleep 5
done
