# Coverage closure — fifo · Tiya Kapadia

> Coverage is a measure of what you *looked at*, never of what is *correct*.
> A closed model with a weak checker reports 100% and proves nothing. This file
> is the argument that your number means something — and the honest list of
> what it still cannot mean.

## 1. The number

| Metric | Value | 
| ----- | ----- | 
| Coverpoints closed | 11 / 11 (100%) | 
| Cross `top.occ_x_op` closed | 16 / 16 bins (100%) *(plus 5 additional crosses closed)* | 
| Target declared in my vplan | 100% | 
| Reached | 100% | 
| Vectors to closure | \~2,500 cycles (at Seed `0xC0FFEE` / Seed 4) | 
| Vectors soaked past closure | \~500 cycles (total run = 3,000 cycles) | 

**How the report was produced:**

```
source ~/.venv/bin/activate
cd ~/VnV/code
SEED=4 N_CYCLES=3000 BURSTS=1 RESETS=1 make -C tb/project1 MODULE=test_crv SIM=icarus WIDTH=8 DEPTH=8
# coverage_db.report_coverage(...) — also exports coverage.yml

```

## 2. The convergence argument

**Shape of the curve:** Coverage climbs rapidly to \~74% within the first 300 cycles as basic single-signal coverpoints (read/write enables, status flags, and mid-range occupancies) are hit immediately. Between cycles 600 and 1,000, the curve flattens around 85–90% because the remaining bins require multi-cycle fills/drains or exact state-plus-input combinations, before closing at 100% around cycle 2,500.

**The last bins to close, and what it took:**

| Bin | Why it was rare | What I changed to hit it | 
| ----- | ----- | ----- | 
| `Full × Write request` (`wr_while_full`) | Balanced random read/write probabilities hover near mid-range occupancy and rarely push `count` to 8 and keep writing. | Added a driver-owned `FILL` phase (`P(wr)=0.84, P(rd)=0.09`) with a dwell at full (337 hits in Seed 4; 340 in Seed `0xC0FFEE`). | 
| `Empty × Read request` (`rd_while_empty`) | Once entries enter the FIFO, uniform random traffic rarely drains occupancy back to 0 and continues issuing reads. | Added a `DRAIN` phase (`P(wr)=0.08, P(rd)=0.84`) with a dwell at empty (268 hits in Seed 4; 249 in Seed `0xC0FFEE`). | 
| `Burst behavior` (`WR_ONLY` / `RD_ONLY` >= 8 cycles) | Back-to-back runs of 8+ consecutive writes or reads have negligible probability under independent per-cycle rolls. | Added dedicated `WR_ONLY` (`P(wr)=1.0`) and `RD_ONLY` (`P(rd)=1.0`) burst phases, reaching runs of 18 writes and 17 reads. | 
| `Reset with active/idle control` (e.g., `(7,0,0)` and `(8,1,1)`) | Hitting an exact occupancy (`7` or `8`) simultaneously with a specific `(wr_en, rd_en)` combination on a reset edge rarely happens by chance. | Added targeted reset triggers tied to `(occupancy, wr_en, rd_en)` states, including an idle reset `(7, 0, 0)` at occupancy 7. | 

**Why I stopped where I stopped:**
We ran 3,000 cycles—soaking roughly 500 cycles past the \~2,500-cycle closure mark—because ticking a bin only proves the input state occurred, not that any resulting pointer or memory corruption propagated to `rd_data` or the status flags. Soaking past closure forces subsequent fills, drains, and simultaneous read/write operations to read back stored entries and expose latent count or pointer drift.

## 3. Bin justification

| Bin | illegal / ignore | The claim | Authority (spec line, or the argument) | 
| ----- | ----- | ----- | ----- | 
| `Transactions defined as illegal by the FIFO specification` | `illegal` | Normal constrained-random stimulus must not drive protocol-violating transactions outside the specification's defined interface. | `dut/specs/fifo.md` (synchronous single-clock control protocol; normal stimulus is constrained to valid control combinations). | 
| `Unreachable combinations caused by the FIFO protocol` (e.g., `full == 1 && empty == 1`) | `ignore` | A FIFO with `DEPTH=8` cannot be simultaneously empty (`count == 0`) and full (`count == 8`). | `dut/specs/fifo.md` (flag definitions: `empty` asserts iff `count == 0` and `full` asserts iff `count == DEPTH`, making simultaneous assertion structurally impossible). | 
| `Reset with an active control request` (`rst_n == 0` with `wr_en == 1` and/or `rd_en == 1`) | `illegal` / undefined observation | Synchronous reset overrides active read/write requests and clears the FIFO to `(count=0, empty=1, full=0)`. | `dut/specs/fifo.md` (active-low synchronous reset behavior) & project security/illegal-control requirement. | 

