import sys
sys.path.append("./")
from backend.devices.device import Keys, FrameCounter, Random


class Bus:
    MAX_WORD_IN_MEMORY = 0xFFFF
    MEMORY_SIZE = 65536 

    def __init__(self, seed=None):
        self.memory = [0] * self.MEMORY_SIZE 
        self.keys = Keys()
        self.frame_counter = FrameCounter()
        self.rng = Random(seed)

    def _check_memory_bound(self,addr):
        if addr>=self.MEMORY_SIZE or addr<0:
            raise IndexError("Requested Memory is out of bound")

    def _check_addr_access(self, addr):
        if addr <= 0xC0FF and addr>= 0xC003:
            return False
        return True
        
    def read(self,addr):
        self._check_memory_bound(addr)
        if addr==0xC000: return self.keys.read()
        if addr==0xC001: return self.frame_counter.read()
        if addr==0xC002: return self.rng.read()

        return self.memory[addr]
    
    def write(self,addr, value):
        self._check_memory_bound(addr)

        if addr==0xC000: return self.keys.write(value)
        if addr==0xC001: return self.frame_counter.write(value)
        if addr==0xC002: return self.rng.write(value)

        value = value & self.MAX_WORD_IN_MEMORY
        if self._check_addr_access(addr):
            self.memory[addr]=value

    def screen_pixels(self) -> list:
        return self.memory[0xD000:0xD07F+1]
