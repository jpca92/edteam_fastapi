import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")
if not mongodb_uri:
	raise RuntimeError("MONGODB_URI no está configurada en el entorno")

client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
db = client["fastapi_db"]
users_collection = db["users"]