set -u
cd "$(dirname "$0")" || exit 2

N_CYCLES="${N_CYCLES:-3000}"
SIM="${SIM:-icarus}"
MODULE="${MODULE:-test_crv}"
REPRO="${REPRO:-1}"
BURSTS="${BURSTS:-1}"
RESETS="${RESETS:-1}"
read -r -a CONFIG_LIST <<< "${CONFIGS:-8x8}"
LOGDIR="regress_logs"

if [ "$#" -gt 0 ]; then SEEDS=("$@"); else SEEDS=(0xC0FFEE 1 2 3 4 5 6 7 8); fi

mkdir -p "$LOGDIR"
SUMMARY="$LOGDIR/summary.txt"
COMMIT="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"

make clean >/dev/null 2>&1 || true

run_one() {
    local config="$1" seed="$2" log="$3"
    local width="${config%x*}" depth="${config#*x}"
    local cmd="SEED=$seed N_CYCLES=$N_CYCLES BURSTS=$BURSTS RESETS=$RESETS make MODULE=$MODULE SIM=$SIM WIDTH=$width DEPTH=$depth"
    {
        echo "# date:   $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        echo "# commit: $COMMIT"
        echo "# config: WIDTH=$width DEPTH=$depth"
        echo "# seed:   $seed"
        echo "# cmd:    $cmd"
        echo "# ----"
    } > "$log"
    SEED="$seed" N_CYCLES="$N_CYCLES" BURSTS="$BURSTS" RESETS="$RESETS" timeout 600 \
        make MODULE="$MODULE" SIM="$SIM" WIDTH="$width" DEPTH="$depth" >> "$log" 2>&1
    grep -q "PASS=[1-9]" "$log" && grep -q "FAIL=0" "$log"
}

stimulus_lines() {
    grep -h -E "occupancy|wr_while_full|longest_run|resets_done" "$1" \
        | sed -E 's/^.*(occupancy|wr_while_full|longest_run|resets_done)/\1/'
}

failed=0
{
    echo "regression: module=$MODULE sim=$SIM N_CYCLES=$N_CYCLES bursts=$BURSTS resets=$RESETS commit=$COMMIT"
    printf '%-7s %-10s %-6s %s\n' "config" "seed" "result" "stimulus"
} | tee "$SUMMARY"

for config in "${CONFIG_LIST[@]}"; do
    for seed in "${SEEDS[@]}"; do
        log="$LOGDIR/${config}_seed_${seed}.log"
        if run_one "$config" "$seed" "$log"; then result=PASS; else result=FAIL; failed=$((failed + 1)); fi
        stim="$(stimulus_lines "$log" | tr '\n' ' ')"
        printf '%-7s %-10s %-6s %s\n' "$config" "$seed" "$result" "$stim" | tee -a "$SUMMARY"
    done
done

if [ "$REPRO" = "1" ] && [ "${#SEEDS[@]}" -gt 0 ]; then
    config="${CONFIG_LIST[0]}"
    first="${SEEDS[0]}"
    rerun="$LOGDIR/${config}_seed_${first}_rerun.log"
    run_one "$config" "$first" "$rerun" >/dev/null
    if [ "$(stimulus_lines "$LOGDIR/${config}_seed_${first}.log")" = "$(stimulus_lines "$rerun")" ] \
        && [ -n "$(stimulus_lines "$rerun")" ]; then
        echo "reproducibility: $config seed $first rerun gave identical stimulus lines" | tee -a "$SUMMARY"
    else
        echo "reproducibility: $config seed $first rerun DIFFERED (or printed no stimulus lines)" | tee -a "$SUMMARY"
        failed=$((failed + 1))
    fi
fi

echo "failures: $failed" | tee -a "$SUMMARY"
[ "$failed" -eq 0 ]
