from typing import Any, Dict, List

from backend.cpu.model import CpuState
from backend.memory.bus import Bus


class Cpu:
    def __init__(self, bus: Bus) -> None:
        self.bus: Bus = bus
        self._set_internal_params_to_default()

    def _set_internal_params_to_default(self) -> None:
        self.registers: List[int] = [0,0,0,0]
        self.pc: int = 0
        self.sp: int = 0xC000
        self.z: int  = False
        self.c: int  = False
        self.n: int  = False
        self.status: str = CpuState.RUNNING.value
        self.error = None

    def load(self, instructions: List[int]) -> None:
        for addr, word in enumerate(instructions):
            self.bus.write(addr, word)

    def reset(self) -> None:
        self._set_internal_params_to_default()
        self.bus.flush()
    def snapshot(self) -> Dict[str,Any]:
        raise NotImplementedError