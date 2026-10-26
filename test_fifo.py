import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge
from cocotb.queue import Queue

from tb.driver import FifoDriver
from tb.monitor import FifoMonitor
from tb.scoreboard import FifoScoreboard, Txn

async def reset_dut(dut):
    # Set default inputs
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.wr_data.value = 0
    
    # Pulse active-low reset
    dut.rst_n.value = 0
    for _ in range(2):
        await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

@cocotb.test()
async def test_fifo_smoke(dut):
    # Start the clock 
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    
    # Reset the DUT
    await reset_dut(dut)
    
    # 1. Setup the environment using Paul's scoreboard
    obs_queue = Queue()
    driver = FifoDriver(dut)  # Removed dut.clk argument
    monitor = FifoMonitor(dut, callback=obs_queue.put_nowait)
    scoreboard = FifoScoreboard()
    
    # Clear any leftover reset observations from the queue
    while not obs_queue.empty():
        obs_queue.get_nowait()
    
    # 2. Send a transaction using Paul's Txn namedtuple
    tx_write = Txn(wr_en=1, rd_en=0, wr_data=99)
    await driver.drive(tx_write)
    
    # 3. Pull the resulting observation from the monitor and check it
    obs = await obs_queue.get()
    scoreboard.check(tx_write, obs, tag="Smoke Write")