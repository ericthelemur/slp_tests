export val=0.0

function proj_conf_repl() { :; }
export -f proj_conf_repl

for val in 0.1 0.2 0.5 1 2 0.05 0.02
# for val in 1 2 3 4 5
do

    sbatch ./test-batches/test_batch_none_inner.sh &
    # sbatch ./test-batches/test.sh &
    sleep 5
done