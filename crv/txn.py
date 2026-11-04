import os

import vsc

WIDTH = int(os.environ.get("WIDTH", "8"))
DEPTH = int(os.environ.get("DEPTH", "8"))

FILL, DRAIN, WR_ONLY, RD_ONLY = 0, 1, 2, 3


@vsc.randobj
class FifoTxn:
    def __init__(self, width=WIDTH):
        self.wr_en = vsc.rand_bit_t(1)
        self.rd_en = vsc.rand_bit_t(1)
        self.wr_data = vsc.rand_bit_t(width)
        self.roll_w = vsc.rand_uint8_t()
        self.roll_r = vsc.rand_uint8_t()
        self.phase = vsc.uint8_t(FILL)

    @vsc.constraint
    def rolls_c(self):
        self.roll_w < 100
        self.roll_r < 100
        # solve each roll before its enable, or the weights drift off uniform
        vsc.solve_order(self.roll_w, self.wr_en)
        vsc.solve_order(self.roll_r, self.rd_en)

    @vsc.constraint
    def ops_c(self):
        # no vsc.dist under a guard: this pyvsc build applies it unconditionally
        with vsc.if_then(self.phase == FILL):
            self.wr_en == (self.roll_w < 85)
            self.rd_en == (self.roll_r < 10)
        with vsc.else_if(self.phase == DRAIN):
            self.wr_en == (self.roll_w < 10)
            self.rd_en == (self.roll_r < 85)
        with vsc.else_if(self.phase == WR_ONLY):
            self.wr_en == 1
            self.rd_en == 0
        with vsc.else_then():
            self.wr_en == 0
            self.rd_en == 1
