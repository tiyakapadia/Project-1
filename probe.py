import random
import sys

sys.path.insert(0, ".")
sys.path.insert(0, "lib")
from crv.txn import DRAIN, FILL, RD_ONLY, WR_ONLY, FifoTxn

N = 1000
random.seed(1)
txn = FifoTxn()
for phase, name in ((FILL, "FILL   "), (DRAIN, "DRAIN  "), (WR_ONLY, "WR_ONLY"), (RD_ONLY, "RD_ONLY")):
    txn.phase = phase
    wr = rd = both = 0
    for _ in range(N):
        txn.randomize()
        w, r = int(txn.wr_en), int(txn.rd_en)
        wr += w
        rd += r
        both += w & r
    print(f"phase={name}  P(wr)={wr / N:.2f}  P(rd)={rd / N:.2f}  P(both)={both / N:.2f}")
