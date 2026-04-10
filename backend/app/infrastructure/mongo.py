# app/infrastructure/mongo.py
import os
from functools import lru_cache
from urllib.parse import urlparse

from pymongo import MongoClient
import certifi
from dotenv import load_dotenv
from pymongo.collection import Collection

load_dotenv()  # 本地开发时加载 .env


@lru_cache
def get_mongo_client() -> MongoClient:
    mongo_uri = (
        os.getenv("MONGO_URI")
        or os.getenv("MONGODB_URL")
        or os.getenv("MONGO_URL")
        or ""
    ).strip()
    if not mongo_uri:
        raise RuntimeError("MONGO_URI not set (also tried MONGODB_URL / MONGO_URL)")

    client = MongoClient(
        mongo_uri,
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=15000,
        connectTimeoutMS=10000,
        socketTimeoutMS=10000,
    )
    # 探活，连不上直接抛错
    client.admin.command("ping")
    return client


@lru_cache
def get_db():
    mongo_uri = (
        os.getenv("MONGO_URI")
        or os.getenv("MONGODB_URL")
        or os.getenv("MONGO_URL")
        or ""
    ).strip()

    parsed = urlparse(mongo_uri)
    db_name = (os.getenv("MONGO_DB_NAME") or parsed.path.lstrip("/") or "dispatch-ai")

    client = get_mongo_client()
    return client[db_name]


def call_logs_col() -> Collection:
    return get_db()["call_logs"]


def tickets_col() -> Collection:
    return get_db()["tickets"]


def actions_col() -> Collection:
    return get_db()["actions"]


def business_col() -> Collection:
    return get_db()["business"]


def users_col() -> Collection:
    return get_db()["users"]


def services_col() -> Collection:
    return get_db()["services"]


def kb_chunks_col() -> Collection:
    return get_db()["kb_chunks"]