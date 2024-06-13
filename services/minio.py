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
    replacements = {
        "!": "", "@": "", "#": "", "$": "", "%": "", "^": "", "&": "", "*": "", "(": "", ")": "",
        "[": "", "]": "", "{": "", "}": "", ";": "", ":": "", "\"": "", "'": "", ",": "", "<": "",
        ">": "", "/": "", "?": "", "`": "", "~": "",
        "é": "e", "è": "e", "ê": "e", "à": "a", "â": "a", "ù": "u", "ô": "o", "î": "i", "ç": "c", "ë": "e"
    }

    has_mp3_extension = filename.lower().endswith('.mp3')
    if has_mp3_extension:
        # Separate the extension and the rest of the filename
        base_name, extension = filename[:-4], filename[-4:]
    else:
        base_name, extension = filename, ''

    # Remove sequences of dots and slashes, remove spaces and replace disallowed characters
    base_name = base_name.replace("..", "").replace("//", "")
    sanitized_base_name = "".join(replacements.get(c, c) for c in base_name if c not in [' '] and (c.isalnum() or c in replacements))

    # Ensure only the last dot is kept in filenames ending with .mp3
    if has_mp3_extension:
        sanitized_base_name = sanitized_base_name.rstrip(".")

    sanitized = sanitized_base_name + extension
    if not sanitized:
        raise ValueError("Filename cannot be empty.")

    return sanitized