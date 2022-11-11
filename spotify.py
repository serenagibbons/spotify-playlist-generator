import requests, json, base64

# request authentication using client credentials flow
def authenticate_app(client_id, client_secret):
    auth_str = f"{client_id}:{client_secret}"
    encoded_auth_str = base64.urlsafe_b64encode(auth_str.encode()).decode()

    response = requests.post(
                url = "https://accounts.spotify.com/api/token", 
                headers = {
                    "Content-Type": 'application/x-www-form-urlencoded', 
                    "Authorization":f"Basic {encoded_auth_str}"
                },
                data = {'grant_type': 'client_credentials'})

    return response

# get songs from recommendations based on filters
def get_recommendations(seed_genres, target_tempo, access_token):
    endpoint_url = "https://api.spotify.com/v1/recommendations"

    # query the recommendations 
    q = f'?seed_genres={seed_genres}&target_tempo={target_tempo}'

    response = requests.get(
                url = f"{endpoint_url}{q}", 
                headers = {
                    "Content-Type":"application/json", 
                    "Authorization":f"Bearer {access_token}"
                })
    
    return response

# get oEmbed
def get_oEmbed(type, id):
    endpoint_url = "https://open.spotify.com/oembed"

    q = f"?url=https://open.spotify.com/{type}/{id}"

    response = requests.get(
                url = f"{endpoint_url}{q}", 
                headers = {
                    "Content-Type":"application/json"
                })

    return response

# get available seed genres
def get_seed_genres(access_token):
    endpoint_url = "https://api.spotify.com/v1/recommendations/available-genre-seeds"

    response = requests.get(url = endpoint_url , 
                headers = {
                    "Content-Type":"application/json",
                    "Authorization":f"Bearer {access_token}"
                })

    return response

# create new playlist
def create_playlist(playlist_name, user_id, access_token):
    endpoint_url = f"https://api.spotify.com/v1/users/{user_id}/playlists"

    request_body = json.dumps({ "name" : playlist_name })

    response = requests.post(
                url = endpoint_url, 
                data = request_body, 
                headers = {
                    "Content-Type":"application/json", 
                    "Authorization":f"Bearer {access_token}"
                })

    # return playlist response
    return response

# add songs to the a playlist
def add_playlist_tracks(playlist_id, track_uris, access_token):
    endpoint_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    request_body = json.dumps({ "uris" : track_uris })
            
    response = requests.post(
                url = endpoint_url, 
                data = request_body, 
                headers = {
                    "Content-Type":"application/json",
                    "Authorization":f"Bearer {access_token}"
                })

    return response

def delete_playlist(playlist_id, access_token):
    endpoint_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/followers"

    response = requests.delete(url = endpoint_url, 
                headers = {
                    "Content-Type":"application/json",
                    "Authorization":f"Bearer {access_token}"
                })

    return response
