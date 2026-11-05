class Bus:
    MAX_WORD_IN_MEMORY = 0xFFFF
    MEMORY_SIZE = 65536 

    def __init__(self):
        self.memory = [0] * self.MEMORY_SIZE 

    def _check_memory_bound(self,addr):
        if addr>=self.MEMORY_SIZE or addr<0:
            raise IndexError("Requested Memory is out of bound")
        
    def read(self,addr):
        self._check_memory_bound(addr)
        return self.memory[addr]
    
    def write(self,addr, value):
        self._check_memory_bound(addr)
        value = value & self.MAX_WORD_IN_MEMORY
        
        self.memory[addr]=value

