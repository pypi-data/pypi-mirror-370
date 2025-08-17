import os
from abc import ABC, abstractmethod


class Database(ABC):
    """
    Database context manager
    """

    def __init__(self, driver) -> None:
        self.driver = driver

    @abstractmethod
    def connect_to_database(self):
        raise NotImplementedError()

    def __enter__(self):
        self.connection = self.connect_to_database()
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exception_type, exc_val, traceback):
        self.cursor.close()
        self.connection.close()

    def get_connection_params(self):
        username = os.getenv("DB_USERNAME", "backend")
        password = os.getenv("DB_PASSWORD", "backend")
        db_url: str = os.getenv("DB_URL", "jdbc:postgresql://localhost:5432/backend")
        db_name = db_url.split("/")[-1]
        db_host_port = db_url.split("//")[1].split("/")[0]
        db_host, db_port = db_host_port.split(":")

        return username, password, db_name, db_host, db_port
