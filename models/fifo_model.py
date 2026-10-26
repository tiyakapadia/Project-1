"""Golden reference model for the CRAFT synchronous FWFT FIFO (dut/fifo.sv).

Mirrors the RTL exactly: full/empty gate writes/reads (evaluated on the
*current* state), a simultaneous read+write leaves the count unchanged, and
rd_data (the head) is valid only while !empty.
"""
from collections import deque


class FifoModel:
    def __init__(self, width=8, depth=8):
        self.width = width
        self.depth = depth
        self.mask = (1 << width) - 1
        self.q = deque()

    def reset(self):
        self.q.clear()

    @property
    def full(self):
        return len(self.q) == self.depth

    @property
    def empty(self):
        return len(self.q) == 0

    @property
    def count(self):
        return len(self.q)

    @property
    def head(self):
        """Value the DUT presents on rd_data; valid only when not empty."""
        return self.q[0] if self.q else None

    def step(self, wr_en, wr_data=0, rd_en=0):
        """Advance one clock edge; gating uses the pre-edge (current) state."""
        do_wr = bool(wr_en) and not self.full
        do_rd = bool(rd_en) and not self.empty
        if do_rd:
            self.q.popleft()
        if do_wr:
            self.q.append(wr_data & self.mask)
        return do_wr, do_rd
