import requests
from core.config import sp, DEFAULT_SETTINGS


def get_track_id(song_name: str, artist: str) -> str:
    """
    Searches for a song on Spotify by name and artist and returns the Spotify ID of the first result.

    Args:
        song_name (str): The name of the song.
        artist (str): The name of the artist.

    Returns:
        str: The Spotify ID of the song.
    """
    results = sp.search(q=f'track:{song_name} artist:{artist}', type='track')
    spotify_id = results['tracks']['items'][0]['id']
    return spotify_id


def fetch_similar_tracks(spotify_id: str) -> list:
    """
    Fetches similar tracks from the Cyanite.ai API based on a given Spotify track ID.

    Args:
        spotify_id (str): The Spotify ID of the track for which similar tracks are to be found.

    Returns:
        list: A list of Spotify IDs for tracks similar to the given track.
    """
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
    variables = {"trackId": spotify_id}
    response = requests.post(url, headers=headers, json={"query": query, "variables": variables})
    data = response.json()

    if 'edges' in data['data']['spotifyTrack']['similarTracks']:
        edges = data['data']['spotifyTrack']['similarTracks']['edges']
        track_ids = [edge['node']['id'] for edge in edges]
        return track_ids
    else:
        return []


def get_track_info(track_id: str) -> dict:
    """
    Retrieves detailed information about a track from Spotify using its Spotify ID.

    Args:
        track_id (str): The Spotify ID of the track.

    Returns:
        dict: A dictionary containing detailed information about the track, including its name, artist, album, URI, and cover image URL.
    """
    track_info = sp.track(track_id)
    track_name = track_info['name']
    artist_name = track_info['artists'][0]['name']
    album_name = track_info['album']['name']
    uri = track_info['uri']
    cover_image = track_info['album']['images'][0]['url']
    return {
        "Track Name": track_name,
        "Artist": artist_name,
        "Album": album_name,
        "URI": uri,
        "Cover Image": cover_image
    }
