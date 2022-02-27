source scripts/setup_tests.sh $1
echo "Setup complete"

# Run tests 8 at a time (change -j#)
find gen -type f -name "*.csc" -printf '%P\n' | parallel -j4 -u runtest {} ::: 

mkdir -p results/$1
cp -rl out results/$1
rm -r out
mkdir out

# find gen -type f -name "*.csc" -printf '%P\n' | grep --color=never square | parallel -j8 -u runtest {} :::