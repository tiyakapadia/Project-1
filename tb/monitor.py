import cocotb
from cocotb.triggers import RisingEdge, ReadOnly
from tb.scoreboard import Obs

class FifoMonitor:
    def __init__(self, dut, callback):
        self.dut = dut
        self.callback = callback
        # background monitoring loop
        cocotb.start_soon(self.monitor_loop())

    async def monitor_loop(self):
        """Samples the DUT outputs every clock cycle and passes them to the scoreboard."""
        while True:
            await RisingEdge(self.dut.clk)
            await ReadOnly()  # wait for combinational logic to settle
            
            # avoid sampling during reset or when reset is in an x/z state
            if self.dut.rst_n.value.is_resolvable and int(self.dut.rst_n.value) == 1:
                
                count = int(self.dut.count.value)
                full = int(self.dut.full.value)
                empty = int(self.dut.empty.value)
                
                # FWFT behavior: rd_data is only valid if the FIFO is not empty
                if not empty and self.dut.rd_data.value.is_resolvable:
                    rd_data = int(self.dut.rd_data.value)
                else:
                    rd_data = None
                    
                obs = Obs(count, full, empty, rd_data)
                self.callback(obs)