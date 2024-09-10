import m5
from m5.objects import *

system = System()

# clock and voltage
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "1GHz"
system.clk_domain.voltage_domain = VoltageDomain()

# memory
system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MB")]

# CPU
system.cpu = RiscvMinorCPU()

# memory bus
system.membus = SystemXBar()

# no cache system
# cpu.icache_port is a request port
# membus.cpu_side_ports is an array of response ports
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports

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
system.workload = SEWorkload.init_compatible(binary)

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
