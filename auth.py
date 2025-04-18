from passlib.context import CryptContext
from models import User
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_user(db: Session, username: str, password: str, role: str):
    hashed_pw = hash_password(password)
    user = User(username=username, hashed_password=hashed_pw, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
