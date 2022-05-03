# Populates cooja properties
# Run from the parent directory of contiki and slp-tests

mv "contiki-slp" "contiki-ng"
ln -s "contiki-ng/tools/cooja"
ln -s "contiki-ng/slp-tests/rpl-udp" "firm-src"

printf "\nPATH_COOJA=$(pwd)/contiki-ng/tools/cooja/" > ~/.cooja.user.properties
printf "\nPATH_CONTIKI=$(pwd)/contiki-ng" > ~/.cooja.user.properties
printf "\nDEFAULT_PROJECTDIRS=[APPS_DIR]/radiologger-headless;[APPS_DIR]/mrm;[APPS_DIR]/mspsim;[APPS_DIR]/avrora;[APPS_DIR]/serial_socket;[APPS_DIR]/powertracker\n" > ~/.cooja.user.properties
