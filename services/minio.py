import os
import tempfile
import base64
import music_tag

from core.config import minio_client


def convert_artwork_to_base64(artwork):
    if artwork is not None:
        return base64.b64encode(artwork.data).decode('utf-8')
    return None


def get_artwork(bucket_name: str, file_name: str):
    # Create a temporary file then download the file from MinIO
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        data = minio_client.get_object(bucket_name, file_name)
        temp_file.write(data.read())

    try:
        # Load the file with music_tag
        f = music_tag.load_file(temp_file.name)
        if f['artwork'] and f['artwork'].first is not None:
            return convert_artwork_to_base64(f['artwork'].first)
        return None
    finally:
        # Delete the temporary file
        os.unlink(temp_file.name)


def get_metadata_and_artwork(bucket_name: str, file_name: str):
    # Create a temporary file then download the file from MinIO
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        data = minio_client.get_object(bucket_name, file_name)
        temp_file.write(data.read())

    try:
        # Load the file with music_tag
        f = music_tag.load_file(temp_file.name)
        metadata = {
            "filepath": file_name,
            "filesize": round(os.path.getsize(temp_file.name) / 1024 / 1024, 2),
            "title": f['title'].first or "Unknown Title",
            "artist": f['artist'].first or "Unknown Artist",
            "album": f['album'].first or "Unknown Album",
            "year": f['year'].first or "Unknown Year",
            "tracknumber": f['tracknumber'].first or "Unknown Track Number",
            "genre": f['genre'].first or "Unknown Genre",
        }

        # Add artwork to the metadata if it exists
        if f['artwork'] and f['artwork'].first is not None:
            metadata["artwork"] = convert_artwork_to_base64(f['artwork'].first)

        return metadata
    finally:
        # Delete the temporary file
        os.unlink(temp_file.name)


def sanitize_filename(filename):
    # Define allowed characters
    allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
    # Replace spaces with underscores
    sanitized = filename.replace(" ", "_")
    # Remove any character not in the allowed set
    sanitized = "".join(char for char in sanitized if char in allowed_chars)
    return sanitized