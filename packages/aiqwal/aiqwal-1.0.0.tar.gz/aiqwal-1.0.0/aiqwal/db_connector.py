# aiqwal/db_connector.py
import sqlalchemy
from sqlalchemy import create_engine, inspect

class DBConnector:
    def __init__(self, db_type: str, connection_string: str):
        self.db_type = db_type.lower()
        self.connection_string = connection_string
        self.engine = create_engine(connection_string)
        self.inspector = inspect(self.engine)

    def fetch_schema(self):
        """
        Fetch all tables and columns from the connected database.
        Returns a dict like:
        { "table_name": ["col1", "col2", ...], ... }
        """
        schema = {}
        for table_name in self.inspector.get_table_names():
            columns = [col['name'] for col in self.inspector.get_columns(table_name)]
            schema[table_name] = columns
        return schema
