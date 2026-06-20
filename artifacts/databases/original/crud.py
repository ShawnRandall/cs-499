# crud.py
# CRUD module for Grazioso Salvare project
# Provides Create, Read, Update, Delete functionality for the AAC MongoDB database

from pymongo import MongoClient
from pymongo.errors import PyMongoError

class AnimalShelterCRUD:
    """Provides CRUD operations for the Grazioso Salvare animal shelter database."""

    def __init__(self, username, password, host='localhost', port=27017, db='aac', collection='animals'):
        """
        Initialize connection to MongoDB.
        Args:
            username (str): MongoDB username
            password (str): MongoDB password
            host (str): Database host (default localhost)
            port (int): Database port (default 27017)
            db (str): Database name
            collection (str): Collection name
        """
        try:
            self.client = MongoClient(f'mongodb://{username}:{password}@{host}:{port}/{db}?authSource=admin')
            self.database = self.client[db]
            self.collection = self.database[collection]
        except PyMongoError as e:
            print(f"Connection error: {e}")
            self.collection = None

    def create(self, data):
        """
        Insert a new document into the collection.
        Args:
            data (dict): Document to insert
        Returns:
            bool: True if successful, False otherwise
        """
        if data is not None:
            try:
                result = self.collection.insert_one(data)
                return True if result.inserted_id else False
            except PyMongoError as e:
                print(f"Create error: {e}")
        return False

    def read(self, query):
        """
        Read documents matching the query.
        Args:
            query (dict): MongoDB query
        Returns:
            list: List of matching documents
        """
        try:
            cursor = self.collection.find(query)
            return list(cursor)
        except PyMongoError as e:
            print(f"Read error: {e}")
            return []

    def update(self, query, new_values):
        """
        Update documents matching the query.
        Args:
            query (dict): MongoDB query
            new_values (dict): Fields to update
        Returns:
            int: Number of documents modified
        """
        try:
            result = self.collection.update_many(query, {"$set": new_values})
            return result.modified_count
        except PyMongoError as e:
            print(f"Update error: {e}")
            return 0

    def delete(self, query):
        """
        Delete documents matching the query.
        Args:
            query (dict): MongoDB query
        Returns:
            int: Number of documents deleted
        """
        try:
            result = self.collection.delete_many(query)
            return result.deleted_count
        except PyMongoError as e:
            print(f"Delete error: {e}")
            return 0