**Corner bins that are legal and must be covered, not excluded:**
Write-while-full (`full == 1 && wr_en == 1`, where the write is dropped without overflow) and read-while-empty (`empty == 1 && rd_en == 1`, where the read is ignored without underflow) are both legal operating conditions permitted by `dut/specs/fifo.md`. Both `(full, write)` and `(empty, read)` are explicitly included as active cross bins (`Full × Write request` and `Empty × Read request`) rather than `ignore` bins, and were hit 337 and 268 times respectively in Seed 4.

## 4. What the cross is aimed at

**The bug `top.occ_x_op` is aimed at:**
`top.occ_x_op` (`Occupancy × Read/Write combination`) targets off-by-one pointer wrap-around, premature/late `full` or `empty` flag transitions, and count update errors that only occur when a specific operation (idle, read-only, write-only, or simultaneous read/write) happens at a specific occupancy boundary (such as simultaneous read/write when `count == 0`, `count == 7`, or `count == 8`).

**A bug it would *not* see, even fully closed:**
Because `top.occ_x_op` only tracks occupancy buckets and control enables (`wr_en`, `rd_en`), it is completely blind to **data-path corruption**—such as a specific bit stuck-at fault in the memory array, a write that corrupts `mem[wr_ptr]` only when `wr_data == 0xFF` at occupancy 7 (`data_ff_at_cnt7`), or byte-ordering/pointer-aliasing bugs when identical data values are written consecutively.

## 5. Coverage vs. correctness — the blind spots

1. **Non-corner `wr_data` payloads at specific occupancies** — The coverage model does not cross `wr_data` bit patterns with occupancy levels, and only 12% of our stimulus is biased (`0x00` and `0xFF` at 6% each). A fault triggered only when a specific non-corner byte (e.g., `0xA5`) is written at a single occupancy level has only a \~1 in 256 chance per write of being reached.

2. **Parameter configurations other than `WIDTH=8, DEPTH=8`** — All closure numbers and runs were executed exclusively at `WIDTH=8, DEPTH=8`. Address wrap-around or counter bit-width bugs that only appear on non-power-of-two depths or wider data buses are completely unverified.

3. **Variable reset pulse widths** — Every reset in our driver is held for exactly two clock edges. A synchronous or asynchronous reset defect that only manifests on a single-cycle reset pulse or a prolonged multi-cycle reset is never exercised.

4. **Undefined `rd_data` behavior when empty** — Because `dut/specs/fifo.md` leaves `rd_data` undefined when `empty == 1`, our scoreboard intentionally skips checking `rd_data` on empty cycles. Any unintended data leakage onto `rd_data` while the FIFO is empty (`rd_data_when_empty`) will not fail the suite.

**Transients in particular:**
No—our model and scoreboard sample signals once per clock cycle (in `ReadOnly()` right after `RisingEdge(dut.clk)`), so a combinational glitch on `full`, `empty`, or `rd_data` that occurs mid-cycle and settles before the next active clock edge ticks no bin and triggers no scoreboard error. Catching intra-cycle transients would require continuous/asynchronous SVA checks or oversampled step-delay assertions inside `fifo.sv` rather than end-of-cycle Python sampling.

## 6. Correlation with mutation

| Stage | found / total | 
| ----- | ----- | 
| Before closing holes | 8 / 8 (released pool) · 3 / 6 (self-made extra pool) | 
| After closing holes | 8 / 8 (released pool) · 5 / 6 (self-made extra pool) | 

**Did closing holes raise the score?**

* **Released pool (`8/8` before and after):** No change—the released pool was already at 100% before our final stimulus refinements.

* **Self-made extra pool (`3/6` -> `5/6`):** **Yes**, closing specific stimulus/coverage holes caught two previously surviving mutants:

  * Adding an idle reset `(occupancy=7, wr_en=0, rd_en=0)` closed the idle-reset hole at occupancy 7 and caught **`reset_ignored_at_cnt7`** (raising the score from `3/6` to `4/6`). Previously, `wr_en=1` was held during the reset at occupancy 7, incrementing `count` to 8 on the first edge and masking the bug when reset took effect on the second edge.

  * Weighting `wr_data` (`0xFF` 6%, `0x00` 6%, uniform 88%) caught **`data_ff_at_cnt7`** (raising the score from `4/6` to `5/6`), which was a *reachability* gap in our un-crossed data space.

  * The single remaining survivor across both runs, **`rd_data_when_empty`**, is an *observability* choice rather than a bug: the mutant drives `0xAA` onto `rd_data` while `empty == 1`, which the specification leaves undefined and our scoreboard deliberately ignores.


* \[x\] Every `illegal` and `ignore` bin in section 3 cites an authority.

* \[x\] Section 5 names blind spots of this design, not of coverage in general.

* \[x\] The numbers here agree with `coverage.yml` and `FINDINGS.md`.