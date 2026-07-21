import requests
import webbrowser
from urllib.parse import urlencode, urlparse, parse_qs
import os
from pathlib import Path
from dotenv import load_dotenv

class spotify_handler():
    def __init__(self, debug=True):

        # Info from .env
        self.env_path = Path(".env")
        self.env_keys = ["CLIENT_ID", "CLIENT_SECRET", "REDIRECT_URI"]
        self.client_id = None
        self.client_secret = None
        self.redirect_uri = None
        
        # Scope for spotify API
        self.scope = "user-read-currently-playing"
        
        # Debug flag
        self.debug = debug

        # Tokens
        self.access_token = None
        self.refresh_token = None

    # -- Debugging print for debug flag
    def debug_print(self, *args):
        if self.debug:
            print(*args)


    # -- Handles ENV variables from .env file
    def env_handler(self):

        # Env does not exist, create one
        if not self.env_path.exists():
            self.debug_print("No env file found, creating one...")
            
            # Ask for inputs of each env key
            env_dict = {}  # Placeholder
            for key in self.env_keys:
                value = input(f"Enter {key}: ").strip()
                env_dict[key] = value

            # Creates the .env file and inputs all the env keys
            with open(self.env_path, "w") as f:
                for key, value in env_dict.items():
                    f.write(f"{key}={value}\n")
            
            self.debug_print(".env created!")
        
        # Loads .env file
        load_dotenv(self.env_path)

        # Updates attributes of the class
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.redirect_uri = os.getenv("REDIRECT_URI")

    # -- Opens authenticator URL local browser
    def auth_url(self):
        # Parameters
        params = urlencode({
                                "client_id":     self.client_id,
                                "response_type": "code",
                                "redirect_uri":  self.redirect_uri,
                                "scope":         self.scope,
                           })

        # Opens authorization url with given parameters
        webbrowser.open("https://accounts.spotify.com/authorize?" + params)

    # -- Gets token from authenticator URL
    def get_tokens(self):
        redirected = input("Paste the full redirect URL here: ").strip()
        code = parse_qs(urlparse(redirected).query)["code"][0]

        # Get tokens from code
        resp = requests.post(
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type":   "authorization_code",
                "code":         code,
                "redirect_uri": self.redirect_uri,
            },
            auth=(self.client_id, self.client_secret),
        )

        # Assigns each token
        tokens = resp.json()
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens["refresh_token"]

        # Prints tokens if enabled
        self.debug_print(f"Access token: {self.access_token}")
        self.debug_print(f"Refresh token: {self.refresh_token}")

    # -- Main workflow
    def main(self):

        # Handles .env
        self.env_handler()

        # Authenticator URL
        self.auth_url()

        # Gets tokens
        self.get_tokens()

if __name__ == "__main__":
    spotify = spotify_handler()
    spotify.main()