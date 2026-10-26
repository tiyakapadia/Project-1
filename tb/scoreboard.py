import random
from collections import namedtuple

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from models.fifo_model import FifoModel

WIDTH = 8
DEPTH = 8

Txn = namedtuple("Txn", "wr_en rd_en wr_data")
Obs = namedtuple("Obs", "count full empty rd_data")

class FifoScoreboard:
    def __init__(self, depth=DEPTH, width=WIDTH):
        self.model = FifoModel(width=width, depth=depth)
        self.cycles = 0

    def reset(self):
        self.model.reset()

    def _expected(self, txn):
        """Step the model with this cycle's txn; return the expected Obs.
        NB: FifoModel.step's signature is (wr_en, wr_data, rd_en)."""
        m = self.model
        m.step(txn.wr_en, txn.wr_data, txn.rd_en)
        return Obs(m.count, int(m.full), int(m.empty), m.head)  # head None if empty

    def check(self, txn, obs, tag=""):
        exp = self._expected(txn)
        self.cycles += 1
        ctx = f"[{tag} cycle {self.cycles}] txn={txn} "
        assert obs.count == exp.count, f"{ctx}count dut={obs.count} exp={exp.count}"
        assert obs.full == exp.full, f"{ctx}full dut={obs.full} exp={exp.full}"
        assert obs.empty == exp.empty, f"{ctx}empty dut={obs.empty} exp={exp.empty}"
        if not exp.empty:    # FWFT head only defined when non-empty
            assert obs.rd_data == exp.rd_data, \
                f"{ctx}rd_data dut={obs.rd_data} exp={exp.rd_data}"
