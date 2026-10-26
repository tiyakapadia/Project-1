# Verification plan — <DUT>

**Author Paul Rich** **Spec version:** **Date:**

> A vplan is an argument that "done" is definable before you write tests. Every
> row here should be something you could defend in a signoff meeting. Rows you
> cannot defend are the honest content of the Risk section, not omissions.

## 1. Scope

**In scope:** <This plan verifes the functional behavior of the provided synchronous FIFO RTL against the written specification. The verification will check FIFO ordering, read and write operations, empty, full, and almost-full behavior, overflow and underflow behavior, boundary conditions, simultaneous read and write operations, and reset behavior. The project will also use constrained-random testing, functional coverage, and mutation testing to measure the effectiveness of the verification environment.>
**Out of scope:** <This project does not provide formal or exhaustive verification of every possible FIFO state and input sequence. Physical implementation, timing closure, setup and hold timing, power analysis, analog behavior, signal integrity, and clock-domain crossing are not verified.>
**Assumptions about the environment:** <The FIFO operates using the clock and reset behavior defined by the provided specification. Normal constrained-random stimulus will generate legal transactions. The scoreboard will use a reference queue and will determine expected behavior from the written specification.>

## 2. Feature list

One row per behavior the spec requires. `Req` cites a line or section of the
spec — if you cannot cite one, that is a spec gap and it belongs in section 5.

Reset places the FIFO into the required initial state
| ID | Feature | Req | Priority | How it is verified |
|----|---------|-----|----------|--------------------|
| F1 | Reset places the FIFO in the required initial state (empty, not full, pointers/count cleared) | Spec — Reset: TBD | H | directed / assertion |
| F2 | A valid write stores the input data | Spec — Write: TBD | H | directed / CRV / scoreboard |
| F3 | A valid read returns the oldest stored value | Spec — Read: TBD | H | directed / CRV / scoreboard |
| F4 | Data is read in the order it was written, including across pointer wrap-around | Spec — Ordering: TBD | H | directed / CRV / scoreboard |
| F5 | `empty` asserts and deasserts at the correct time | Spec — Empty: TBD | H | directed / CRV / assertion |
| F6 | `full` asserts and deasserts at the correct time | Spec — Full: TBD | H | directed / CRV / assertion |
| F7 | `almost_full` asserts and deasserts at the specified threshold | Spec — Almost-full: TBD | H | directed / CRV / assertion |
| F8 | A read while empty behaves as the spec defines | Spec — Underflow: TBD | H | directed / assertion |
| F9 | A write while full behaves as the spec defines | Spec — Overflow: TBD | H | directed / assertion |
| F10 | Operations at occupancy 0 and 1 produce correct data and flags | Spec — Occupancy: TBD | H | directed / CRV / scoreboard |
| F11 | Operations at occupancy DEPTH-1 and DEPTH produce correct data and flags | Spec — Occupancy: TBD | H | directed / CRV / scoreboard |
| F12 | Simultaneous read and write behave as the spec defines, in the middle and at both boundaries | Spec — Simultaneous operation: TBD | H | directed / CRV / scoreboard |
| F13 | Bursty traffic preserves correct behavior (stimulus profile, not a spec behavior) | Project CRV requirement | M | CRV / scoreboard |
| F14 | Capacity matches the configured `DEPTH` | Spec — Parameters: TBD | H | directed / CRV |
| F15 | Data is stored and returned correctly for the configured `WIDTH` | Spec — Parameters: TBD | M | CRV / scoreboard |
| F16 | FWFT output behavior is correct when that configuration is tested | Spec — FWFT: TBD | M | directed / CRV |
| F17 | At least one illegal or undefined control combination is covered or checked (project-derived, not spec-derived) | Project Security & Trust requirement | M | coverage / assertion |

## 3. Coverage model

Coverpoints and their bins. A cross earns its place only if the interaction is
where a bug would hide — say which bug.

| ID | Coverpoint | Bins | Why these bins |
|----|-----------|------|----------------|
| C1 | FIFO occupancy | 0, 1, mid (2..DEPTH-2), DEPTH-1, DEPTH | Exact boundary levels where off-by-one bugs sit |
| C2 | Read/write combination | idle, read only, write only, read and write | All control combinations; subsumes separate read/write request coverpoints |
| C3 | `almost_full` vs threshold | occupancy AF_T-1, AF_T, AF_T+1 | Threshold off-by-one and flag-lag bugs |
| C4 | Pointer wrap | write pointer wrapped, read pointer wrapped, both wrapped since reset | Wrap-around corruption and flag errors |
| C5 | Occupancy change | increase, decrease, unchanged | Confirms each operation type moves the count correctly (checked via scoreboard) |
| C6 | Burst profile | consecutive writes ≥ DEPTH, consecutive reads ≥ DEPTH, alternating read/write | Sustained fill, drain, and interleave |
| C7 | Reset timing | reset when empty, partially full, full; reset while a request is active | Stale data or count after reset mid-traffic |
| C8 | Configuration | each tested DEPTH × WIDTH × FWFT combination | Ties coverage to configurations actually run |



**Crosses**

| ID | Cross | The interaction it is aimed at (and the bug it targets) |
|----|-------|-------------------------------|
| X1 | C1 × C2 | Operations at each boundary level. Targets: write+read at full dropping or wrongly accepting the write; read+write at empty returning stale data or underflowing; count off by one |
| X2 | C3 × C2 | Operations around the `almost_full` threshold. Targets: threshold off by one, flag updating one cycle late, flag not clearing on a read |
| X3 | C4 × C2 | Operations while pointers wrap. Targets: wrap error under simultaneous read/write, wrong `full`/`empty` after wrap |
| X4 | C7 × C2 | Reset against active requests. Targets: a request completing during reset, or stale data/count after reset |


