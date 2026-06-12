import gc
import util.tft_config as tft_config
import st7789
import util.Noto_sans as font
import util.spotify as spotify
import ujson as json
import util.image_file as image_file

import gc
gc.collect()
import micropython
micropython.mem_info()

# --- zone config ---
FONT_H  = 32
ZONE_W  = 320
ZONE_H  = 160
ZONE_Y  = 320
ROWS    = ZONE_H // FONT_H  # 4
Y_OFFSET = -8  # tweak if vertical centering is off
LINE_SPACING = 8  # extra pixels between lines, tweak to taste

# --- text wrapping ---
def wrap_text(display, font, text, max_width=ZONE_W):
    words = text.split(' ')
    lines = []
    current = ''
    for word in words:
        test = (current + ' ' + word).strip()
        if display.write_len(font, test) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            if display.write_len(font, word) > max_width:
                while display.write_len(font, word) > max_width:
                    i = len(word) - 1
                    while i > 0 and display.write_len(font, word[:i]) > max_width:
                        i -= 1
                    lines.append(word[:i])
                    word = word[i:]
            current = word
    if current:
        lines.append(current)
    return lines

# --- clear zone ---
def clear_text_zone(display, bg):
    display.fill_rect(0, ZONE_Y, ZONE_W, ZONE_H, bg)

# --- main draw function ---
def draw_text_zone(display, font, strings, bg):
    # first pass: collect all wrapped lines
    all_lines = []
    for text, fg in strings:
        lines = wrap_text(display, font, text)
        for line in lines:
            all_lines.append((line, fg))

    # clip to available rows
    all_lines = all_lines[:ROWS]

    # vertical centering accounting for spacing
    total_height = len(all_lines) * FONT_H + (len(all_lines) - 1) * LINE_SPACING
    y_start = ZONE_Y + (ZONE_H - total_height) // 2 + Y_OFFSET

    # draw each line horizontally centered
    for i, (line, fg) in enumerate(all_lines):
        line_width = display.write_len(font, line)
        x = (ZONE_W - line_width) // 2
        y = y_start + i * (FONT_H + LINE_SPACING)
        display.write(font, line, x, y, fg, bg)

gc.enable()
gc.collect()

# Credentials
with open("credentials.json") as credentials_json:
    credentials = json.loads(credentials_json.read())

# Credentials from JSON
client_id = credentials["spotify"]["client_id"]
client_secret = credentials["spotify"]["client_secret"]
redirect_uri = credentials["spotify"]["redirect_uri"]
access_token = credentials["spotify"]["access_token"]
spotify_class = spotify.Spotify(client_id, client_secret, redirect_uri, access_token=access_token)
gc.collect()
spotify_class.get_current_play()
image_url = spotify_class.get_current_play_image_url()
song_name = spotify_class.get_current_play_name()
author = spotify_class.get_current_play_autor_or_show()
print(image_url)
print(song_name)
print(author)
#song_name = items["item"]["name"]
#author = items["item"]["show"]["name"]

gc.collect()  
image_file.download_image(image_url, "cover.jpg")

# enable display and clear screen
tft_config.tft_display.init()
tft_config.tft_display.jpg("cover.jpg", 10, 10, True)
# 320, 352, tft_

clear_text_zone(tft_config.tft_display, st7789.BLACK)
draw_text_zone(tft_config.tft_display, font, [
    (song_name, st7789.WHITE),
    (author,        st7789.GREEN)
], st7789.BLACK)
print(2)