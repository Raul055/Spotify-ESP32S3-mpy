import urequests
import gc

def download_image(url, filename):
    res = urequests.get(url)
    if res.status_code == 200:
        with open(filename, "wb") as f:
            f.write(res.content)
        res.close()
        print("Download complete")
    else:
        print("Download failed")
    gc.collect()