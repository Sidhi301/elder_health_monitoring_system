"""
This file connects the FastAPI app to MongoDB.
The code is kept simple so beginners can understand it easily.
"""

from pymongo import MongoClient
from pymongo.database import Database

from backend.config import MONGO_DB_NAME, MONGO_URL


def get_database() -> Database:
    """
    Create a MongoDB client and return the selected database.
    This small function keeps database access in one place.
    """
    client = MongoClient(MONGO_URL)
    return client[MONGO_DB_NAME]
    

# Create one shared database object for the whole project.
db = get_database()
