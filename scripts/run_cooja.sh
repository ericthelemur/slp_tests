source scripts/setup_env.sh
cd ../contiki-ng/tools/cooja
ant jar
java -jar dist/cooja.jar -Xmx2g
