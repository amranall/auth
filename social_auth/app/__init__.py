from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello Working"}

# Load configurations from .env
SESSION_SECRET_KEY = os.getenv('SESSION_SECRET_KEY')
print(SESSION_SECRET_KEY)

# Add Session Middleware
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from .routes import google, github
from . import ws_mange

app.include_router(google.router, prefix="/auth/google")
app.include_router(github.router, prefix="/auth/github")
app.include_router(ws_mange.router, prefix="/ws")
