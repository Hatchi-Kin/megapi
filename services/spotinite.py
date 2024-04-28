# functions using the spotipy client and the cyanite API
import requests

from core.config import sp, DEFAULT_SETTINGS


def get_track_id(song_name, artist):
    # Search for the song
    results = sp.search(q=f'track:{song_name} artist:{artist}', type='track')
    # Get the Spotify ID of the first result
    spotify_id = results['tracks']['items'][0]['id']
    return spotify_id


def fetch_similar_tracks(spotify_id):
    url = "https://api.cyanite.ai/graphql"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEFAULT_SETTINGS.cyanite_token}",
    }

    query = """
    query SimilarTracksQuery($trackId: ID!) {
      spotifyTrack(id: $trackId) {
        __typename
        ... on Error {
          message
        }
        ... on Track {
          id
          similarTracks(target: { spotify: {} }, first: 15) {
            __typename
            ... on SimilarTracksError {
              code
              message
            }
            ... on SimilarTracksConnection {
              edges {
                node {
                  id
                }
              }
            }
          }
        }
      }
    }
    """
    # Define the variables
    variables = {
        "trackId": spotify_id,
    }

    response = requests.post(url, headers=headers, json={"query": query, "variables": variables})
    data = response.json()

    # Check if 'edges' key exists
    if 'edges' in data['data']['spotifyTrack']['similarTracks']:
        edges = data['data']['spotifyTrack']['similarTracks']['edges']
        # Extract the track IDs
        track_ids = [edge['node']['id'] for edge in edges]

        return track_ids
    else:
        return []
    

def get_track_info(track_id):
    # Get the track info
    track_info = sp.track(track_id)

    # Extract the track info
    track_name = track_info['name']
    artist_name = track_info['artists'][0]['name']
    album_name = track_info['album']['name']
    uri = track_info['uri']
    cover_image = track_info['album']['images'][0]['url']  # URL of the largest available cover image

    return {
        "Track Name": track_name,
        "Artist": artist_name,
        "Album": album_name,
        "URI": uri,
        "Cover Image": cover_image
    }