import json
from flask import Flask, request, redirect, g, render_template
import requests
from urllib.parse import quote
import config as CONFIG

# Authentication Steps, paramaters, and responses are defined at https://developer.spotify.com/web-api/authorization-guide/
# Visit this url to see all the steps, parameters, and expected response.
app = Flask(__name__)

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": CONFIG.REDIRECT_URI,
    "scope": CONFIG.SCOPE,
    "client_id": CONFIG.CLIENT_ID
}

@app.route("/")
def index():
    # Auth Step 1: Authorization
    query_parameters = []
    for key, val in auth_query_parameters.items():
        query_parameters.append("{}={}".format(key, quote(val))) 
    url_args = "&".join(query_parameters)
    auth_url = "{}/?{}".format(CONFIG.SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)


@app.route("/callback/")
def callback():
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": CONFIG.REDIRECT_URI,
        'client_id': CONFIG.CLIENT_ID,
        'client_secret': CONFIG.CLIENT_SECRET,
    }
    post_request = requests.post(CONFIG.SPOTIFY_TOKEN_URL, data=code_payload)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Auth Step 6: Use the access token to access Spotify API
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}

    # Get profile data
    user_profile_api_endpoint = "{}/me".format(CONFIG.SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    profile_data = json.loads(profile_response.text)

    # Get user playlist data
    playlist_api_endpoint = "{}/playlists".format(profile_data["href"])
    playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
    playlist_data = json.loads(playlists_response.text)

    # Combine profile and playlist data to display
    display_arr = [profile_data] + playlist_data["items"]
    return render_template("index.html", sorted_array=display_arr)


if __name__ == "__main__":
    app.run(debug=True, port=CONFIG.PORT)
