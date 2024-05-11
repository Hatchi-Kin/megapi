import pytest
from unittest.mock import MagicMock, PropertyMock, patch

from services.minio import convert_artwork_to_base64, get_artwork, get_metadata_and_artwork


def test_convert_artwork_to_base64():
    # Create a mock artwork object
    artwork = MagicMock()
    artwork.data = b"test data"

    result = convert_artwork_to_base64(artwork)
    assert result == "dGVzdCBkYXRh"

@patch("services.minio.minio_client.get_object")
@patch("services.minio.music_tag.load_file")
def test_get_artwork(mock_load_file, mock_get_object):
    mock_artwork = MagicMock()
    mock_artwork.data = b"test data"
    mock_file = MagicMock()
    mock_file['artwork'].first = mock_artwork
    mock_load_file.return_value = mock_file

    mock_object = MagicMock()
    mock_object.read.return_value = b"test data"
    mock_get_object.return_value = mock_object

    result = get_artwork("test_bucket", "test_file")
    assert result is not None




@patch("services.minio.minio_client.get_object")
@patch("services.minio.music_tag.load_file")
def test_get_metadata_and_artwork(mock_load_file, mock_get_object):
    mock_artwork = MagicMock()
    mock_artwork.data = b"test data"
    
    mock_file = {'title': MagicMock(), 'artist': MagicMock(), 'album': MagicMock(), 'year': MagicMock(), 'tracknumber': MagicMock(), 'genre': MagicMock(), 'artwork': MagicMock()}
    mock_file['title'].first = "Test Title"
    mock_file['artist'].first = "Test Artist"
    mock_file['album'].first = "Test Album"
    mock_file['year'].first = "Test Year"
    mock_file['tracknumber'].first = "Test Track Number"
    mock_file['genre'].first = "Test Genre"
    mock_file['artwork'].first = mock_artwork
    mock_load_file.return_value = mock_file

    mock_object = MagicMock()
    mock_object.read.return_value = b"test data"
    mock_get_object.return_value = mock_object

    result = get_metadata_and_artwork("test_bucket", "test_file")

    assert result["title"] == "Test Title"
    assert result["artist"] == "Test Artist"
    assert result["album"] == "Test Album"
    assert result["year"] == "Test Year"
    assert result["tracknumber"] == "Test Track Number"
    assert result["genre"] == "Test Genre"
    assert "artwork" in result