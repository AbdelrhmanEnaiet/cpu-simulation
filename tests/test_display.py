from backend.devices.display import Display
from backend.memory.bus import Bus
def test_exact_pixel_update():
    bus = Bus()
    bus.write(0xD000, 0x8000)
    pixel_array = bus.screen_pixels()
    display = Display()
    screen__pixel_flag = display.pixels(pixel_array)

    for i in range(len(screen__pixel_flag)):
        for m in range(len(screen__pixel_flag[i])):
            if i==0 and m==0:
                assert screen__pixel_flag[i][m] == True
                continue
            assert screen__pixel_flag[i][m] == False


def test_screen_size_32_row_64_column():
    bus = Bus()
    pixel_array = bus.screen_pixels()
    display = Display() 
    screen__pixel_flag = display.pixels(pixel_array)
    assert len(screen__pixel_flag)==32
    assert len(screen__pixel_flag[0])==64

def test_activate_full_screen():
    bus = Bus()
    for addr in range(bus.SCREEN_PIXEL_START, bus.SCREEN_PIXEL_END):
        bus.write(addr, 0xFFFF)
    pixel_array = bus.screen_pixels()
    display = Display() 
    screen__pixel_flag = display.pixels(pixel_array)
    for y in range(0,32):
        for x in range(0,64):
            assert screen__pixel_flag[y][x] is True

def test_activate_specific_pixel():
    bus = Bus()
    bus.write(0xD016, 2**10)
    pixel_array = bus.screen_pixels()
    display = Display()
    screen__pixel_flag = display.pixels(pixel_array)

    assert screen__pixel_flag[5][36] == False
    assert screen__pixel_flag[5][37] == True
    assert screen__pixel_flag[5][38] == False