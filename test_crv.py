import os
import random
from collections import Counter

import cocotb
from cocotb.clock import Clock
from cocotb.queue import Queue
from cocotb.triggers import RisingEdge, Timer, with_timeout

from crv.phase import Phase
from crv.txn import DEPTH, WIDTH, FifoTxn
from driver import FifoDriver
from monitor import FifoMonitor
from scoreboard import FifoScoreboard, Txn

SEED = int(os.environ.get("SEED", "0xC0FFEE"), 0)
N_CYCLES = int(os.environ.get("N_CYCLES", "3000"))
BURSTS = int(os.environ.get("BURSTS", "1"))
RESETS = int(os.environ.get("RESETS", "1"))
ALL_ONES = (1 << WIDTH) - 1

RESET_PLAN = [
    (1 / 6, DEPTH - 1, 1, 0),
    (2 / 6, DEPTH, 1, 1),
    (3 / 6, DEPTH // 2, 0, 1),
    (4 / 6, 1, 1, 1),
    (5 / 6, 0, 1, 0),
]


async def reset_dut(dut):
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.wr_data.value = 0
    dut.rst_n.value = 0
    for _ in range(2):
        await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


async def reset_mid_traffic(dut, scoreboard, obs_queue, wr_en, rd_en):
    dut.wr_en.value = wr_en
    dut.rd_en.value = rd_en
    dut.wr_data.value = ALL_ONES
    dut.rst_n.value = 0
    for _ in range(2):
        await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    count, empty, full = int(dut.count.value), int(dut.empty.value), int(dut.full.value)
    assert (count, empty, full) == (0, 1, 0), \
        f"after reset with wr_en={wr_en} rd_en={rd_en}: count={count} empty={empty} full={full}"
    dut.rst_n.value = 1
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    scoreboard.reset()
    while not obs_queue.empty():
        obs_queue.get_nowait()


@cocotb.test()
async def test_crv(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    obs_queue = Queue()
    driver = FifoDriver(dut)
    FifoMonitor(dut, callback=obs_queue.put_nowait)
    scoreboard = FifoScoreboard(depth=DEPTH, width=WIDTH)
    scoreboard.reset()
    while not obs_queue.empty():
        obs_queue.get_nowait()

    random.seed(SEED)
    dut._log.info(f"SEED={SEED:#x}  N_CYCLES={N_CYCLES}  WIDTH={WIDTH}  DEPTH={DEPTH}  "
                  f"BURSTS={BURSTS}  RESETS={RESETS}")
    txn, phase = FifoTxn(WIDTH), Phase(DEPTH, burst_every=2 if BURSTS else 0)
    model = scoreboard.model
    hist = Counter()
    wr_full = rd_empty = both = 0
    run_w = run_r = run_alt = max_w = max_r = max_alt = 0
    prev = None
    pending = [(int(N_CYCLES * f), occ, w, r) for f, occ, w, r in RESET_PLAN] if RESETS else []
    resets_done = []

    for i in range(N_CYCLES):
        for item in pending:
            start, occ, rst_w, rst_r = item
            if i >= start and model.count == occ:
                await reset_mid_traffic(dut, scoreboard, obs_queue, rst_w, rst_r)
                pending.remove(item)
                resets_done.append((occ, rst_w, rst_r))
                break

        txn.phase = phase.update(model.count)
        txn.randomize()
        tx = Txn(int(txn.wr_en), int(txn.rd_en), int(txn.wr_data))

        wr_full += int(bool(tx.wr_en and model.full))
        rd_empty += int(bool(tx.rd_en and model.empty))
        both += int(bool(tx.wr_en and tx.rd_en and not model.full and not model.empty))
        run_w = run_w + 1 if tx.wr_en else 0
        run_r = run_r + 1 if tx.rd_en else 0
        cur = (tx.wr_en, tx.rd_en)
        if tx.wr_en == tx.rd_en:
            run_alt, prev = 0, None
        else:
            run_alt = run_alt + 1 if prev is not None and cur != prev else 1
            prev = cur
        max_w, max_r, max_alt = max(max_w, run_w), max(max_r, run_r), max(max_alt, run_alt)

        await driver.drive(tx)
        obs = await with_timeout(obs_queue.get(), 100, "ns")
        scoreboard.check(tx, obs, tag=f"seed {SEED:#x}")
        hist[model.count] += 1
        await Timer(1, unit="ns")

    dut._log.info("occupancy " + " ".join(f"{o}:{hist[o]}" for o in range(DEPTH + 1)))
    dut._log.info(f"wr_while_full={wr_full}  rd_while_empty={rd_empty}  simultaneous_rw_midrange={both}")
    dut._log.info(f"longest_run: writes={max_w} reads={max_r} alternating={max_alt}")
    dut._log.info(f"resets_done={len(resets_done)}  (occupancy, wr_en, rd_en): {resets_done}")

    assert wr_full, "stimulus never wrote into a full FIFO"
    assert rd_empty, "stimulus never read from an empty FIFO"
    assert both, "stimulus never did a simultaneous read+write mid-range"
    missing = set(range(DEPTH + 1)) - set(hist)
    assert not missing, f"stimulus never reached occupancy {sorted(missing)}"
    if BURSTS:
        assert max_w >= DEPTH, f"no burst of {DEPTH} consecutive write requests (longest {max_w})"
        assert max_r >= DEPTH, f"no burst of {DEPTH} consecutive read requests (longest {max_r})"
        assert max_alt >= DEPTH, f"no alternating read/write burst of {DEPTH} cycles (longest {max_alt})"
    if RESETS:
        assert not pending, f"resets never triggered: {pending}"
