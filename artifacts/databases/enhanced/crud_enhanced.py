# crud_enhanced.py
# Enhanced CRUD module for Grazioso Salvare project
# Provides Create, Read, Update, Delete functionality for the AAC MongoDB database

import logging
import json
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Configure logging
logging.basicConfig(
    filename='crud.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

class AnimalShelterCRUD:
    """Provides CRUD operations for the Grazioso Salvare animal shelter database."""

    def __init__(self, username, password, config_file='config.json'):
        """
        Initialize connection to MongoDB using a configuration file.

        Args:
            username (str): MongoDB username
            password (str): MongoDB password
            config_file (str): Path to JSON config file
        """
        try:
            with open(config_file) as f:
                config = json.load(f)

            host = config.get("host", "localhost")
            port = config.get("port", 27017)
            db = config.get("db", "aac")
            collection = config.get("collection", "animals")

            self.client = MongoClient(
                f"mongodb://{username}:{password}@{host}:{port}/{db}?authSource=admin"
            )
            self.database = self.client[db]
            self.collection = self.database[collection]

            logging.info("Connected to MongoDB successfully.")

        except (PyMongoError, FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Initialization error: {e}")
            self.collection = None

    def _execute(self, operation, *args, **kwargs):
        """
        Helper method to safely execute MongoDB operations.

        Returns:
            Operation result or None if an error occurs.
        """
        try:
            return operation(*args, **kwargs)
        except PyMongoError as e:
            logging.error(f"Database operation failed: {e}")
            return None

    def create(self, data):
        """
        Insert a new document into the collection.

        Args:
            data (dict): Document to insert

        Returns:
            dict: Result message
        """
        if not isinstance(data, dict) or not data:
            return {"success": False, "message": "Data must be a non-empty dictionary."}

        result = self._execute(self.collection.insert_one, data)

        if result and result.inserted_id:
            logging.info(f"Document created with ID: {result.inserted_id}")
            return {"success": True, "id": str(result.inserted_id)}

        return {"success": False, "message": "Insert failed."}

    def read(self, query):
        """
        Read documents matching the query.

        Args:
            query (dict): MongoDB query

        Returns:
            list: List of matching documents
        """
        if not isinstance(query, dict):
            logging.warning("Read failed: Query must be a dictionary.")
            return []

        # Security check
        if "$where" in query:
            logging.warning("Blocked unsafe query containing $where operator.")
            return []

        cursor = self._execute(self.collection.find, query)
        return list(cursor) if cursor else []

    def update(self, query, new_values):
        """
        Update documents matching the query.

        Args:
            query (dict): MongoDB query
            new_values (dict): Fields to update

        Returns:
            dict: Result message
        """
        if not isinstance(query, dict) or not isinstance(new_values, dict):
            return {"success": False, "message": "Query and new_values must be dictionaries."}

        result = self._execute(self.collection.update_many, query, {"$set": new_values})

        if result:
            logging.info(f"Updated {result.modified_count} documents.")
            return {"success": True, "modified": result.modified_count}

        return {"success": False, "message": "Update failed."}

    def delete(self, query):
        """
        Delete documents matching the query.

        Args:
            query (dict): MongoDB query

        Returns:
            dict: Result message
        """
        if not isinstance(query, dict):
            return {"success": False, "message": "Query must be a dictionary."}

        result = self._execute(self.collection.delete_many, query)

        if result:
            logging.info(f"Deleted {result.deleted_count} documents.")
            return {"success": True, "deleted": result.deleted_count}

        return {"success": False, "message": "Delete failed."}
