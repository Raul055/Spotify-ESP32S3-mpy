import network
import socket
import time
import ujson as json
import machine

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

        # For AP
        self.ap = None
        self.s = None
        self.ip = None

        # Credentials path
        self.credentials = 'credentials.json'

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

    # -- Creates an ap portal for wifi credentials
    def create_ap_portal(self):
        try:
            # Creates local server
            self.ap = network.WLAN(network.AP_IF)
            self.ap.active(True)
            self.ap.config(essid="ESP32-Setup", password="") # No password

            # Socket
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind(('', 80))
            self.s.listen(1)

            # IP
            self.ip = self.ap.ifconfig()[0]
            print(f"AP started, portal listening on {self.ip}")
            return True

        # Something went wrong, error
        except Exception as e:
            self.error_handler(e)
    
    # -- Gets current IP
    def get_current_ip(self):
        # All good
        try:
            sta = network.WLAN(network.STA_IF)
            if sta.isconnected():
                return sta.ifconfig()[0]
            return None

        # Something went wrong, error
        except Exception as e:
            self.error_handler(e)

    # -- Loads page
    def load_page(self, path):
        with open(path) as f:
            return f.read()
    
    # -- Polls when a html request for wifi credentials is done
    def ap_portal_polling(self):
        # Flag
        wifi_credentials_sent = False
        
        # While True
        while not wifi_credentials_sent:
            # Connection
            conn, addr = self.s.accept()
            request = conn.recv(1024).decode()

            # - Gets SSID and Password
            if "GET /save" in request:
                # Check params
                params = request.split("GET /save?")[1].split(" ")[0]
                kv = dict(p.split("=") for p in params.split("&"))
                new_ssid = kv["ssid"]
                new_pass = kv["pass"]

                # Update credentials
                with open(self.credentials) as f:
                    config = json.load(f)
                config["wifi"]["ssid"] = new_ssid
                config["wifi"]["password"] = new_pass
                with open(self.credentials, "w") as f:
                    json.dump(config, f)

                # Close connection
                conn.send("HTTP/1.1 200 OK\r\n\r\nSaved. Rebooting...")
                conn.close()
                return True
            
            # - Loads page
            else:
                html = self.load_page("html/ap_page.html")
                conn.send("HTTP/1.1 200 OK\r\n\r\n" + html)
                conn.close()

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
    if wifi_test.do_connect():
        print(f"You are connected!")
    else:
        wifi_test.create_ap_portal()
        wifi_test.ap_portal_polling()