import base64
from urequests import post, get
import ujson as json

# -- Spotify class for use
class spotify_client:
    # -- Init class
    def __init__(self,
                        client_id=None,
                        client_secret=None,
                        redirect_url=None,
                        access_token=None,
                        refresh_token =None,
                        scope="user-read-currently-playing",
                        debug : bool = False
                ):
                
        # Use for authentication in spotify API
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_url = redirect_url
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.scope = scope

        # For debugging
        self.debug = debug

        # Item response
        self.item_response = None

        # Image url & name
        self.image_url = None
        self.image_filename = "cover.jpg"

    # -- Debug print
    def debug_print(self, *args):
        if self.debug:
            print(*args)

    # -- Error handler
    def error_handler(self, e):
        if self.debug:
            print(f"Error: {e}")

    # -- Authentcation header
    def get_auth_header(self):
        auth_str = f"{self.client_id}:{self.client_secret}"
        return {"Authorization": f"Basic {base64.b64encode(auth_str.encode()).decode()}"}
    
    # -- Refresh access token, retunrns true if token refreshed, else false
    def refresh_access_token(self):
        # All good
        try:
            # URL for token update
            url = "https://accounts.spotify.com/api/token"
            
            # For API call, use refresh token
            auth_header = self.get_auth_header()
            headers = {
                        "Authorization": auth_header["Authorization"],
                        "Content-Type": "application/x-www-form-urlencoded"
                    }

            data = f"grant_type=refresh_token&refresh_token={self.refresh_token}" 
            
            # API response
            response = post(url, headers=headers, data=data)
            
            # Response is good, token updated
            if response.status_code == 200:
                new_token = response.json()["access_token"]
                self.access_token = new_token
                self.debug_print("New token obtained!")
                return True
            
            # Response is bad, falied to refreshed token
            else:
                self.debug_print(f"Failed to refresh token: {response.status_code}")
                return False
        
        # Something went wrong, error
        except Exception as e:
            self.error_handler(e)
    
    # -- Gets the current play
    def get_current_play(self):
        # All good
        try:
            # Do the API call to get the current call
            url = "https://api.spotify.com/v1/me/player/currently-playing?additional_types=track,episode"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = get(url, headers=headers)
            
            # Check the GET request
            if response.status_code == 200:		# Status is good and current play is sent
                item = response.json()
                self.debug_print("Good 200: something is playing")
                self.item_response = item
                return item
            elif response.status_code == 204:	# Nothing is being sent
                self.debug_print("Good 204: nothing is being sent")
                return None
            else:								# Token expired or error
                self.debug_print("Token expired or error")
                return False
        
        # Something went wrong, error
        except Exception as e:
            self.error_handler(e)
    
    # -- Get url image (300x300)
    def get_current_play_image_url(self, item_response=None):
        # All good
        try:
            # Uses item response by default
            if item_response is None:
                item_response = self.item_response
            
            # Default if None
            if item_response is None:
                return None

            # Returns the current url
            item = item_response.get("item", {})
            
            # Url when the current play is a show
            if item.get("show") is not None:
                url = item_response["item"]["images"][1]["url"]
            
            # Url when the current play is a song
            elif item.get("album") is not None:
                url = item_response["item"]["album"]["images"][1]["url"]
            
            # Returns none if not valid
            else:
                url = None

            self.image_url = url
            return url
            
        # Something went wrong, error
        except Exception as e:
            self.error_handler(e)
    
    # -- Gets song/show name
    def get_current_play_name(self, item_response=None):
        # All good
        try:
            # Uses item response by default
            if item_response is None:
                item_response = self.item_response
            
            # Default if None
            if item_response is None:
                return None
            
            # Returns the item's name
            if item_response is not None:
                name = item_response["item"]["name"]
            
            # Returns none if not valid
            else:
                name = None
                
            return name
        
        # Something went wrong, error
        except Exception as e:
            self.error_handler(e)
        
    # -- Gets author/show
    def get_current_play_autor_or_show(self, item_response=None):
        # All good
        try:
            # Uses item response by default
            if item_response is None:
                item_response = self.item_response
        
            # Default if None
            if item_response is None:
                return None

            # Returns the author or name's show
            item = item_response.get("item", {})
            
            # Response when the current play is a show
            if item.get("show") is not None:
                response = item_response["item"]["show"]["name"]
            
            # Response when the current play is a song
            elif item.get("album") is not None:
                response = item_response["item"]["artists"][0]["name"]	# Gets the first artist
            
            # Returns none if not valid
            else:
                response = None
                
            return response
        
        # Something went wrong, error
        except Exception as e:
            self.error_handler(e)

    # -- Downloads image into the MCU
    def download_cover_image(self, url=None, filename=None):
        # All good
        try:
            # Uses classes attributes as default
            url = self.image_url if url is None else url
            filename = self.image_filename if filename is None else filename

            res = get(url)
            # Image was received successfully
            if res.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(res.content)
                res.close()
                self.debug_print("Download complete")
                return True

            # Something went wrong with request
            else:
                self.debug_print("Download failed :(")
                return False

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
    CLIENT_ID = credentials["spotify"]["client_id"]
    CLIENT_SECRET = credentials["spotify"]["client_secret"]
    REDIRECT_URI = credentials["spotify"]["redirect_uri"]
    REFRESH_TOKEN = credentials["spotify"]["refresh_token"]
    ACCESS_TOKEN = credentials["spotify"]["access_token"]
    
    # Spotify client
    spotify_test = spotify_client(
                                    client_id=CLIENT_ID,
                                    client_secret=CLIENT_SECRET,
                                    redirect_url=REDIRECT_URI,
                                    refresh_token=REFRESH_TOKEN,
                                    access_token=ACCESS_TOKEN,
                                    debug=True
                                 )
    
    # Saves for tests
    print(f"Refresh token: {spotify_test.refresh_access_token()}")
    print(f"Get current play: {spotify_test.get_current_play()}")
    print(f"Get current image url: {spotify_test.get_current_play_image_url()}")
    print(f"Get current play name: {spotify_test.get_current_play_name()}")
    print(f"Get current play author or show: {spotify_test.get_current_play_autor_or_show()}")
    print(f"Image was downloaded: {spotify_test.download_cover_image()}")