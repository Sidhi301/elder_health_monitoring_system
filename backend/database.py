

from pymongo import MongoClient
from pymongo.database import Database

from backend.config import MONGO_DB_NAME, MONGO_URL


def get_database() -> Database:
  
    client = MongoClient(MONGO_URL)
    return client[MONGO_DB_NAME]


db = get_database()
