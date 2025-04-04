"""MongoDB client for frontend data access."""

import os
from typing import Optional
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from utils.config import mongo_uri  # ✅ Import the central URI builder


class MongoDBClient:
    """Client for connecting to and querying the MongoDB backend."""

    def __init__(self) -> None:
        """Initializes MongoDB client using constructed MongoDB URI."""
        mongo_connection_uri = mongo_uri()  # ✅ Use central builder
        db_name = os.getenv("DB_NAME", "kraken_data")

        self.client: MongoClient = MongoClient(mongo_connection_uri)
        self.db: Database = self.client[db_name]

    def get_collection(self, collection_name: str) -> Optional[Collection]:
        """Returns a MongoDB collection."""
        if collection_name in self.db.list_collection_names():
            return self.db[collection_name]
        return None

    def get_all_documents(self, collection_name: str) -> list[dict]:
        """Fetches all documents from a specified collection."""
        collection = self.get_collection(collection_name)
        if not collection:
            return []
        return list(collection.find({}))

    def get_latest_metadata(self, data_type: str) -> Optional[dict]:
        """Fetches the latest metadata document for a given data type."""
        collection = self.get_collection("kraken_metadata")
        if not collection:
            return None
        return collection.find_one(
            {"data_type": data_type},
            sort=[("timestamp", -1)]
        )