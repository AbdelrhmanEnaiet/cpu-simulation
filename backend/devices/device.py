import random


class Device:
    def write(self,value):
        raise NotImplementedError
    def read(self):
        raise NotImplementedError

class Keys(Device):
    def __init__(self) -> None:
        self.keys = 0
    def write(self,value):
        pass
    def set_keys(self, value):
        self.keys = value & 0x1F
    def read(self) ->int:
        return self.keys

class FrameCounter(Device):
    def __init__(self) -> None:
        self.frame_counter = 0
    def write(self,value):
        pass
    def read(self) ->int:
        return self.frame_counter
    def tick_frame(self):             
        self.frame_counter = (self.frame_counter + 1) & 0xFFFF
        
class Random(Device):
    def __init__(self, seed=None) -> None:
        if seed is None:
            self.seed = random.randint(0, 1_000_000)
        else:
            self.seed = seed
        self.rng = random.Random(self.seed)
    def write(self, value: int):
        self.seed = value
        self.rng = random.Random(self.seed)
    def read(self):
        return self.rng.randrange(0x10000)