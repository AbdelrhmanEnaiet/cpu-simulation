from backend.memory.bus import Bus
from backend.cpu.cpu import Cpu
from backend.cpu.model import CpuState


def test_load_words_in_memory():
    instructions = [0x0100, 0x0005, 0x0110, 0x0003, 0x1001, 0xFF00]
    bus = Bus()
    cpu = Cpu(bus=bus)
    cpu.load(instructions)
    for addr, command in enumerate(instructions):
        value = bus.read(addr)
        assert value == command
    value = bus.read(len(instructions))
    assert value == 0

def test_attributes_reset():
    bus = Bus()
    cpu = Cpu(bus=bus)
    cpu.pc = 99
    cpu.sp = 99
    cpu.z = True
    cpu.n = True
    cpu.c = True
    cpu.registers = [
        3,77,9,22
    ]
    cpu.status = CpuState.HALTED.value
    cpu.reset()
    assert len(cpu.registers) == 4
    for value in cpu.registers:
        assert value==0
    assert cpu.pc == 0
    assert cpu.sp == 0xC000 
    assert cpu.z is False
    assert cpu.n is False
    assert cpu.c is False
    assert cpu.status == CpuState.RUNNING.value


def test_snapshot():
    bus = Bus()
    cpu = Cpu(bus=bus)
    cpu.reset()
    snapshot = cpu.snapshot()
    assert snapshot == {
        "R0": 0,
        "R1": 0,
        "R2": 0,
        "R3": 0,
        "PC": 0,
        "SP": 0xC000,
        "Z": False,
        "C": False,
        "N": False,
        "status": "running",
        "error": None,
    }
