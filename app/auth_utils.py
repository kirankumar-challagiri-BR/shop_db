import os
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt

#1. Setup password hashing 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


#2. Secrete key (in phase 3 we will move this to env variables)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def hash_password(password: str):
    """Hash a plaintext password."""
    return pwd_context.hash(password)

def verify_assword(plain_password:str, hashed_password:str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    #tokem expire in 30 minutes
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



# This tells FastAPI where to look for the token (the /login URL)
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_schema)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # decode the JWT token 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        user_id: int = payload.get("user_id")

        if username is None or user_id is None: 
            raise credentials_exception
        
        return {"user_id": user_id, "username": username}
    except jwt.PyJWTError:
        raise credentials_exception
    
