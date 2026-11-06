import pytest
from backend.memory.bus import Bus

def test_memory_init_values_of_zero():
    bus = Bus(seed=0)
    for i in range(0, 0xC002): #this addr hold the random number generated with every read
        register_value = bus.read(i)
        assert register_value == 0
    for i in range(0xC003, 65536):
        register_value = bus.read(i)
        assert register_value == 0
        
def test_seed_determinisim():
    first_bus = Bus(seed=5)
    first_register_values = [first_bus.read(0xC002) for i in range(5)]
    
    second_bus = Bus(seed=5)
    second_register_values = [second_bus.read(0xC002) for i in range(5)]
    assert first_register_values == second_register_values

def test_memory_writing_can_be_recalled():
    bus = Bus()

    bus.write(0x0000, 2)
    bus.write(0x0234, 25)

    bus.write(0xBFFF, 7)
    first_value = bus.read(0x0000)
    second_value = bus.read(0x0234)
    last_value = bus.read(0xBFFF)
    assert first_value == 2
    assert second_value == 25
    assert last_value == 7

def test_memory_overflow_Masking():
    bus = Bus()
    bus.write(0x0234, 65536)
    value = bus.read(0x0234)
    assert value == 0

    bus.write(0x0239, 65540)
    value = bus.read(0x0239)
    assert value == 4

    bus.write(0x0244, 0x30005)
    value = bus.read(0x0244)
    assert value == 5

def test_requesting_negative_and_outbound_addr():
    bus = Bus()
    ls = [-1, 0x10000]
    for i in ls:
        with pytest.raises(IndexError):
            bus.read(i)
        with pytest.raises(IndexError):
            bus.write(i, 9)


def test_reserved_memory_no_write():
    bus = Bus(seed=5)
    addrs_to_check = [0xC003, 0xC007, 0xC0FF]
    for addr in addrs_to_check:
        bus.write(addr, 19)
        value = bus.read(addr)
        assert value==0
    bus.write(0xC100, 19)
    assert bus.read(0xC100)== 19

def test_keys_update_through_handler():
    bus = Bus()
    bus.set_keys(5)
    value_1 = bus.read(0xC000)
    assert value_1 == 5

def test_write_device_and_frame_counter():
    bus = Bus()
    bus.write(0xC000, 5)
    bus.write(0xC001, 5)
    value_1 = bus.read(0xC000)
    value_2 = bus.read(0xC001)

    assert value_1 == 0
    assert value_2 == 0

def test_write_random_state():
    bus = Bus(seed=19476)
    value_1 = bus.read(0xC002)
    bus.write(0xC002, 5)
    value_2 = bus.read(0xC002)
    bus.write(0xC002, 19476)
    value_3 = bus.read(0xC002)

    assert value_1 != value_2
    assert value_1 == value_3


def test_screen_pixels_length():
    bus = Bus()
    screen_pixels = bus.screen_pixels()
    assert len(screen_pixels) == 128

def test_screen_pixels_order_update():
    bus = Bus()
    bus.write(0xD000, 5)
    bus.write(0xD07F, 10)
    screen_pixels = bus.screen_pixels()
    assert screen_pixels[0]==5
    assert screen_pixels[127]==10

def test_screen_pixels_size_complience():
    bus = Bus()
    bus.write(0xD080 , 5)
    screen_pixels = bus.screen_pixels()
    for i in screen_pixels:
        assert i==0