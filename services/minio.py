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
    allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_./"
    replacements = {
        " ": "_", "!": "", "@": "", "#": "", "$": "", "%": "", "^": "", "&": "", "*": "", "(": "", ")": "",
        "[": "", "]": "", "{": "", "}": "", ";": "", ":": "", "\"": "", "'": "", ",": "", ".": "", "<": "",
        ">": "", "/": "", "?": "", "`": "", "~": "",
        "é": "e", "è": "e", "ê": "e", "à": "a", "â": "a", "ù": "u", "ô": "o", "î": "i", "ç": "c", "ë": "e"
    }

    def replace_chars(s):
        return "".join(replacements.get(c, c) for c in s if c in allowed_chars or c == '.')

    # Check if the filename ends with '.mp3' and preserve the extension if it does
    extension = '.mp3' if filename.endswith('.mp3') else ''
    base_name = filename[:-4] if extension else filename

    sanitized_base_name = replace_chars(base_name)

    # Reconstruct the filename with the sanitized base name and extension, if any
    sanitized = sanitized_base_name + extension

    if not sanitized:
        raise ValueError("Filename cannot be empty.")

    return sanitized
