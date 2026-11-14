# Check the Machine — CtM-NN


**Name: Tiya Kapadia**
**Section:** EEE 4701
**Week:** Project 1 
**Autonomy tier:** self-directed
**Assistant used:** <web interface, <10 2026>">
---

## 1. Task

 Build the layered cocotb verification environment (driver.py, monitor.py) and constrained-random stimulus generator (test_crv.py) for the 8-bit × 8-deep synchronous FIFO, including phase-based fill/drain shaping, burst runs, biased data corners, and targeted resets across occupancy and control states.

**Prompt (verbatim):**

```text
Given the synchronous FIFO specification and the project verification plan, help structure the cocotb driver and monitor interfaces and design constrained-random stimulus phases (fill, drain, burst, and targeted resets) that reach all occupancy levels and boundary corners.
```

---

## 2. Before

**Prediction 1 —** Uniform random stimulus will hover in mid-range occupancy and fail to reach full or empty long enough to hit wr_while_full and rd_while_empty corners.

*Evidence that would show it:* Simulation summary logs showing zero or near-zero hits for wr_while_full, rd_while_empty, or occupancy 8, leaving boundary mutants unreached.

**Prediction 2 —** Holding wr_en=1 during a reset at occupancy 7 will mask reset bugs that only fail on the first clock edge, and uniform random wr_data will miss specific corner-value faults at exact occupancy levels.

*Evidence that would show it:* Mutation testing surviving mutants like reset_ignored_at_cnt7 or data_ff_at_cnt7 (scoring 3/6 on our self-made extra mutant pool).

**Review criteria I am checking against:**

1. Driver and monitor sample and drive signals on the proper synchronous clock edges (RisingEdge(dut.clk)) without race conditions.

2. Stimulus visits every FIFO occupancy level from 0 through 8 across a 3,000-cycle run.

3. Stimulus exercises boundary and burst corners (wr_while_full, rd_while_empty, simultaneous mid-range read/write, and consecutive write/read bursts >= 8 cycles).

4. Stimulus triggers targeted resets across distinct (occupancy, wr_en, rd_en) combinations, including an idle reset (7, 0, 0) at occupancy 7.

5. Weighted data generation biases 0x00 and 0xFF corners (6% each) alongside uniform random bytes (88%) to catch data-dependent faults.

6. Regression runs are strictly reproducible from a fixed SEED and pass all scoreboard and mutation checks (8/8 on the released pool)

---

## 3. After

**Raw output:**

```text
https://github.com/tiyakapadia/Project-1//main/FINDINGS.md
(and tb/project1/driver.py, tb/project1/monitor.py, tb/project1/test_crv.py)
```

**The number:** <8/8, 100%>

**Against each prediction:**

| # | Predicted | Observed | Verdict |
|---|-----------|----------|---------|
| 1 | Uniform random stimulus would fail to reach full and empty boundaries or trigger wr_while_full and rd_while_empty.|Adding driver-owned FILL (P(wr)=0.84) and DRAIN (P(rd)=0.84) phases with boundary dwells visited every occupancy 0–8 and hit wr_while_full=337 and rd_while_empty=268 in Seed 4 (340 and 249 in Seed 0xC0FFEE).  | confirmed (and resolved by phase shaping) |
| 2 | Initial extra-pool score was 3/6; adding an idle reset (7, 0, 0) caught reset_ignored_at_cnt7 (4/6) and weighting 0xFF/0x00 at 6% each caught data_ff_at_cnt7 (5/6) | confirmed |

---

## 4. Takeaway

**The class of failure (or of success): Stimulus reachability vs. observability separation. Reaching an occupancy state (such as occupancy 7) is not enough if concurrent control signals (wr_en=1) or low data-corner probability (1/256 for 0xFF) mask the fault before the scoreboard observes it.**

**Where it connects: : Connects directly to constrained-random verification, state-space reachability, and mutation-driven testbench refinement—using self-made extra mutants to expose subtle stimulus blind spots that a small released mutant pool does not test.**

**What I would change in how I framed the request: Provide the exact DUT port list, reset polarity (rst_n), and target (occupancy, wr_en, rd_en) reset tuples upfront so the initial stimulus generator includes idle-control resets and corner-weighted data distributions on the first pass.**

---

## Disclosure

- [X] Every prompt above is verbatim and complete.
- [X] I have marked every edit I made to the generated output.
- [X] The tool is described by class, not by product name.
- [X] Section 2 was written before the prompt was sent.
