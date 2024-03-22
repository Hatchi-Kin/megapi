from fastapi_login import LoginManager
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from source.models.users import User

DATABASE_URL = "postgresql://admin:example@db:5432/fastapi_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

manager = LoginManager("SECRET", "/auth/token")

@manager.user_loader()
def get_user(email: str):
    db = SessionLocal()
    return db.query(User).filter(User.email == email).first()