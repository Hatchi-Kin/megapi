import os
import tempfile
import pickle
import base64
import zipfile

import music_tag
from minio.error import S3Error

from core.extract_openl3_embeddings import EmbeddingsOpenL3
from core.config import minio_client, DEFAULT_SETTINGS


def load_model_from_minio():
    """
    Loads a model from MinIO into a temporary file and returns the model.

    Returns:
        EmbeddingsOpenL3: The loaded model.
    """
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        response = minio_client.get_object(DEFAULT_SETTINGS.minio_openl3_bucket_name, DEFAULT_SETTINGS.minio_openl3_file_name)
        temp_file.write(response.read())
        temp_file.flush()
        embedding_512_model = EmbeddingsOpenL3(graph_path=temp_file.name)
    return embedding_512_model


def get_temp_file_from_minio(file_name: str) -> str:
    """
    Retrieves a file from MinIO and writes it to a temporary file.

    Args:
        file_name (str): The name of the file to retrieve.

    Returns:
        str: The path to the temporary file.
    """
    try:
        # Determine the bucket name based on the file name
        bucket_name = DEFAULT_SETTINGS.minio_bucket_name if file_name.startswith("MegaSet/") else DEFAULT_SETTINGS.minio_temp_bucket_name
        # Retrieve the file from MinIO
        response = minio_client.get_object(bucket_name, file_name)

        # Write the file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            for data in response.stream(32 * 1024):
                temp_file.write(data)
        return temp_file.name
    
    except Exception as e:
        print(f"Error retrieving file from MinIO: {e}")
        raise


def delete_temp_file(temp_file_path: str):
    """
    Deletes a temporary file.

    Args:
        temp_file_path (str): The path to the temporary file to delete.
    """
    os.unlink(temp_file_path)


def convert_artwork_to_base64(artwork):
    """
    Converts artwork data to a base64-encoded string.

    Args:
        artwork: The artwork data.

    Returns:
        str or None: The base64-encoded string, or None if artwork is None.
    """
    if artwork is not None:
        return base64.b64encode(artwork.data).decode('utf-8')
    return None


