import argparse

from caches import *

import m5
from m5.objects import *

parser = argparse.ArgumentParser(
    description="A simple system with 2-level cache."
)
parser.add_argument(
    "binary",
    default="",
    nargs="?",
    type=str,
    help="Path to the binary to execute.",
)
parser.add_argument(
    "--l1i_size", help=f"L1 instruction cache size. Default: 16kB."
)
parser.add_argument(
    "--l1d_size", help="L1 data cache size. Default: Default: 64kB."
)
parser.add_argument("--l2_size", help="L2 cache size. Default: 256kB.")

options = parser.parse_args()

system = System()

# clock and voltage
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "1GHz"
system.clk_domain.voltage_domain = VoltageDomain()

# memory
system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MB")]

# CPU
system.cpu = RiscvTimingSimpleCPU()

# memory bus
system.membus = SystemXBar()

# caches
system.cpu.icache = L1ICache(options)
system.cpu.dcache = L1DCache(options)
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

system.l2bus = L2XBar()
system.cpu.icache.connectBus(system.l2bus)
system.cpu.dcache.connectBus(system.l2bus)

system.l2cache = L2Cache(options)
system.l2cache.connectCPUSideBus(system.l2bus)
system.l2cache.connectMemSideBus(system.membus)

system.cpu.createInterruptController()
system.system_port = system.membus.cpu_side_ports

# memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# specify the program file
binary = "tests/test-progs/hello/bin/riscv/linux/hello"

# syscall emulation mode
system.workload = SEWorkload.init_compatible(options.binary)

process = Process()
process.cmd = [binary]
system.cpu.workload = process
system.cpu.createThreads()

# instantiate the simulation
root = Root(full_system=False, system=system)
m5.instantiate()

print("Beginning Simulation!")
exit_event = m5.simulate()

print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
