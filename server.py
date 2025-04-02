import os
from pymongo import MongoClient
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi import HTTPException

# Load environment variables
load_dotenv()

# MongoDB Connection
MONGO_URI = "mongodb+srv://Ronak:Ronak123@task.nabdt.mongodb.net/?retryWrites=true&w=majority&appName=Task"  # Example: "mongodb+srv://username:password@cluster.mongodb.net/"
DB_NAME = "Task"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["link"]

# Initialize FastAPI app
app = FastAPI()

# Allow CORS (configure properly for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow only frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Hello from Python FastAPI Backend!"}

@app.get("/api/data")
def get_data():
    return {"data": [1, 2, 3, 4, 5]}

# Define Request Model
class ProfileData(BaseModel):
    github: str
    linkedin: str
    leetcode: str

@app.post("/api/analyze")
async def analyze_profiles(data: ProfileData):
    # Check if GitHub ID or LinkedIn link already exists
    existing_profile = collection.find_one(
        {"$or": [{"github": data.github}, {"linkedin": data.linkedin}]}
    )

    if existing_profile:
        raise HTTPException(
            status_code=400,
            detail="Profile with this GitHub ID or LinkedIn link already exists."
        )

    # Insert new profile if no duplicate is found
    result = collection.insert_one(data.dict())
    print(f"Inserted ID: {result.inserted_id}")

    return {
        "message": "Profile saved successfully!",
        "inserted_id": str(result.inserted_id),
        "data": data
    }
