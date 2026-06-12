from urequests import get
from gc import collect
from util.debug import debug_print

# -- Downloads image into the MCU
def download_image(url, filename):
    res = get(url)
    # Image was received successfully
    if res.status_code == 200:
        with open(filename, "wb") as f:
            f.write(res.content)
        res.close()
        debug_print("Download complete")
        return True
    # Something went wrong
    else:
        debug_print("Download failed")
        return False
    collect()