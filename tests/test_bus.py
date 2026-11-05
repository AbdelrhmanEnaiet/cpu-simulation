from backend.memory.bus import Bus

def test_memory_init_values():
    bus = Bus()
    for i in range(0, 65536):
        register_value = bus.read(i)
        assert register_value == 0

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

