from web.database import Database
import os
from pymongo import MongoClient

class MongoDatabase(Database):
    def __init__(self):
        super().__init__(None)
    def connect_to_database(self):
        db_uri, db_name = self.get_connection_params()
        return MongoClient(db_uri)

    def get_connection_params(self):
        db_uri = os.getenv('MONGO_URI')
        db_name = os.getenv('MONGO_DB')
        return db_uri, db_name

    def __enter__(self):
        db_uri, db_name = self.get_connection_params()
        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]
        return self.db

    def __exit__(self, exception_type, exc_val, traceback):
        self.client.close()
