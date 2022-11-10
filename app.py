from flask import Flask, render_template, redirect, request
from spotify import Spotify

app = Flask(__name__)
spotify = Spotify()

app.secret_key = spotify.client_secret

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method=="POST":
        return create_playlist()
    
    return render_template('index.html', spotify=spotify, iframe="37i9dQZF1DWXMg4uP5o3dm")

@app.route('/spotify/authorize/')
def authorize():
    url = spotify.get_authorization_url()
    return redirect(url)

@app.route('/spotify/callback/')
def spotify_callback():
    spotify.get_user_authorization()
    genres = spotify.get_seed_genres()
    return render_template('index.html', spotify=spotify, genres=genres)

@app.route('/spotify/logout/')
def spotigfy_logout():
    spotify.logout()
    return redirect('/')

@app.route('/generate/', methods=['POST', 'GET'])
def create_playlist():
    # get form data
    playlist_name = request.form['playlistname']
    seed_genres = request.form['seedgenres']
    target_tempo = request.form['targettempo']

    # create playlist
    playlist_id = spotify.create_playlist(playlist_name)

    # get recommendation songs
    track_uris = spotify.get_tracks(seed_genres, target_tempo)

    # add songs to playlist
    spotify.add_playlist_tracks(playlist_id, track_uris)

    # get playlist embed
    iframe = spotify.get_embed(playlist_id)

    return render_template('index.html', spotify=spotify, iframe=iframe)

if __name__ == "__main__":
    app.run(debug=True)