# Supported database types
DB_TYPES = ["postgresql", "mysql", "sqlite"]

# Default AI model path (GGUF)
import os

AI_MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "sqlcoder-7b-2-q4_k_m.gguf")

# Max tokens for SQL generation
MAX_TOKENS = 512