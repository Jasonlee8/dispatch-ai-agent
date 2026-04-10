import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGODB_URI")
print("MONGODB_URI =", uri)

client = MongoClient(uri, serverSelectionTimeoutMS=5000)

print("Ping:", client.admin.command("ping"))
print("Databases:", client.list_database_names())