def get_artwork(bucket_name: str, file_name: str):
    """
    Retrieves artwork from a specified bucket and file name, converts it to base64.

    Args:
        bucket_name (str): The name of the bucket.
        file_name (str): The name of the file.

    Returns:
        str or None: The base64-encoded artwork, or None if not found or an error occurs.
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            try:
                data = minio_client.get_object(bucket_name, file_name)
                temp_file.write(data.read())
            except S3Error as e:
                if e.code == 'NoSuchKey':
                    return None
                else:
                    raise
        f = music_tag.load_file(temp_file.name)
        if f['artwork'] and f['artwork'].first is not None:
            return convert_artwork_to_base64(f['artwork'].first)
        return None
    finally:
        os.unlink(temp_file.name)


def get_metadata_and_artwork(bucket_name: str, file_name: str):
    """
    Retrieves metadata and artwork for a given file from MinIO, converting artwork to base64.

    Args:
        bucket_name (str): The name of the bucket.
        file_name (str): The name of the file.

    Returns:
        dict: A dictionary containing the metadata and base64-encoded artwork.
    """
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        data = minio_client.get_object(bucket_name, file_name)
        temp_file.write(data.read())

    try:
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
        if f['artwork'] and f['artwork'].first is not None:
            metadata["artwork"] = convert_artwork_to_base64(f['artwork'].first)
        return metadata
    finally:
        os.unlink(temp_file.name)


def sanitize_filename(filename):
    """
    Sanitizes a filename by removing disallowed characters and sequences.

    Args:
        filename (str): The filename to sanitize.

    Returns:
        str: The sanitized filename.
    """
    replacements = {
        "!": "", "@": "", "#": "", "$": "", "%": "", "^": "", "&": "", "*": "", "(": "", ")": "",
        "[": "", "]": "", "{": "", "}": "", ";": "", ":": "", "\"": "", "'": "", ",": "", "<": "",
        ">": "", "/": "", "?": "", "`": "", "~": "",
        "é": "e", "è": "e", "ê": "e", "à": "a", "â": "a", "ù": "u", "ô": "o", "î": "i", "ç": "c", "ë": "e"
    }
    has_mp3_extension = filename.lower().endswith('.mp3')
    if has_mp3_extension:
        base_name, extension = filename[:-4], filename[-4:]
    else:
        base_name, extension = filename, ''
    base_name = base_name.replace("..", "").replace("//", "")
    sanitized_base_name = "".join(replacements.get(c, c) for c in base_name if c not in [' '] and (c.isalnum() or c in replacements))
    if has_mp3_extension:
        sanitized_base_name = sanitized_base_name.rstrip(".")
    sanitized = sanitized_base_name + extension
    if not sanitized:
        raise ValueError("Filename cannot be empty.")
    return sanitized


def get_embedding_pkl(filename):
    """
    Retrieves the embeddings for a specified audio file from MinIO. If the pkl containing the embeddings exists,
    it returns the content of the pkl file (a list of floats). If the pkl file does not exist, it returns False.

    Args:
        filename (str): The name of the audio file.

    Returns:
        list or False: The content of the pkl file (a list of floats) if exists, otherwise False.
    """
    pkl_filename = filename.replace(".mp3", ".pkl")
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            data = minio_client.get_object(DEFAULT_SETTINGS.minio_temp_bucket_name, pkl_filename)
            temp_file.write(data.read())
            temp_file.seek(0)
            embeddings = pickle.load(temp_file)
        return embeddings
    except S3Error as e:
        if e.code == 'NoSuchKey':
            return False
        else:
            raise


def save_embedding_pkl(object_name, file_path):
    """
    Saves an object to MinIO.

    Args:
        object_name (str): The name of the object to be saved in the bucket.
        file_path (str): The local path to the file to be uploaded.

    Returns:
        bool: True if the file was successfully uploaded, False otherwise.
    """
    bucket_name = DEFAULT_SETTINGS.minio_temp_bucket_name
    try:
        # Open the file in binary read mode
        with open(file_path, "rb") as file_data:
            # Get the position of the cursor, i.e., the file size
            file_data.seek(0, 2)
            file_length = file_data.tell() 
            file_data.seek(0)  

            # Upload the file
            minio_client.put_object(
                bucket_name,
                object_name,
                file_data,
                length=file_length,
                content_type="application/octet-stream"
            )
        return True
    except S3Error as e:
        return False


def delete_file_background_task(file_path: str):
    """
    Deletes the specified file from the filesystem. To be used as a cleanup function after the file has been sent.
    FastAPI will call this function after the file has been sent. (See: https://fastapi.tiangolo.com/tutorial/background-tasks/)

    Args:
        file_path (str): The path to the file to delete.
    """
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")



def create_zip_from_minio_paths(paths, zip_name="genre.zip"):
    """
    Creates a ZIP file containing MP3 files from the given paths in the MinIO bucket.

    Args:
        paths (list): List of paths to the MP3 files in the MinIO bucket.
        zip_name (str): The name of the output ZIP file.

    Returns:
        str: The path to the created ZIP file.
    """
    temp_dir = "/tmp/minio_downloads"

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    try:
        with zipfile.ZipFile(zip_name, 'w') as zipf:
            for path in paths:
                try:
                    file_data = minio_client.get_object(DEFAULT_SETTINGS.minio_bucket_name, path)
                    local_file_path = os.path.join(temp_dir, os.path.basename(path))

                    with open(local_file_path, 'wb') as local_file:
                        for d in file_data.stream(32*1024):
                            local_file.write(d)

                    zipf.write(local_file_path, os.path.basename(path))

                except S3Error as e:
                    print(f"Error downloading {path}: {e}")

        return zip_name

    finally:
        for file in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, file))
        os.rmdir(temp_dir)