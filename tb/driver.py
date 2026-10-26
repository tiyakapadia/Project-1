import cocotb
from cocotb.triggers import RisingEdge
from tb.scoreboard import Txn


class FifoDriver:
    def __init__(self, dut):
        self.dut = dut
        # default values
        self.dut.wr_en.value = 0
        self.dut.rd_en.value = 0
        self.dut.wr_data.value = 0

    async def drive(self, txn: Txn):
        """Drives a single transaction onto the DUT pins."""
        self.dut.wr_en.value = txn.wr_en
        self.dut.rd_en.value = txn.rd_en
        
        if txn.wr_en:
            self.dut.wr_data.value = txn.wr_data
            
        await RisingEdge(self.dut.clk)
        
        self.dut.wr_en.value = 0
        self.dut.rd_en.value = 0