# Default simulator 
SIM ?= icarus

# Hardware language
TOPLEVEL_LANG ?= verilog

# Path to your Verilog RTL file.
VERILOG_SOURCES += $(PWD)/fifo.sv

# The exact name of the Verilog module inside fifo.sv
TOPLEVEL = fifo

COCOTB_TEST_MODULES = test_fifo

include $(shell cocotb-config --makefiles)/Makefile.sim