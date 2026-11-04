SIM ?= icarus
TOPLEVEL_LANG ?= verilog

WIDTH ?= 8
DEPTH ?= 8
export WIDTH DEPTH

DUT ?= $(CURDIR)/fifo.sv
VERILOG_SOURCES = $(DUT)
TOPLEVEL = fifo
MODULE ?= test_crv

SIM_BUILD ?= sim_build_w$(WIDTH)_d$(DEPTH)

ifeq ($(SIM),icarus)
COMPILE_ARGS += -Pfifo.WIDTH=$(WIDTH) -Pfifo.DEPTH=$(DEPTH)
endif
ifeq ($(SIM),verilator)
COMPILE_ARGS += -GWIDTH=$(WIDTH) -GDEPTH=$(DEPTH)
endif

export PYTHONPATH := $(CURDIR):$(CURDIR)/tb:$(CURDIR)/lib:$(PYTHONPATH)

include $(shell cocotb-config --makefiles)/Makefile.sim
