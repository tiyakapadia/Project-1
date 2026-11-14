# Contributions — <team name> · <track>

**Members:** Tiya Kapadia ti506075 · Paul Rich pa630816· Jason Ralph (NID) …>
**Repo:** [(https://github.com/tiyakapadia/Project-1)]
**Track:** Constrained-Random Verification of Parameterized FIFO
**Last updated:** 11/12/26 · **through milestone:** M4

---

## How to read this file

Each milestone section lists what each member owned, with the commits, files, or
tags that show it. "Helped with the testbench" is not a contribution record.
"Wrote the constrained-random sequence and its coverage bins — `tb/seq_rw.py`,
commits `a1b2c3d`..`e4f5g6h`" is.

Work that is genuinely shared gets its own row and says how it was shared
(pairing, review, a split you can describe). Do not inflate, and do not
flatten real differences into a polite fiction — an honest record of an uneven
milestone reads far better than a uniform one nobody believes.

---

## M1 — <due Wk 11>

| Member | What they owned | Evidence (commits / files / PRs) | Approx. share |
|--------|-----------------|----------------------------------|--------------:|
| Tiya Kapadia | Driver and Monitor component development and interface integration | `tb/driver.py`, `tb/monitor.py`, `test_fifo py` | 34% |
| Paul Rich | Verification Plan authorship and initial requirements mapping | `vplan.md` | 33% |
| Jason Ralph | Initial transaction structuring and base simulation harness | `crv/txn.py`, `Makefile` | 33%

**Shared or paired work:**
For the most part, we all worked individually
**What slipped, and who picked it up:**
Some initial enviornment confusion, but it was easily fixable
>

## M2 — <due Wk 12>

| Member | What they owned | Evidence (commits / files / PRs) | Approx. share |
|--------|-----------------|----------------------------------|--------------:|
| Tiya Kapadia | Driver/Monitor refinement and waveform verification | `tb/driver.py`, `tb/monitor.py`, `fifo.fst` | 33% |
| Paul Rich | Scoreboard model and expected FIFO output checking | `tb/scoreboard.py` | 34% |
| Jason Ralph | PyVSC transaction constraints and stimulus legality enforcement | `crv/txn.py`, `crv/phase.py` | 33% |

**Shared or paired work:**
Integrating the scoreboard with the monitor outputs to ensure accurate checking.

**What slipped, and who picked it up:**
Handling corner-case occupancy boundaries during simultaneous read/write; fixed via constraint tuning.

**Changes to the division of labor since M1, and why:**
For the most part, the insitial split of labor was kept the same, and each member respectivley worked on their portion. 

## M3 — <due Wk 13>

| Member | What they owned | Evidence (commits / files / PRs) | Approx. share |
|--------|-----------------|----------------------------------|--------------:|
| Tiya Kapadia | Regression log review and testbench integration support | `regress_logs/summary.txt` | 33% |
| Paul Rich | Functional coverage model, coverpoints, bins, and crosses | Coverage collector script and yaml reports | 34% |
| Jason Ralph | Seeded regression automation, stimulus distribution tracking, and hole closure | `regress.sh`, `regress_logs/` | 33% |

**Shared or paired work:**
Analyzing coverage holes and tuning PyVSC weights to achieve coverage closure.

**What slipped, and who picked it up:**
We didn't have any slips this week. 

**Changes to the division of labor since M2, and why:**


## M4 — <due Wk 14, at the `m4` tag>

| Member | What they owned | Evidence (commits / files / PRs) | Approx. share |
|--------|-----------------|----------------------------------|--------------:|
Tiya Kapadia | Report section compilation, environment documentation, and version tracking | `REPORT.md`, `CONTRIBUTIONS.md` | 33% |
| Paul Rich | Coverage closure verification and mutation analysis review | `REPORT.md`, '| 33% |
| Jason Ralph| Mutation testing execution and findings documentation | `mutants_released.yaml`, `FINDINGS.md` | 34% |

**Shared or paired work:**
Writing the reoirt, test suite re-runs, and final sign-off.

**What slipped, and who picked it up:**
We didn't have any slips this week. 

---

## Whole-project summary

One row per member, across all four milestones. This is the row a reader checks
first, so it must be consistent with the four sections above.

| Member | Principal contributions (all four milestones) | Overall share |
|--------|-----------------------------------------------|--------------:|
|Tiya Kapadia | Driver/Monitor (`tb/driver.py`, `tb/monitor.py`), Report integration, and tracking | 33% |
| Paul Rich | `vplan.md`, Scoreboard (`tb/scoreboard.py`), and Functional Coverage model | 34% |
| JasR321 | PyVSC Constraints, Seeded Regression (`regress.sh`), and `FINDINGS.md` | 33% |

**The three things this team did that we would each defend in an interview:**

1. Implementing a cycle-accurate scoreboard verifying data integrity and flags every clock cycle.
2. Designing targeted PyVSC constraints that successfully stressed deep boundary states (full/empty) and simultaneous operations.
3. Achieving a 100% kill rate on the released mutant pool through robust verification environments.

## Non-code contributions

Real work that leaves a thin git trace — and is graded all the same. Cite the
artifact where one exists.

| Member | Contribution | Where it shows |
|--------|--------------|----------------|
| Tiya Kapadia | Documentation tracking and waveform verification | `CONTRIBUTIONS.md`, `REPORT.md` |
| Paul Rich | Spec archaeology and test planning | `vplan.md` |
| Jason Ralph | Regression script automation and failure analysis | `regress.sh`, `FINDINGS.md` |

## AI assistance

Consistent with the course policy and your `ctm` record: name where an assistant
was used on capstone work, and who verified the output. The verifier is a named
person, always.

| Where | Used for | Verified by | Where the verification shows |
|-------|----------|-------------|------------------------------|
| Claude / Gemini AI | Syntax reference, boilerplate structuring, and debugging assistance | Tiya Kapadia / Paul Rich / Jason Ralph | `ai_log.md`, code implementations |

---

## Attestation

- [X] Every claim above can be traced to the repo history.
- [X] This file was updated at each milestone, not reconstructed at the end.
- [X] Every member has read this file and agrees it is accurate.
- [X] Each member has separately submitted their **confidential individual peer
      eval** — teammates' main contributions, an equity judgment, one sentence
      of evidence each — outside this repo, by the M4 deadline.

