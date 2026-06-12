import network
import usys
import ujson as json
import time
from util.debug import debug_print

# Connect to WLAN
def do_connect(timeout_seconds=15):
    
    # Credentials
    with open("credentials.json") as credentials_json:
        credentials = json.loads(credentials_json.read())
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    # WLAN is not connected
    if not wlan.isconnected():
        # Trying to connect to password
        debug_print('Connecting to network with given credentials...')
        wlan.disconnect()
        debug_print(credentials["wifi"]["ssid"])
        debug_print(credentials["wifi"]["password"])
        wlan.connect(credentials["wifi"]["ssid"], credentials["wifi"]["password"])
        
        # Record the start time in milliseconds
        start_time = time.ticks_ms()
        
        # WLAN tries to connect in the given timeout
        while not wlan.isconnected():
            if time.ticks_diff(time.ticks_ms(), start_time) > (timeout_seconds * 1000):
                debug_print("Timeout reached and could not connect. Something went wrong :(")
                wlan.active(False)
                return False
            time.sleep(0.5)
                
    # WLAN is fine, prints current network configuration
    debug_print('WLAN active: ', wlan.active())
    debug_print("IP address: ", wlan.ifconfig()[0])
    return True

if __name__ == "__main__":
    
    # Connect to internet with given credentials
    do_connect()