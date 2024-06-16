from sqlalchemy.orm import Session
from models.uploaded import UserUploaded


def store_upload_info(db: Session, user_id: int, filename: str):
    # Check if the entry already exists
    existing_entry = db.query(UserUploaded).filter_by(user_id=user_id, filename=filename).first()
    
    if not existing_entry:
        upload_entry = UserUploaded(user_id=user_id, filename=filename)
        db.add(upload_entry)
        db.commit()


def get_user_uploads(db: Session, user_id: int):
    uploaded_files = db.query(UserUploaded).filter(UserUploaded.user_id == user_id).all()
    return [{"filename": file.filename} for file in uploaded_files]