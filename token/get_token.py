# run this on your PC once: python get_refresh_token.py
import requests
import webbrowser
from urllib.parse import urlencode, urlparse, parse_qs

CLIENT_ID     = "8a57f6008e1245dca843b570eecdd337"
CLIENT_SECRET = "fee1565ebfdd4b30a2f6904efdb683d1"
REDIRECT_URI  = "https://example.org/callback"
SCOPE         = "user-read-currently-playing"

# Step 1: open auth URL in browser
params = urlencode({
    "client_id":     CLIENT_ID,
    "response_type": "code",
    "redirect_uri":  REDIRECT_URI,
    "scope":         SCOPE,
})
webbrowser.open("https://accounts.spotify.com/authorize?" + params)

# Step 2: paste the full redirect URL after you approve
redirected = input("Paste the full redirect URL here: ").strip()
code = parse_qs(urlparse(redirected).query)["code"][0]

# Step 3: exchange code for tokens
resp = requests.post(
    "https://accounts.spotify.com/api/token",
    data={
        "grant_type":   "authorization_code",
        "code":         code,
        "redirect_uri": REDIRECT_URI,
    },
    auth=(CLIENT_ID, CLIENT_SECRET),
)

tokens = resp.json()
print(tokens)  # add this line
print("Access token:  ", tokens["access_token"])
print("Refresh token: ", tokens["refresh_token"])