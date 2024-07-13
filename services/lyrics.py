import requests
import urllib.parse


def fetch_lyrics(artist: str, title: str) -> str:
    """
    Fetches the lyrics for a given song by artist and title.

    Args:
        artist (str): The name of the artist.
        title (str): The title of the song.

    Returns:
        str: The lyrics of the song if found, otherwise a message indicating no lyrics were found.
    """
    encoded_artist = urllib.parse.quote(artist)
    encoded_song = urllib.parse.quote(title)
    try:
        response = requests.get(f"https://api.lyrics.ovh/v1/{encoded_artist}/{encoded_song}", timeout=7)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return "No lyrics found for this song."
    
    json_response = response.json()
    if 'error' in json_response:
        return "No lyrics found for this song."
    return json_response['lyrics']
