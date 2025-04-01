from pymongo import MongoClient
from pydantic import BaseModel
from fastapi import FastAPI
from typing import List
from fastapi.middleware.cors import CORSMiddleware

# Initialize the FastAPI app
app = FastAPI()

# MongoDB URI (replace with your actual MongoDB URI)
MONGO_URI = "mongodb+srv://Ronak:Ronak@51@analyzer.4lzmsnj.mongodb.net/?retryWrites=true&w=majority&appName=Analyzer"

# Create a client and connect to the MongoDB cluster
client = MongoClient(MONGO_URI)

# Access the database and collection
db = "Ronak"  # Replace with your database name
collection = db.profiles  # Replace with your collection name

# Allow CORS (so Next.js can call the API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Allow all origins
    allow_credentials=True,
    allow_methods=['*'],  # Allow all HTTP methods
    allow_headers=['*'],  # Allow all headers
)

@app.get('/')
def home():
    return {'message': 'Hello from Python FastAPI Backend!'}

@app.get('/api/data')
def get_data():
    return {'data': [1, 2, 3, 4, 5]}

# Define Request Model
class ProfileData(BaseModel):
    github: str
    linkedin: str
    leetcode: str

@app.post("/api/analyze")
async def analyze_profiles(data: ProfileData):
      return {"message": "Profiles received!", "data": data}