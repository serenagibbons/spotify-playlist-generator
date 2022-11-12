from requests_oauthlib import OAuth2Session
from flask import Flask, redirect, render_template, url_for, request, session
from flask.json import jsonify
from flask_session import Session
from time import time
from dotenv import load_dotenv
import os
import spotify
import webbrowser

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

load_dotenv()
client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']

authorization_base_url = 'https://accounts.spotify.com/authorize?'
token_url = 'https://accounts.spotify.com/api/token'
logout_url = 'https://accounts.spotify.com/logout'
redirect_uri = 'callback'
scope = 'user-library-read playlist-modify-public'
genres = ''

@app.route('/', methods=['GET'])
def index():
    try:
        token=session['oauth_token']
        spotify_oauth = OAuth2Session(client_id, token=token)
        user = spotify_oauth.get('https://api.spotify.com/v1/me').json()
        session['user'] = user
        return render_template('index.html', genres=genres)
    except:
        return render_template('index.html', genres=genres)

@app.route('/authorize/')
def authorize():
    # redirect the user to the OAuth provider (Spotify)
    spotify_oauth = OAuth2Session(client_id, scope=scope, redirect_uri=url_for(redirect_uri, _external=True))
    authorization_url, state = spotify_oauth.authorization_url(authorization_base_url)

    # state is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route('/callback/', methods=["GET"])
def callback():
    spotify_oauth = OAuth2Session(client_id, redirect_uri=url_for(redirect_uri, _external=True), state=session['oauth_state'])
    token = spotify_oauth.fetch_token(token_url, client_secret=client_secret, 
        authorization_response=request.url)
    
    # save token
    session['oauth_token'] = token

    return redirect('/')

@app.route("/automatic_refresh/", methods=["GET"])
def automatic_refresh():
    # refresh OAuth 2 token using a refresh token
    token = session['oauth_token']

    # trigger an automatic refresh by forcing token expiration
    token['expires_at'] = time() - 10

    extra = {
        'client_id': client_id,
        'client_secret': client_secret,
    }

    def token_updater(token):
        session['oauth_token'] = token

    spotify_oauth = OAuth2Session(client_id,
        token=token,
        auto_refresh_kwargs=extra,
        auto_refresh_url=token_url,
        token_updater=token_updater)

    # trigger the automatic refresh
    jsonify(spotify_oauth.get('https://api.spotify.com/v1/me').json())
    return jsonify(session['oauth_token'])

@app.route("/manual_refresh/", methods=["GET"])
def manual_refresh():
    # refresh an OAuth 2 token using a refresh token
    token = session['oauth_token']

    extra = {
        'client_id': client_id,
        'client_secret': client_secret,
    }

    spotify_oauth = OAuth2Session(client_id, token=token)
    session['oauth_token'] = spotify_oauth.refresh_token(token_url, **extra)
    return jsonify(session['oauth_token'])

@app.route('/logout/')
def spotify_logout():
    session.clear()
    webbrowser.open(url=logout_url)
    return redirect('/')

@app.route('/refresh/')
def refresh():
    return redirect('/')

@app.route('/', methods=['POST'])
def generate_playlist():
    # get form data
    playlist_name = request.form['playlistname']
    seed_genres = request.form['seedgenres']
    target_tempo = request.form['targettempo']

    # create playlist
    playlist_id = spotify.create_playlist(playlist_name, 
        user_id=session['user']['id'],
        access_token=session['oauth_token']['access_token']
        ).json()['id']

    # get recommendation songs
    tracks = spotify.get_recommendations(seed_genres, 
        target_tempo, 
        access_token=session['oauth_token']['access_token']
        ).json()['tracks']

    track_uris = []
    for track in tracks:
        track_uris.append(track['uri'])

    # add songs to playlist
    spotify.add_playlist_tracks(playlist_id, 
        track_uris,
        access_token=session['oauth_token']['access_token'])

    # get playlist embed
    iframe = spotify.get_oEmbed(type="playlist", id=playlist_id).json()['html']

    return render_template('index.html', iframe=iframe, playlist_id=playlist_id)

@app.route('/delete/<playlist_id>')
def delete_playlist(playlist_id):
    spotify.delete_playlist(playlist_id=playlist_id, access_token=session['oauth_token']['access_token'])
    return redirect('/')

if __name__ == "__main__":    
    response = spotify.authenticate_app(client_id, client_secret)
    genres = spotify.get_seed_genres(response.json()['access_token']).json()['genres']
    
    app.secret_key = os.urandom(24)
    app.run(debug=True)