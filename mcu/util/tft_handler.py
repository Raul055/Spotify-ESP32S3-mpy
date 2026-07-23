from machine import Pin, SPI
import st7789
import Noto_sans as font

# -- Handler for TFT display
class tft_handler:
    def __init__(self,
                    # -- Adjust to the tft display used
                    width=320,
                    height=480,
                    sck_pin=39,
                    mosi_pin=40,
                    reset_pin=41,
                    dc_pin=42,
                    cs_pin=10,
                    backlight_pin=9,
                    rotation=4,

                    # -- For debugging
                    debug=False
                ):

        # ----------------------------- HARDWARE SPECIFIC VALUES ----------------------------- #

        # -- Hardware specific, adjust in class to corresponding display used
        self.width = width
        self.height = height
        self.sck_pin = sck_pin
        self.mosi_pin = mosi_pin
        self.reset_pin = reset_pin
        self.dc_pin = dc_pin
        self.cs_pin = cs_pin
        self.backlight_pin = backlight_pin

        # -- Available rotations
        self.available_rotations = [
            (0x00, self.width,  self.height, 0, 0),	# 0. Portrait
            (0x60, self.height, self.width,  0, 0),	# 1. Landscape
            (0xC0, self.width,  self.height, 0, 0),	# 2. Inverted Portrait
            (0xA0, self.height, self.width,  0, 0),	# 3. Inverted Landscape
            
            (0x40, self.width,  self.height, 0, 0),	# 4. Portrait (Mirrored)
            (0x20, self.height, self.width,  0, 0),	# 5. Landscape (Mirrored)
            (0x80, self.width,  self.height, 0, 0),	# 6. Inverted Portrait (Mirrored)
            (0xE0, self.height, self.width,  0, 0)	# 7. Inverted Landscape (Mirrored)
        ]

        # Select the correct rotation for your tft display
        self.rotation = rotation

        # ----------------------------- ZONE CONFIG VALUES ----------------------------- #
        self.font_h       = 32
        self.zone_w       = 320
        self.zone_h       = 160
        self.zone_y       = 320
        self.rows         = self.zone_h // self.font_h  
        self.y_offset     = -8  # For vertical centering
        self.line_spacing = 8   # Extra pixels between lines


        # ----------------------------- TFT UTILS ----------------------------- #
        self.tft_display = None
        self.font = font
        self.display_colors = {
                                    "WHITE"     : st7789.WHITE,
                                    "BLACK"     : st7789.BLACK,
                                    "GREEN"     : st7789.GREEN,
                                    "RED"       : st7789.RED,
                                    "YELLOW"    : st7789.YELLOW,
                                    "BLUE"      : st7789.BLUE,
                                    "CYAN"      : st7789.CYAN,
                                    "MAGENTA"   : st7789.MAGENTA
                              }
        self.image_file = "cover.jpg"
        self.image_speed = {"FAST": st7789.FAST, "SLOW": st7789.SLOW}
        self.debug = debug

    # -- Debug print
    def debug_print(self, *args):
        if self.debug:
            print(*args)
    
    # -- Error handler
    def error_handler(self, e):
        if self.debug:
            print(f"Error: {e}")

    # -- Inits dsplay
    def init_display(self):
        # All good
        try:
            # Creates tft display instance
            self.tft_display = st7789.ST7789(
                    SPI(1, baudrate=30000000, sck=Pin(self.sck_pin), mosi=Pin(self.mosi_pin)),
                    self.width,
                    self.height,
                    reset=Pin(self.reset_pin, Pin.OUT),
                    cs=Pin(self.cs_pin, Pin.OUT),
                    dc=Pin(self.dc_pin, Pin.OUT),
                    backlight=Pin(self.backlight_pin, Pin.OUT),
                    color_order=st7789.BGR,
                    inversion=False,
                    rotations=self.available_rotations,
                    rotation=self.rotation
            )

            # Inits display
            self.tft_display.init()
            # All good, return true
            return True

        # Something went wrong, error
        except Exception as e:
            self.error_handler(e)
            # Init was not achieved, return false
            return False

    # -- Wraps text
    def wrap_text(self, text, max_width=None):
        # All good
        try:
            # By default, uses ZONE_W
            max_width = self.zone_w if max_width is None else max_width

            # Splits text and puts it into the display
            words = text.split(' ')
            lines = []
            current = ''
            for word in words:
                test = (current + ' ' + word).strip()
                if self.tft_display.write_len(self.font, test) <= max_width:
                    current = test
                else:
                    if current:
                        lines.append(current)
                    if self.tft_display.write_len(self.font, word) > max_width:
                        while self.tft_display.write_len(self.font, word) > max_width:
                            i = len(word) - 1
                            while i > 0 and self.tft_display.write_len(self.font, word[:i]) > max_width:
                                i -= 1
                            lines.append(word[:i])
                            word = word[i:]
                    current = word
            if current:
                lines.append(current)
            return lines

        # Something went wrong, error
        except Exception as e:
            self.error_handler(e)

    # -- Clears tft zone
    def clear_text_zone(self, bg):
        # All good
        try:
            self.tft_display.fill_rect(0, self.zone_y, self.zone_w, self.zone_h, bg)
        # Something went wrong, error
        except Exception as e:
            self.error_handler(e)

    # -- Draws text zone
    def draw_text_zone(self, strings, bg):
        # All good
        try:
            # Collects all wrapped lines
            all_lines = []
            for text, fg in strings:
                lines = self.wrap_text(text=text)
                for line in lines:
                    all_lines.append((line, fg))

            # Clips to available rows
            all_lines = all_lines[:self.rows]

            # Vertical centering accounting for spacing
            total_height = len(all_lines) * self.font_h + (len(all_lines) - 1) * self.line_spacing
            y_start = self.zone_y + (self.zone_h - total_height) // 2 + self.y_offset

            # Draws each line horizontally centered
            for i, (line, fg) in enumerate(all_lines):
                line_width = self.tft_display.write_len(self.font, line)
                x = (self.zone_w - line_width) // 2
                y = y_start + i * (self.font_h + self.line_spacing)
                self.tft_display.write(self.font, line, x, y, fg, bg)

        # Something went wrong, error
        except Exception as e:
            self.error_handler(e)

    # -- Draws current song playing
    def draw_current_song(self, song_name:str, author:str):
        # All good
        try:
            # Expects that JPG is ALREADY in MCU
            self.tft_display.jpg(self.image_file, 10, 10, self.image_speed["FAST"])
            self.clear_text_zone(self.display_colors["BLACK"])
            self.draw_text_zone(
                                    # - Text
                                    [
                                        (song_name, self.display_colors["WHITE"]),
                                        (author,    self.display_colors["GREEN"])
                                    ],
                                    # - Backlight
                                    self.display_colors["BLACK"]
                            )

        # Something went wrong, error
        except Exception as e:
            self.error_handler(e)

    # -- Draws a centered message on a full black background
    def draw_message(self, message:str, fg=None):
        # All good
        try:
            fg = self.display_colors["WHITE"] if fg is None else fg

            # Clears the entire display, not just the text zone
            self.tft_display.fill(self.display_colors["BLACK"])

            # Wraps message to fit full screen width
            lines = self.wrap_text(text=message, max_width=self.width)

            # Vertical centering across the whole screen
            total_height = len(lines) * self.font_h + (len(lines) - 1) * self.line_spacing
            y_start = (self.height - total_height) // 2

            # Draws each line horizontally centered
            for i, line in enumerate(lines):
                line_width = self.tft_display.write_len(self.font, line)
                x = (self.width - line_width) // 2
                y = y_start + i * (self.font_h + self.line_spacing)
                self.tft_display.write(self.font, line, x, y, fg, self.display_colors["BLACK"])

        # Something went wrong, error
        except Exception as e:
            self.error_handler(e)

if __name__ == "__main__":
    # ---------------------------- For testing ---------------------------- #
    tft_test = tft_handler(debug=True)
    tft_test.init_display()
    tft_test.draw_current_song(song_name="Song name", author="Author")
    tft_test.draw_message("This is an example of a long message check")

    