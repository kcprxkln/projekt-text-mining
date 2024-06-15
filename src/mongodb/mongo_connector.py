from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
from typing import List
import os 

class MongoDatabase(object):
    MONGODB_HOST = os.environ.get("MONGODB_HOST", "localhost")
    MONGODB_PORT = int(os.environ.get("MONGODB_PORT", 27017))
    MONGODB_USER = os.environ.get("MONGODB_USER")
    MONGODB_PASSWORD = os.environ.get("MONGODB_PASSWORD")
    DB_NAME = 'crypto_sentiment' or os.environ.get("MONGODB_DB")

    CLIENT = None
    DATABASE = None


    @staticmethod
    def initialize():
        try:
            if MongoDatabase.MONGODB_USER and MongoDatabase.MONGODB_PASSWORD:
                connection_string = f"mongodb://{MongoDatabase.MONGODB_USER}:{MongoDatabase.MONGODB_PASSWORD}@{MongoDatabase.MONGODB_HOST}:{MongoDatabase.MONGODB_PORT}/{MongoDatabase.DB_NAME}"
            else:
                connection_string = f"mongodb://{MongoDatabase.MONGODB_HOST}:{MongoDatabase.MONGODB_PORT}/"

            MongoDatabase.CLIENT = MongoClient(connection_string)
            MongoDatabase.DATABASE = MongoDatabase.CLIENT[MongoDatabase.DB_NAME]

        except ConnectionFailure as e:
            print(f"Error connecting to MongoDB: {e}")
            # Log the error

        except ConfigurationError as e:
            print(f"MongoDB configuration error: {e}")
            # log error


    @staticmethod
    def insert_one(collection: str, data: dict):
        try:
            MongoDatabase.DATABASE[collection].insert_one(data)
        except Exception as e:
            print(f"Error with inserting data into MongoDB: {e}")

    @staticmethod
    def insert_many(collection: str, data: list[dict]):
        try:
            MongoDatabase.DATABASE[collection].insert_many(data)
        except Exception as e:
            print(f"Error with inserting data into MongoDB: {e}")

    @staticmethod
    def find(collection: str, query: dict):
        return MongoDatabase.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection: str, query: dict):
        return MongoDatabase.DATABASE[collection].find_one(query)

    @staticmethod
    def upsert(collection: str, query: dict, document: dict):
        try:
            if '_id' in document:
                del document['_id']
            update_data = {"$set": document}
            result = MongoDatabase.DATABASE[collection].update_one(query, update_data, upsert=True)
            return result
        except Exception as e:
            print(f"Error with upserting data into MongoDB: {e}")

    @staticmethod
    def close():
        if MongoDatabase.CLIENT:
            MongoDatabase.CLIENT.close()