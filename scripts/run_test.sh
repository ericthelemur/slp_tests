source scripts/setup_env.sh

mkdir -p out/$1
java -jar ../cooja/dist/cooja.jar -nogui=gen/$1.csc