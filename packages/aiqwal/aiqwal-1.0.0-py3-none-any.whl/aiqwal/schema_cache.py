# aiqwal/schema_cache.py

class SchemaCache:
    def __init__(self):
        self.cache = {}  # {session_id: schema_json}

    def save_schema(self, session_id: str, schema_json: dict):
        self.cache[session_id] = schema_json

    def get_schema(self, session_id: str):
        return self.cache.get(session_id, {})
