import base64
from urequests import post, get
import ujson as json

# -- CONSTANTS
CREDENTIALS_JSON = "credentials.json"

# Credentials
with open(CREDENTIALS_JSON) as credentials_json:
    credentials = json.loads(credentials_json.read())

# Credentials from JSON
CLIENT_ID = credentials["spotify"]["client_id"]
CLIENT_SECRET = credentials["spotify"]["client_secret"]
REDIRECT_URI = credentials["spotify"]["redirect_uri"]
AUTHENTICATION_CODE = credentials["spotify"]["authentication_code"]
ACCESS_TOKEN = credentials["spotify"]["access_token"]

# -- Spotify class for use
class Spotify:
    # -- Init class
    def __init__(self, client_id, client_secret, redirect_url,
                       authentication_code=None, access_token=None, scope="user-read-currently-playing"):
        # Use for authentication
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_url = redirect_url
        self.authentication_code = authentication_code
        self.access_token = access_token
        self.scope = scope
        self.item_response = None
    
    # -- Authentcation header
    def get_auth_header(self):
        auth_str = f"{self.client_id}:{self.client_secret}"
        return {"Authorization": f"Basic {base64.b64encode(auth_str.encode()).decode()}"}
    
    # -- Writes token into JSON file
    def write_token_json(self, token):
        # Reads json file
        with open(CREDENTIALS_JSON, "r") as f:
            data = json.load
        
        # Updates to new token
        data["spotify"]["access_token"] = token
        
        # Updates token into json
        with open(CREDENTIALS_JSON, "w") as f:
            json.dump(data, f)
    
    def refresh_access_token(self):
        url = "https://accounts.spotify.com/api/token"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = "grant_type=refresh_token&refresh_token=" + self.access_token
        print(self.get_auth_header())
        print(self.access_token)
        response = post(url, headers=self.get_auth_header(), data=data)
        return response
    
    
    # -- Gets the current play
    def get_current_play(self):
        # Do the API call to get the current call
        url = "https://api.spotify.com/v1/me/player/currently-playing?additional_types=track,episode"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = get(url, headers=headers)
        
        # Check the GET request
        if response.status_code == 200:		# Status is good and current play is sent
            item = response.json()
            print("Good 200")
            self.item_response = item
            return item
        elif response.status_code == 204:	# Nothing is being sent
            print("Good 204")
            return None
        else:								# Token expired or error
            print("Token expired or error")
            return False
    
    # -- Get url image (300x300)
    def get_current_play_image_url(self, item_response=None):
        
        # Uses item response by default
        if item_response is None:
            item_response = self.item_response
        
        # Returns the current url
        try:
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
                
            return url
        
        # Returns none if no url is in place
        except:
            print("Cannot get the image url")
            return None
    
    # -- Gets name
    def get_current_play_name(self, item_response=None):
        
        # Uses item response by default
        if item_response is None:
            item_response = self.item_response
        
        # Returns the name
        try:
            
            # Returns the item's name
            if item_response is not None:
                name = item_response["item"]["name"]
            
            # Returns none if not valid
            else:
                name = None
                
            return name
        
        # Returns none if no name is in place
        except:
            print("Cannot get the name")
            return None
        
    # -- Gets name
    def get_current_play_autor_or_show(self, item_response=None):
        
        # Uses item response by default
        if item_response is None:
            item_response = self.item_response
        
        # Returns the author or name's show
        try:
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
        
        # Returns none if no name is in place
        except:
            print("Cannot get the author or name's show")
            return None

if __name__ == "__main__":
    
    spotify_test = Spotify(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, AUTHENTICATION_CODE, ACCESS_TOKEN)
    print(spotify_test.get_current_play())


    #print(spotify_test.search_for_artist("Rammstein"))
    #print(spotify_test.get_current_track())

