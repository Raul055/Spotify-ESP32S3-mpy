from util.tft_handler import tft_handler
from util.spotify_client import spotify_client
from util.wifi_handler import wifi_handler
import ujson as json
import time

# -- Class that handles all process
class process_handler:
    # -- Init class
    def __init__(self,
                        debug=False
                ):

        # ------------------------ Handlers placeholders ------------------------ #
        self.tft_handler = None
        self.spotify_client = None
        self.wifi_handler = None

        # ------------------------ Credentials ------------------------ #
        # -- For wifi
        self.wifi_ssid = None
        self.wifi_password = None
        # -- For spotify API
        self.spotify_client_id = None
        self.spotify_client_secret = None
        self.spotify_redirect_uri = None
        self.spotify_refresh_token = None
        # -- json file credentials
        self.credentials_json = "credentials.json"

        # ------------------------ Flags ------------------------ #
        self.nothing_playing_display_flag = None
        self.debug = debug

    # -- Debug print
    def debug_print(self, *args):
        if self.debug:
            print(*args)

    # -- Error handler
    def error_handler(self, e):
        if self.debug:
            print(f"Error: {e}")    

    # -- Reads credentials from json files
    def read_credentials(self):
        # All good
        try:
            # Open credentials
            with open(self.credentials_json) as credentials_json:
                credentials = json.loads(credentials_json.read())
        
            # Pass credentials to class attributes
            self.wifi_ssid = credentials["wifi"]["ssid"]
            self.wifi_password = credentials["wifi"]["password"]
            self.spotify_client_id = credentials["spotify"]["client_id"]
            self.spotify_client_secret = credentials["spotify"]["client_secret"]
            self.spotify_redirect_uri = credentials["spotify"]["redirect_uri"]
            self.spotify_refresh_token = credentials["spotify"]["refresh_token"]
            return True

        # Something went wrong, error
        except Exception as e:
            self.error_handler(e)
            return False

    # -- Creates handlers
    def create_handlers(self):
        # All good
        try:
            # Creates all three classes
            self.wifi_handler = wifi_handler(
                                                ssid=self.wifi_ssid,
                                                password=self.wifi_password,
                                                debug=self.debug
                                            )
            self.spotify_client = spotify_client(
                                                    client_id=self.spotify_client_id,
                                                    client_secret=self.spotify_client_secret,
                                                    redirect_url=self.spotify_redirect_uri,
                                                    refresh_token=self.spotify_refresh_token,
                                                    debug=self.debug
                                                )
            self.tft_handler = tft_handler(debug=self.debug)
            self.tft_handler.init_display()
            return True
        
        # Something went wrong, error
        except Exception as e:
            self.error_handler(e)
            return False

    # -- Connect to wifi
    def connect_to_wifi(self):
        # All good
        try:
            # Connecting to internet message
            self.tft_handler.draw_message("Connecting to internet...")
            time.sleep(1)

            # Checks if connection was successfull
            if self.wifi_handler.do_connect():
                self.tft_handler.draw_message("You are connected to the internet!")
                time.sleep(2)
                return True

            # Cannot connect to wifi
            else:
                self.tft_handler.draw_message("Cannot connect to the internet, sorry :(")
                time.sleep(2)
                return False
            
        # Something went wrong, error
        except Exception as e:
            self.error_handler(e)
            return False

    # -- Gets current song
    def get_current_song(self):
        # All good
        try:
            # Get status, name and author of current play!
            status, name, author = self.spotify_client.get_current_play_handler()

            # Song changed, update
            if status == "CHANGED":
                self.nothing_playing_display_flag = False
                self.tft_handler.draw_current_song(song_name=name, author=author)

            # There is nothing being played
            elif status == "NO_PLAY":
                if self.nothing_playing_display_flag != True:
                    self.tft_handler.draw_message("Nothing is being played...")
                self.nothing_playing_display_flag = True

            # Song remains the same, do nothing
            elif status == "UNCHANGED":
                pass

            # Unsupported state, error
            else:
                self.tft_handler.draw_message("Something went wrong :(")
            
        # Something went wrong, error
        except Exception as e:
            self.error_handler(e)
            return False
            
    # -- Main handler
    def main(self):

        # First read credentials
        if self.read_credentials():
            # Then, create the handlers
            if self.create_handlers():
                # Connect to internet
                if self.connect_to_wifi():
                    # All good, get spotify
                    while True:
                        self.get_current_song()
                        time.sleep(2)
                else:
                    # Internet error
                    self.debug_print("Could not connect to wifi, sorry :(")
                    self.tft_handler.draw_message("No connection, check WLAN or credentials")
            else:
                # Handler error
                self.debug_print("Could not create handlers, sorry :(")
        else:
            # Credentials error
            self.debug_print("Could not read credentials, sorry :(")

if __name__ == "__main__":
    process_test = process_handler(debug=True)
    process_test.main()