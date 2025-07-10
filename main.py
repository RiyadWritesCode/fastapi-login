from hashlib import scrypt
import bcrypt
from fastapi import FastAPI, Depends, Form, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware
import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


SECRET_KEY = "secret-key"
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=5)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")

# Database
engine = create_engine("sqlite:///./items.db")
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Model
class User(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True)
    email = Column(String)
    password = Column(String)#t

# Create the table
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/protected")
def protected(token: str = Depends(oauth2_scheme)):
    try:
        payload = verify_token(token)
        return {"email": payload["sub"]}
    except:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.post("/signup")
def signup(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user = User(email=email, password=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.email})

    return {"message": "Signup successful", "token": token, "email": email}


@app.post("/login")
def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email, User.password == password).first()

    if user:
        return {"message": "Login successful", "email": user.email}
    else:
        return {"message": "Invalid email or password"}
    
@app.post("/delete-user")
def delete_user(db: Session = Depends(get_db)):
    return
