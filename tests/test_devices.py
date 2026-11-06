from backend.devices.device import Random, Keys, FrameCounter

def test_set_keys_inbound():
    keys = Keys()
    keys.set_keys(17)
    value = keys.read()
    assert value==17
def test_set_keys_outbound():
    keys = Keys()
    keys.set_keys(33)
    value = keys.read()
    assert value==1
def test_write_from_cpu():
    keys = Keys()
    keys.write(46)
    value = keys.read()
    assert value==0

def test_frame_counter():
    frame = FrameCounter()
    value_1 = frame.read()
    frame.tick_frame()
    value_2 = frame.read()

    assert value_1 == 0
    assert value_2 == 1

    frame.frame_counter = 0xFFFF
    frame.tick_frame()
    value_3 = frame.read()
    assert value_3 == 0

def test_random_seed_consistency():
    random = Random(seed=19736)
    value_1 = random.read()
    random.write(5)
    value_2 = random.read()
    random.write(19736)
    value_3 = random.read()
    assert value_1 != value_2
    assert value_1 == value_3