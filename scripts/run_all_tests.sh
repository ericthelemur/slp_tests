source scripts/setup_tests.sh $1

# Take input from stdin if existing, otherwise find in gen
[ ! -t 0 ] && files=$(cat -) || files=$(find gen -type f -name "*.csc" -printf '%P\n')

# Run tests 4 at a time (change -j#)
echo $files | parallel -j4 -u runtest {} ::: 

# Move results from out to results
mkdir -p results/$1
cp -rl out results/$1
rm -r out
mkdir out

# find gen -type f -name "*.csc" -printf '%P\n' | grep --color=never square | parallel -j8 -u runtest {} :::