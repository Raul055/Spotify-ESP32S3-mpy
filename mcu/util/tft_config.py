from machine import Pin, SPI
import st7789

TFA = 1
BFA = 3

# -- Adjust to the tft display used
WIDTH = 320
HEIGHT = 480
SCK_PIN = 39
MOSI_PIN = 40
RESET_PIN = 41
DC_PIN = 42
CS_PIN = 10
BACKLIGHT_PIN = 9 

# -- Available rotations
AVAILABLE_ROTATIONS = [
    (0x00, WIDTH, HEIGHT, 0, 0),	# 0. Portrait
    (0x60, HEIGHT, WIDTH, 0, 0),	# 1. Landscape
    (0xC0, WIDTH, HEIGHT, 0, 0),	# 2. Inverted Portrait
    (0xA0, HEIGHT, WIDTH, 0, 0),	# 3. Inverted Landscape
    
    (0x40, WIDTH, HEIGHT, 0, 0),	# 4. Portrait (Mirrored)
    (0x20, HEIGHT, WIDTH, 0, 0),	# 5. Landscape (Mirrored)
    (0x80, WIDTH, HEIGHT, 0, 0),	# 6. Inverted Portrait (Mirrored)
    (0xE0, HEIGHT, WIDTH, 0, 0),	# 7. Inverted Landscape (Mirrored)
]

# -- Select the correct rotation for your tft display
ROTATION = 4

# TFT used
tft_display = st7789.ST7789(
        SPI(1, baudrate=30000000, sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN)),
        WIDTH,
        HEIGHT,
        reset=Pin(RESET_PIN, Pin.OUT),
        cs=Pin(CS_PIN, Pin.OUT),
        dc=Pin(DC_PIN, Pin.OUT),
        backlight=Pin(BACKLIGHT_PIN, Pin.OUT),
        color_order=st7789.BGR,
        inversion=False,
        rotations=AVAILABLE_ROTATIONS,
        rotation=ROTATION
)