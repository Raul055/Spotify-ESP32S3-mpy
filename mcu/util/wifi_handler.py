import network
import time
import ujson as json

# -- Wifi client for connect to WLAN
class wifi_handler:
    def __init__(self,
                        ssid=None,
                        password=None,
                        debug: bool = False
                ):

        # Credentials for WLAN
        self.ssid = ssid
        self.password = password

        # For debugging
        self.debug = debug
    
    # -- Debug print
    def debug_print(self, *args):
        if self.debug:
            print(*args)
    
    # -- Error handler
    def error_handler(self, e):
        if self.debug:
            print(f"Error: {e}")

    # -- Connect to WLAN
    def do_connect(self, timeout_seconds=15):
        # All good
        try:
            # Check for WLAN
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            
            # WLAN is not connected
            if not wlan.isconnected():
                # Trying to connect to password
                self.debug_print('Connecting to network with given credentials...')
                wlan.disconnect()
                self.debug_print(f"SSID: {self.ssid}")
                self.debug_print(f"Password: {self.password}")
                wlan.connect(self.ssid, self.password)
                
                # Record the start time in milliseconds
                start_time = time.ticks_ms()
                
                # WLAN tries to connect in the given timeout
                while not wlan.isconnected():
                    if time.ticks_diff(time.ticks_ms(), start_time) > (timeout_seconds * 1000):
                        self.debug_print("Timeout reached and could not connect. Something went wrong :(")
                        wlan.active(False)
                        return False
                    time.sleep(0.5)
                        
            # WLAN is fine, prints current network configuration
            self.debug_print('WLAN active: ', wlan.active())
            self.debug_print("IP address: ", wlan.ifconfig()[0])
            return True

        # Something went wrong, error
        except Exception as e:
            self.error_handler(e)

if __name__ == "__main__":
    
    # ---------------------------- For testing ---------------------------- #
    # CONSTANTS
    CREDENTIALS_JSON = "credentials.json"

    # Credentials
    with open(CREDENTIALS_JSON) as credentials_json:
        credentials = json.loads(credentials_json.read())

    # Credentials from JSON
    SSID = credentials["wifi"]["ssid"]
    PASSWORD = credentials["wifi"]["password"]

    # Wifi client
    wifi_test = wifi_handler(
                            ssid=SSID,
                            password=PASSWORD,
                            debug=True
                      )

    # Check if wifi is connected
    print(f"Connected: {wifi_test.do_connect()}")