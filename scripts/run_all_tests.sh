source scripts/setup_tests.sh $1 $2

sleep 3
# Take input from stdin if existing, otherwise find in gen
[ ! -t 0 ] && files=$(cat -) || files=$(find gen -type f -name "*.csc" -printf '%P\n')

cp ../contiki-ng/slp-tests/rpl-udp/project-conf.h out

# Run tests 4 at a time (change -j#)
printf "%s\n" $files | parallel --lb -j9 --joblog jobs.log --memfree 2G --load 500% runtest {} ::: 

sleep 3

# Move results from out to results
date=$(date +%Y-%m-%d_%H%M)
loc="results-$3-$2-$date/$1"
mkdir -p $loc
# cp -rl out/* $loc
mv out/* $loc
# rm -r out
# mkdir out

# find gen -type f -name "*.csc" -printf '%P\n' | grep --color=never square | parallel -j12 -u runtest {} :::
