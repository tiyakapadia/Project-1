# Coverage closure — FIFO · Team 5

> Coverage is a measure of what you *looked at*, never of what is *correct*.
> A closed model with a weak checker reports 100% and proves nothing. This file
> is the argument that your number means something — and the honest list of
> what it still cannot mean.

## 1. The number

| | |
|---|---|
| Coverpoints closed | 11/11 (100%) |
| Cross closed | 6 / 6 bins (100%) (`Occupancy x Read/Write`, `Empty x Read`, `Full x Write`, `Occupancy x Simultaneous R/W`, `Almost-full x Write`, `Occupancy change x Read/Write`) | |
| Target declared in my vplan | 100% |
| Reached | 100% |
| Vectors to closure | ~2,500 cycles (at Seed 4) |
| Vectors soaked past closure | 500 cycles (up to 3,000 cycles per seed)|

**How the report was produced:**

```bash
source ~/.venv/bin/activate
cd /code
SEED=4 N_CYCLES=3000 BURSTS=1 RESETS=1 make -C tb/project1 MODULE=test_crv SIM=icarus WIDTH=8 DEPTH=8
# coverage_db.report_coverage(...) — also exports coverage.yml
```

## 2. The convergence argument


**Shape of the curve:** Coverage quickly jumps to ~74% within the first 300 cycles as basic single-signal bins and mid-range occupancies are hit by standard random traffic. Around cycles 600 to 1,000, the curve flattens at 85% to 90% while waiting on harder multi-cycle bursts, Full x Write boundaries, and specific occupancy-plus-input reset triggers. Once those targeted sequences complete around cycle 2,500, coverage reaches 100% and remains flat through the end of the 3,000-cycle run.

**The last bins to close, and what it took:**

| Bin | Why it was rare | What I changed to hit it |
|-----|-----------------|--------------------------|
|Full × Write request (wr_while_full)|Balanced random read/write probabilities hover near mid-range occupancy and rarely push count to 8 and keep writing.|Added a FILL phase (P(wr)=0.84, P(rd)=0.09) with a dwell at full (337 hits in Seed 4; 340 in Seed 0xC0FFEE).|
|Empty × Read request (rd_while_empty)|Once entries enter the FIFO, uniform random traffic rarely drains occupancy back to 0 and continues issuing reads.|Added a DRAIN phase (P(wr)=0.08, P(rd)=0.84) with a dwell at empty (268 hits in Seed 4; 249 in Seed 0xC0FFEE).|
|Burst behavior (WR_ONLY / RD_ONLY >= 8 cycles)|Back-to-back runs of 8+ consecutive writes or reads have negligible probability under independent per-cycle rolls.|Added dedicated WR_ONLY (P(wr)=1.0) and RD_ONLY (P(rd)=1.0) burst phases, reaching runs of 18 writes and 17 reads.|
|Reset with active/idle control (e.g., (7,0,0) and (8,1,1))|Hitting an exact occupancy (7 or 8) simultaneously with a specific (wr_en, rd_en) combination on a reset edge rarely happens by chance.|Added targeted reset triggers tied to (occupancy, wr_en, rd_en) states, including an idle reset (7, 0, 0) at occupancy 7.

**Why I stopped where I stopped:**

Stopping right at cycle 2,500 when the last bin ticks would leave no time for late-propagating bugs to reach rd_data or the status flags. Soaking for 500 extra cycles up to 3,000 cycles per seed ensures that entries written at boundary states get drained and checked by the scoreboard.

## 3. Bin justification

Every `illegal` and `ignore` bin is a claim about the design. Each one needs an
authority — a line of `dut/specs/fifo.md`, or an argument you would defend.

| Bin | illegal / ignore | The claim | Authority (spec line, or the argument) |
|-----|------------------|-----------|----------------------------------------|
| Transactions defined as illegal by the FIFO specificatio |illegal |Normal constrained-random stimulus should only generate legal FIFO transactions.|FIFO specification limits capacity to DEPTH = 8 (0 <= count <= 8) and defines full (count == 8) and empty (count == 0) as mutually exclusive.|
|Unreachable combinations caused by the FIFO protocol|Ignore|These combinations cannot occur during legal operation and should not be included in the functional coverage target.|Protocol rules tie flag assertions and occupancy transitions directly to count, making contradictory flag/count pairs unreachable in legal operation.|
|Reset with an active control request|Illegal/undefined observation|Included separately to satisfy the illegal or undefined control requirement.|Spec leaves reset with active wr_en/rd_en as a special boundary case, so it is tracked separately (resets_done=5) and checked via assertions that state returns to (0, 1, 0).  

**Corner bins that are legal and must be covered, not excluded:**

Write-while-full (wr_while_full) and read-while-empty (rd_while_empty) are both legal behaviors in the spec, not illegal states. Write-while-full must drop the incoming write without overwriting stored data, and read-while-empty must ignore the read without underflowing pointers. Both bins were kept in the coverage target and hit 337 times and 268 times in Seed 0x4.

## 4. What the cross is aimed at

A cross earns its place only if the interaction is where a bug would hide.

**The bug `top.occ_x_op` is aimed at:**  It catches boundary overflow and underflow bugs, like writing when the FIFO is already full or reading when it's empty, so pointers don't wrap around or overwrite data. It also checks for off-by-one flag and count bugs when doing simultaneous reads and writes at corner levels like 0, 1, 7, and 8.

**A bug it would *not* see, even fully closed:** Even at 100%, it won't catch corrupted data inside the memory array (like stuck bits or stale rd_data) because it only tracks control signals and occupancy, not the actual data values. It also misses multi-cycle bugs that only show up after

## 5. Coverage vs. correctness — the blind spots


My model is closed and my suite is green. That still establishes nothing about:

1. **Data payload integrity across individual bits**   The coverage model tracks control signals, bursts (writes=18, reads=17, alternating=18), and occupancy counts, not every bit of wr_data and rd_data. A stuck-at fault on a middle data bit would still close every coverage bin and can only be caught by scoreboard data comparison.

2. **Exact reset release timing and back-to-back resets** Our reset bins check that rst_n asserts at specific (occupancy, wr_en, rd_en) points, but they do not require testing single-cycle versus multi-cycle reset pulses or writes arriving on the exact clock edge where rst_n deasserts.

3. **Long-term circular pointer wrap-around**  A pointer bug that only triggers after many full wrap-arounds of the 8-entry buffer would not be separated by occupancy bins that only track 0..8.

**Transients in particular:** Because our monitor and coverage model sample signals once per rising clock edge, a one-cycle glitch on full, empty, almost_full, or rd_data between clock edges would not be seen. Catching intra-cycle glitches would require asynchronous assertions or sub-cycle oversampling.

## 6. Correlation with mutation

Cross-reference `FINDINGS.md`. The interesting case is divergence.

| | found / total |
|---|---|
| Before closing holes |8/8, 3/6 (custom mutants) |
| After closing holes | 8/8 (customt mutants)|

**Did closing holes raise the score?**

- **Yes** on our custom mutant suite (from 3/6 to 5/6). Adding an idle reset at occupancy 7 (wr_en=0, rd_en=0) caught reset_ignored_at_cnt7 (4/6), and weighting wr_data to emit 0x00 and 0xFF at 6% each caught data_ff_at_cnt7 (5/6).

---

- [X] Every `illegal` and `ignore` bin in section 3 cites an authority.
- [X] Section 5 names blind spots of this design, not of coverage in general.
- [X] The numbers here agree with `coverage.yml` and `FINDINGS.md`.
