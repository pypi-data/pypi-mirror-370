from web.database import Database
import psycopg2


class PgDatabase(Database):
    def __init__(self) -> None:
        self.driver = psycopg2
        super().__init__(self.driver)

    def connect_to_database(self):
        username, password, db_name, db_host, db_port = super().get_connection_params()

        return self.driver.connect(
            host=db_host,
            port=db_port,
            user=username,
            password=password,
            database=db_name
        )
