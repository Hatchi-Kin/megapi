from sqlalchemy.orm import Session
from models.uploaded import UserUploaded


def store_upload_info(db: Session, user_id: int, filename: str):
    """
    Stores information about a file uploaded by a user in the database if it does not already exist.

    Args:
        db (Session): The SQLAlchemy session object.
        user_id (int): The ID of the user who uploaded the file.
        filename (str): The name of the uploaded file.

    This function checks if an entry with the given user ID and filename already exists in the database.
    If not, it creates a new entry and commits it to the database.
    """
    existing_entry = db.query(UserUploaded).filter_by(user_id=user_id, filename=filename).first()
    
    if not existing_entry:
        upload_entry = UserUploaded(user_id=user_id, filename=filename)
        db.add(upload_entry)
        db.commit()


def get_user_uploads(db: Session, user_id: int):
    """
    Retrieves all files uploaded by a specific user.

    Args:
        db (Session): The SQLAlchemy session object.
        user_id (int): The ID of the user whose uploads are to be retrieved.

    Returns:
        list[dict]: A list of dictionaries, each containing the filename of an uploaded file.
    """
    uploaded_files = db.query(UserUploaded).filter(UserUploaded.user_id == user_id).all()
    return [{"filename": file.filename} for file in uploaded_files]


def delete_user_upload_from_db(db: Session, user_id: int, filename: str):
    """
    Deletes an entry from the database for a file uploaded by a user.

    Args:
        db (Session): The SQLAlchemy session object.
        user_id (int): The ID of the user who uploaded the file.
        filename (str): The name of the uploaded file.

    This function deletes the entry corresponding to the user ID and filename from the database.
    """
    db.query(UserUploaded).filter_by(user_id=user_id, filename=filename).delete()
    db.commit()
    