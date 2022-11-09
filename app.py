from flask import Flask, render_template, redirect
from spotify import Spotify

app = Flask(__name__)
spotify = Spotify()

app.secret_key = spotify.client_secret

@app.route('/')
def index():
    return render_template('index.html', spotify=spotify, iframe="37i9dQZF1DWXMg4uP5o3dm")

@app.route('/spotify/authorize/')
def authorize():
    url = spotify.get_authorization_url()
    return redirect(url)

@app.route('/spotify/callback/')
def spotify_callback():
    spotify.get_user_authorization()
    return redirect('/')

@app.route('/spotify/logout/')
def spotigfy_logout():
    spotify.logout()
    return redirect('/')

@app.route('/generate/', methods=['POST', 'GET'])
def create_playlist():
    playlist_id = spotify.create_playlist()
    track_uris = spotify.get_tracks()

    spotify.add_playlist_tracks(playlist_id=playlist_id, track_uris=track_uris)

    iframe = spotify.get_embed(playlist_id=playlist_id)

    return render_template('index.html', spotify=spotify, iframe=iframe)

if __name__ == "__main__":
    app.run(debug=True)