**Illegal / ignore bins:** <Transactions the spec defines as illegal are never generated by constrained-random stimulus. Illegal or undefined cases required by F17 are driven only by directed tests (T12). For each, the expected result is either the spec-defined behavior or an explicit "no check". Reset with an active request is treated as legal stimulus unless the spec says otherwise.>

## 4. Test matrix

Every feature maps to at least one test; every test traces back to a feature.
An untraceable test is a test nobody can defend.

| Test | Features | Kind | Pass criterion |
|------|----------|------|----------------|
| T1 — Reset | F1 | directed / assertion | After reset: `empty` high, `full` low, `almost_full` low, and the first read after one write returns that write |
| T2 — Single write and read | F2, F3 | directed | The written value is returned by the next valid read |
| T3 — FIFO ordering | F2, F3, F4 | directed | N distinct values are read in write order |
| T4 — Empty boundary | F5, F8, F10 | directed | `empty` follows the spec on transitions 0↔1; a read at empty produces the spec-defined result and does not corrupt later reads |
| T5 — Full boundary | F6, F9, F11, F14 | directed | After DEPTH writes with no reads, `full` is high per spec timing; a write at full produces the spec-defined result; the first DEPTH values read back intact |
| T6 — Almost-full boundary | F7 | directed / random | `almost_full` changes at AF_T exactly, on both fill and drain |
| T7 — Simultaneous read/write | F12 | directed / random | Data and occupancy match the reference queue in the middle of the range |
| T8 — Boundary simultaneous operations | F10, F11, F12 | directed / random | Read+write at empty and at full match the spec-defined result and the reference queue |
| T9 — Pointer wrap | F4, F14 | directed / random | After more than DEPTH total writes through the FIFO (several wraps), all data and flags match the reference queue |
| T10 — Reset mid-traffic | F1, F12 | directed | Reset with a non-empty FIFO and with active requests returns the FIFO to the initial state with no stale data; back-to-back resets behave the same |
| T11 — Bursty operations | F4, F10, F11, F13 | random | DUT data and flags stay consistent with the reference queue under fill, drain, and interleave bursts |
| T12 — Illegal/undefined control case | F17 | assertion / coverage | Required condition is reached and either checked against the spec or recorded as "no check" |
| T13 — Parameter configuration | F14, F15, F16 | directed / random | Each tested configuration passes T1–T11 with a configuration-aware scoreboard |
| T14 — Constrained-random regression | F1–F16 | random | No unexplained scoreboard, assertion, or protocol failures across all recorded seeds |

## 5. Risk and spec ambiguity

| # | Ambiguity or risk | Where in the spec | How I resolved it | Residual |
|---|-------------------|-------------------|-------------------|----------|
| 1 | Exact requirement citations not yet added | Whole spec | Replace each `TBD` with a section/line citation; uncitable rows become spec gaps listed here | Traceability incomplete until done |
| 2 | Exact `almost_full` threshold and its direction (≥ or >) | Almost-full: TBD | Take from spec; if unstated, ask | None once confirmed |
| 3 | Behavior of read while empty and write while full (ignored, error flag, undefined) | Underflow / Overflow: TBD | Take from spec, never from RTL; if unstated, ask and test both | Undefined behavior stays undefined |
| 4 | Whether `empty`/`full`/`almost_full` are registered or combinational | Flags: TBD | Take from spec; scoreboard timing derived from it | Wrong timing model if spec is silent |
| 5 | Read latency (non-FWFT vs FWFT) and when data is valid | Read / FWFT: TBD | Configuration-aware scoreboard | FWFT not verified if not run |
| 6 | Simultaneous read+write at empty and at full | Simultaneous operation: TBD | Test middle, empty, and full cases separately (T7, T8) | Risk remains if spec is unclear |
| 7 | Reset type (sync/async) and effect on in-flight operations | Reset: TBD | Take from spec; T10 covers mid-traffic reset | Undefined cases remain if spec is silent |
| 8 | Random stimulus may not reach boundaries often enough | Project CRV requirement | Weight constraints toward near-empty, near-full, wrap, burst, and simultaneous operations; confirm via X1–X3 | Random testing is not exhaustive |
| 9 | Illegal/undefined control combinations may have no required output | Security & Trust requirement | Cover the condition; do not claim a result unless the spec defines one | Undefined behavior remains undefined |
| 10 | High coverage does not guarantee bug detection | Project coverage and mutation requirements | Use both coverage and mutation testing | Bugs outside the model and mutant pool may remain |
| 11 | Random failures must be reproducible | Project reproducibility requirement | Record seed and command for every run | None when seeds are preserved |


## 6. Closure criteria

State the numbers *before* you start, so closure is a measurement and not a
negotiation.

- Functional coverage target: **_100_%** of the model in section 3
- Mutation target: **__/__** on the hidden pool
- Assertions: every property paired with a passing `cover` (no vacuous passes)
- What I will report as **not verified**:
    - Formal or exhaustive correctness of every FIFO state and sequence
    - WIDTH, DEPTH, or FWFT configurations not in the tested list above
    - Undefined behavior with no required result in the spec
    - Bugs not exercised by the environment or not represented in the mutant pool