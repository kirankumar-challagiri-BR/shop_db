from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from app.database import postgreSql_pool
from app.auth_utils import hash_password, verify_assword, create_access_token
from psycopg2.extras import RealDictCursor


router = APIRouter(prefix="/auth", tags=["Authentication"])

# Schema for user registration
class UserRegister(BaseModel):
    username: str
    email: EmailStr #validates that it's real email format
    password: str

@router.post("/register")
def register_user(user: UserRegister):
    conn = postgreSql_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE username = %s or email = %s", (user.username, user.email))
            #1. Check if user already exists
            existing_user = cursor.fetchone()
            if existing_user:
                raise HTTPException(status_code=400, detail="Username or email already registered")

            # Hash the password
            hashed_password = hash_password(user.password)

            # Insert new user into the database
            cursor.execute(
                "INSERT INTO users (username, email, hashed_password) VALUES (%s, %s, %s) RETURNING id, username, email",
                (user.username, user.email, hashed_password)
            )
            new_user = cursor.fetchone()
            conn.commit()
            return {"msg": "User registered successfully", "user": new_user}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        postgreSql_pool.putconn(conn)

# Schema for user login
class UserLogin(BaseModel):
    username: str
    password: str

@router.post("/login")
def login_user(user_credentials: OAuth2PasswordRequestForm = Depends()):
    conn= postgreSql_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Fetch user by username
            cursor.execute("SELECT * FROM users WHERE username = %s", (user_credentials.username,))
            user = cursor.fetchone()
            if not user:
                raise HTTPException(status_code=401, detail="Invalid username or password")

            # Verify password
            if not verify_assword(user_credentials.password, user['hashed_password']):
                raise HTTPException(status_code=401, detail="Invalid username or password")

            # Create JWT token
            access_token = create_access_token(data={"user_id": user['id'], "username": user['username']})
            return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:  
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        postgreSql_pool.putconn(conn)