# aiqwal/session.py
import uuid
from aiqwal.schema_cache import SchemaCache

class SessionManager:
    def __init__(self):
        self.sessions = SchemaCache()

    def create_session(self):
        session_id = str(uuid.uuid4())
        self.sessions.save_schema(session_id, {})
        return session_id

    def save_schema(self, session_id: str, schema_json: dict):
        self.sessions.save_schema(session_id, schema_json)

    def get_schema(self, session_id: str):
        return self.sessions.get_schema(session_id)
