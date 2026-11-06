from backend.devices.display import Display
from backend.memory.bus import Bus
def test_exact_pixel_update():
    bus = Bus()
    bus.write(0xD000, 0x8000)
    pixel_array = bus.screen_pixels()
    display = Display()
    screen__pixel_flag = display.pixels(pixel_array)

    assert screen__pixel_flag[0][0] == True

    