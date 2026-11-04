# CRAFT V&V -- student runnable code. Run testbenches and score with mutation.
# `just` is optional: every recipe is a one-line command you can run by hand.
# First set up your tools (see ../INSTALL.md), then from the packet root:
#     nix-shell                              # Nix users (this folder is not a git repo)
#     source .venv/bin/activate              # venv users
#     source /opt/course/cocotb-env/bin/activate   # eustis
#
#   just test alu                 # run a testbench (Verilator)
#   just test alu icarus          # ...with Icarus
#   just mutate alu               # found/total on YOUR suite vs the RELEASED pool
#   just cover fifo_cov           # run a coverage testbench (emits a report)
#   just waves alu                # write a waveform + print the file to open
#   just demo 03 s2               # replay a class demo (see its DEMO.md)
#   just formal fifo              # SymbiYosys proof
#   just clean-tmp                # show what is in ~/.vvtemp, then clear it

export PYTHONPATH := justfile_directory() / "lib"

_default:
    @just --list

# run a testbench:  just test <name> [verilator|icarus]
test name sim="verilator":
    make -C tb/{{name}} SIM={{sim}}

# score YOUR suite vs the RELEASED practice pool:  just mutate <name> [sim]
mutate name sim="icarus":
    python -m craft_mutate.mutate --tb tb/{{name}} --pool tb/{{name}}/mutants_released.yaml --sim {{sim}}

# run a coverage testbench (it writes its own report):  just cover <name>
cover name sim="verilator":
    make -C tb/{{name}} SIM={{sim}}

# write a waveform and name the file to open:  just waves <name> [icarus|verilator]
#   Icarus honours WAVES=1 and writes sim_build/<top>.fst.
#   Verilator IGNORES WAVES=1 -- it wants VERILATOR_TRACE=1, and writes dump.vcd.
#   Getting a green run and silently no waveform is the classic Week-1 time-sink;
#   this recipe picks the right flag, and clears a stale sim_build first.
waves name sim="icarus":
    #!/usr/bin/env bash
    set -euo pipefail
    d=tb/{{name}}
    [ -d "$d" ] || { echo "no testbench directory $d"; exit 1; }
    rm -rf "$d/sim_build" "$d/dump.vcd"   # a stale sim_build re-runs the OLD rtl
    if [ "{{sim}}" = verilator ]; then
        make -C "$d" SIM=verilator VERILATOR_TRACE=1
    else
        make -C "$d" SIM=icarus WAVES=1
    fi
    w=$(find "$d" \( -name '*.fst' -o -name '*.vcd' \) | head -1)
    [ -n "$w" ] || { echo "no waveform written -- see the log above"; exit 1; }
    echo
    echo "waveform: $w"
    echo "open it:  gtkwave $w"

# replay a live demo from class:  just demo 03 s2      (lists the steps)
#                                  just demo 03 s2 0    (runs step 0)
# Each demo directory has a DEMO.md written for you, with the commands, the
# output you should get, and what it means.
demo week session step="":
    #!/usr/bin/env bash
    set -euo pipefail
    d=$(ls -d demos/wk{{week}}-{{session}}-*/ 2>/dev/null | head -1)
    [ -n "$d" ] || { echo "no demo for week {{week}} session {{session}}"; exit 1; }
    if [ -z "{{step}}" ]; then
        awk '/^\| Step/{f=1} f{if(NF==0) exit; print}' "$d/DEMO.md"
        echo "run one with:  just demo {{week}} {{session}} <step>"
    else
        make -C "$d" STEP={{step}}
    fi

# SymbiYosys formal proof:  just formal <name>
formal name:
    cd formal/{{name}} && sby -f {{name}}.sby

# show what is in your scratch dir (~/.vvtemp), then offer to delete it
clean-tmp *args:
    bash setup/clean_tmp.sh {{args}}

# remove sim build dirs and stray results
clean:
    -find tb -name sim_build -type d -exec rm -rf {} + 2>/dev/null
    -find demos -name '*.gen.sby' -delete 2>/dev/null
    -find . -name results.xml -delete 2>/dev/null
