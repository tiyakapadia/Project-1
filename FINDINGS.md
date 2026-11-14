# FINDINGS — Project 1, Team 5



## Score

| Pool | found | total | % |
|------|------:|------:|--:|
| released (practice) | 8 | 8 | 100% |
| hidden (reported at grading) | | | |
| our own extra mutants (self-made, not a course pool) | 5 | 6 | 83% |

The released score is 8/8 with the final stimulus at the default seed, and it was 8/8 at seeds 0xC0FFEE, 1, 2 and 3 before our last two changes. The extra score is 5/6 with the final stimulus at seeds 0xC0FFEE, 1, 2 and 3, and the only survivor is the same one each time.

The six extra mutants are ours, not the course's. We wrote them to get survivors to study, and we tuned the stimulus after seeing them, so the 5/6 is not independent evidence about the hidden pool.

**Command run:**

```bash
python -m craft_mutate.mutate --tb . --dut $PWD/fifo.sv --pool mutants_released.yaml --sim icarus
SEED=<0xC0FFEE|1|2|3> python -m craft_mutate.mutate --tb . --dut $PWD/fifo.sv --pool mutants_extra.yaml --sim icarus
```

## Survivors

One row per mutant your suite did not find. `Reachable?` is the important
column: a survivor you never reached is a *stimulus* problem, a survivor you
reached but did not notice is a *checking* problem, and they have different
fixes.

| Mutant | What it changes | Reachable by my stimulus? | Observable by my checks? | Why it survived |
|--------|-----------------|---------------------------|--------------------------|-----------------|
| rd_data_when_empty (extra) | rd_data shows 0xAA while the FIFO is empty | yes (the FIFO is empty about 700 of 3000 cycles) | no | The spec says rd_data is only valid when the FIFO is not empty, so the scoreboard checks it only when not empty. The mutant changes behavior the spec leaves undefined, so we treat it as spec-permitted, not as a gap in the suite. |

Survivors from our first run, before we tuned the stimulus (extras 3/6). All three were reachable states; two were stimulus problems and one is the survivor above.

| Mutant | Stimulus problem | Fix |
|--------|------------------|-----|
| reset_ignored_at_cnt7 | We did reset at occupancy 7, but with wr_en=1 held. The mutant ignored reset on the first edge, the write moved the count to 8, and reset worked on the second edge, so the write hid the bug. | Added a reset at occupancy 7 with wr_en=0 and rd_en=0. |
| data_ff_at_cnt7 | It needs a write of exactly 0xFF at occupancy 7, about 1 in 256 per write with uniform data. | Weighted wr_data: 0xFF 6%, 0x00 6%, uniform 88%. |

## What I changed, and what it bought

| Change | Score before | Score after | Which survivors it caught |
|--------|-------------:|------------:|---------------------------|
| Reset at occupancy 7 with both requests idle | 3/6 extras | 4/6 extras | reset_ignored_at_cnt7 |
| wr_data dist: 0xFF 6%, 0x00 6%, uniform 88% | 4/6 extras | 5/6 extras | data_ff_at_cnt7 |

The released pool was 8/8 before and after both changes.

## Stimulus distribution

Per-phase probabilities, measured with `probe.py` over 1000 samples each:

```
phase=FILL     P(wr)=0.84  P(rd)=0.09  P(both)=0.08
phase=DRAIN    P(wr)=0.08  P(rd)=0.84  P(both)=0.07
phase=WR_ONLY  P(wr)=1.00  P(rd)=0.00  P(both)=0.00
phase=RD_ONLY  P(wr)=0.00  P(rd)=1.00  P(both)=0.00
```

One run, 8-bit by 8-deep, seed 0xC0FFEE, 3000 cycles:

```
occupancy 0:704 1:564 2:200 3:218 4:203 5:203 6:194 7:243 8:471
wr_while_full=340  rd_while_empty=249  simultaneous_rw_midrange=99
longest_run: writes=19 reads=23 alternating=19
resets: (occupancy, wr_en, rd_en) = (7,1,0) (7,0,0) (8,1,1) (4,0,1) (1,1,1) (0,1,0)
```

Every occupancy level from 0 to 8 is visited, and the full, empty and simultaneous corners are all hit. Regression: seeds 0xC0FFEE and 1 to 8 all pass, and a rerun of 0xC0FFEE produced identical stimulus. The seed and the make command are in the head of each log in `regress_logs/`.

The shaping uses a roll per enable with `solve_order`, and a driver-owned FILL/DRAIN phase with a dwell at full and empty. Both patterns are adapted from the Week 5 HW5 field guide. The constraint and regression code was written with AI assistance, recorded in `ai_log.md`.

## Residual risk

What this suite still cannot catch, stated plainly. Name a fault class, not a
mutant id — the pool is a sample, not the population.

1. **Data-dependent faults on values other than 0x00 and 0xFF.** Only 12% of the data is biased. A fault that needs one specific other byte at one specific occupancy is reached roughly 1 time in 256 per write, which is the same weakness data_ff_at_cnt7 had before the fix.
2. **Configurations other than 8-bit by 8-deep.** We ran only WIDTH=8, DEPTH=8. The parameter overrides are in the Makefile and the test, but we did not run them.
3. **Reset timing.** Every reset we apply is held for exactly two clock edges. A fault that only shows with a one-cycle reset pulse, or with a long reset, is not exercised.
4. **Behavior between clock edges.** The scoreboard samples once per cycle, just after the edge. A glitch on a combinational flag that settles before the next sample would not be seen.
5. **Behavior the spec leaves undefined**, such as rd_data while empty, is deliberately unchecked.

**If I had another day:** We would use the coverage report to cross occupancy with the data corners. We showed that the data bias catches the fault at occupancy 7, but we have no measurement that it reaches the other occupancy levels, and that is the claim we would want before trusting it on the hidden pool.
