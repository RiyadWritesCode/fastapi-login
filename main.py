from fastapi import FastAPI, Depends, Form
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware


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
    allow_origins=["*"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root(): 
    return "Hello world"

@app.post("/signup")
def signup(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = User(email=email, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Sign up successful", "email": user.email}


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
