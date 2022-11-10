import requests, base64, json
from requests_oauthlib import OAuth2Session
from flask import session, request
from clientsecrets import client_id, client_secret
from requests.auth import HTTPBasicAuth

import os 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

REDIRECT_URI = "http://localhost:5000/spotify/callback/"
SCOPES = "user-library-read playlist-modify-public"
CONTENT_TYPE = 'application/x-www-form-urlencoded'
TOKEN_DATA = []
LOGOUT_URI = "https://accounts.spotify.com/logout"

class Spotify():
    # initializer
    def __init__(self):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = ""
        self.user_id = ""
        self.user_name = ""

    # request authentication using client credentials flow
    def authenticate_app(self):
        endpoint_url = "https://accounts.spotify.com/api/token"
        grant_type = "client_credentials"

        auth_str = f"{self.client_id}:{self.client_secret}"
        encoded_auth_str = base64.urlsafe_b64encode(auth_str.encode()).decode()

        response = requests.post(
                    url = endpoint_url, 
                    headers = {
                        "Content-Type": CONTENT_TYPE, 
                        "Authorization":f"Basic {encoded_auth_str}"
                        },
                    data = {'grant_type':grant_type})

        self.access_token = response.json()['access_token']

        return response.status_code
       
    # get authorization url
    def get_authorization_url(self):
        endpoint_url = "https://accounts.spotify.com/authorize?"

        # to avoid flask-login displaying the login error message
        session.pop("_flashes", None)

        # create authorization url
        oauth = OAuth2Session(self.client_id, scope = SCOPES, redirect_uri = REDIRECT_URI)
        authorization_url, state = oauth.authorization_url(endpoint_url)
        
        # state is used to prevent CSRF, keep this for later.
        session["oauth_state"] = state

        return authorization_url
    
    # get user authorization token
    def get_user_authorization(self):
        endpoint_url = "https://accounts.spotify.com/api/token"

        auth = HTTPBasicAuth(client_id, client_secret)
        
        # Fetch the access token
        oauth = OAuth2Session(self.client_id, scope = SCOPES, redirect_uri = REDIRECT_URI)

        token = oauth.fetch_token(
            endpoint_url,
            authorization_response=request.url,
            client_secret=self.client_secret)

        self.access_token = token["access_token"]

        # fetch a protected resource, i.e. user profile
        spotify_user = oauth.get('https://api.spotify.com/v1/me')
        # print(spotify_user.content)

        self.user_id = spotify_user.json()["id"]
        self.user_name = spotify_user.json()["display_name"]

    # get songs from recommendations based on filters
    def get_tracks(self, seed_genres, target_tempo):
        endpoint_url = "https://api.spotify.com/v1/recommendations"
        uris = []

        # query the recommendations 
        q = f'?seed_genres={seed_genres}&target_tempo={target_tempo}'

        response = requests.get(
                    url = f"{endpoint_url}{q}", 
                    headers = {
                        "Content-Type":"application/json", 
                        "Authorization":f"Bearer {self.access_token}"
                        })
        
        json_data = response.json()
        
        # print(response.status_code)
        # print(json_data)

        print('Recommended Songs:')
        for i,j in enumerate(json_data['tracks']):
            uris.append(j['uri'])
            print(f"{i+1}. {j['name']} by {j['artists'][0]['name']}")

        return uris

    # create new playlist
    def create_playlist(self, name):
        endpoint_url = f"https://api.spotify.com/v1/users/{self.user_id}/playlists"

        request_body = json.dumps({ "name": name })

        response = requests.post(
                    url = endpoint_url, 
                    data = request_body, 
                    headers = {
                        "Content-Type":"application/json", 
                        "Authorization":f"Bearer {self.access_token}"
                    })

        # return response to get playlist uri
        print(f"Playlist response: {response.json()}")
        return response.json()['id']
    
    # add songs to the new playlist
    def add_playlist_tracks(self, playlist_id, track_uris):
        # add tracks to the new playlist
        endpoint_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

        request_body = json.dumps({
                        "uris" : track_uris
                        })
                
        response = requests.post(url = endpoint_url, 
                                data = request_body, 
                                headers = {"Content-Type":"application/json","Authorization":f"Bearer {self.access_token}"})

        print(f"Add tracks to playlist reponse: {response.status_code}")
        print(response.json())

    # log out user
    def logout(self):
        self.access_token = ""
        self.user_id = ""
        response = requests.get(LOGOUT_URI)
        print(response)

    # get playlist embed
    def get_embed(self, playlist_id):
        base_url = "https://open.spotify.com/oembed"

        q = f"?url=https://open.spotify.com/playlist/{playlist_id}"

        response = requests.get(url = base_url + q, 
            headers = {"Content-Type":"application/json"})

        print(response.json()['html'])
        return response.json()['html']
    
    # get available seed genres
    def get_seed_genres(self):
        endpoint_url = "https://api.spotify.com/v1/recommendations/available-genre-seeds"

        response = requests.get(url = endpoint_url , 
            headers = {
                "Content-Type":"application/json",
                "Authorization":f"Bearer {self.access_token}"
                })

        print(response.json()['genres'])
        return response.json()['genres']
