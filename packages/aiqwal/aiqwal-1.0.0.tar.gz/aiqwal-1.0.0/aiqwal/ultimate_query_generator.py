# # aiqwal/ultimate_query_generator.py
# """
# Ultimate Query Generator - Works with ANY database in the world
# Uses database-aware prompts and generates database-specific SQL
# """

# from pathlib import Path
# from llama_cpp import Llama
# from aiqwal.config import AI_MODEL_PATH
# import re
# from typing import Dict, Any

# class UltimateQueryGenerator:
#     """
#     Ultimate SQL Generator that adapts to ANY database
#     """
    
#     def __init__(self, model_path: str = AI_MODEL_PATH):
#         model_file = Path(model_path)
#         if not model_file.exists():
#             raise FileNotFoundError(f"Model not found at {model_path}")
        
#         self.model = Llama(
#             model_path=str(model_file), 
#             n_ctx=4096,
#             n_threads=8,
#             verbose=False,
#             temperature=0.0
#         )
    
#     def generate_sql(self, user_query: str, schema_json: Dict, database_manager) -> str:
#         """
#         Generate SQL optimized for the specific database
#         """
#         # Validation
#         validation_result = self._validate_request(user_query, schema_json)
#         if not validation_result['is_valid']:
#             raise ValueError(validation_result['error_message'])
        
#         db_info = database_manager.get_database_info()
#         db_type = db_info['type']
#         db_name = db_info['name']
        
#         print(f"🎯 Generating SQL for {db_name} ({db_type})")
        
#         # Try database-specific strategies
#         strategies = [
#             lambda: self._generate_database_optimized_sql(user_query, schema_json, db_info),
#             lambda: self._generate_universal_sql(user_query, schema_json),
#             lambda: self._generate_pattern_based_sql(user_query, schema_json, db_info)
#         ]
        
#         for i, strategy in enumerate(strategies, 1):
#             try:
#                 print(f"  Trying {db_name} strategy {i}...")
                
#                 raw_sql = strategy()
                
#                 # Adapt SQL for the specific database
#                 adapted_sql = database_manager.adapt_sql_for_database(raw_sql)
                
#                 if self._validate_generated_sql(adapted_sql, schema_json):
#                     print(f"  ✅ Strategy {i} succeeded: {adapted_sql}")
#                     return adapted_sql
#                 else:
#                     print(f"  ❌ Strategy {i} generated invalid SQL")
                    
#             except Exception as e:
#                 print(f"  ❌ Strategy {i} failed: {e}")
#                 continue
        
#         raise Exception(f"Failed to generate SQL for {db_name}: '{user_query}'")
    
#     def _generate_database_optimized_sql(self, user_query: str, schema_json: Dict, db_info: Dict) -> str:
#         """
#         Generate SQL optimized for the specific database type
#         """
#         db_type = db_info['type']
#         db_name = db_info['name']
#         schema_text = self._format_schema(schema_json)
        
#         # Database-specific optimization instructions
#         db_optimizations = {
#             'postgresql': """
# - Use PostgreSQL advanced features: NULLS LAST, window functions, CTEs
# - Use proper LIMIT/OFFSET for pagination
# - Use single quotes for strings, double quotes for identifiers
# - Leverage PostgreSQL's powerful aggregation functions
#             """,
#             'mysql': """
# - Use MySQL syntax with backticks for identifiers if needed
# - Use LIMIT for pagination (no OFFSET issues)
# - Be aware of MySQL's GROUP BY requirements
# - Use MySQL-specific functions where beneficial
#             """,
#             'sqlite': """
# - Use simple SQLite syntax - avoid complex features
# - Use LIMIT for pagination (simple and effective)
# - Avoid window functions and advanced features
# - Keep queries lightweight and efficient
#             """,
#             'mssql': """
# - Use SQL Server TOP syntax instead of LIMIT
# - Use square brackets for identifiers with spaces
# - Leverage SQL Server's advanced analytics functions
# - Use proper SQL Server pagination with OFFSET/FETCH
#             """,
#             'oracle': """
# - Use Oracle ROWNUM for limiting results
# - Use NULLS LAST for proper sorting
# - Leverage Oracle's advanced SQL features
# - Use dual table when needed for expressions
#             """,
#             'snowflake': """
# - Use Snowflake's cloud-optimized SQL features
# - Leverage powerful analytics and window functions
# - Use proper LIMIT/OFFSET syntax
# - Optimize for columnar storage patterns
#             """,
#             'bigquery': """
# - Use BigQuery Standard SQL syntax
# - Leverage BigQuery's powerful analytics functions
# - Use proper dataset.table references
# - Optimize for BigQuery's distributed architecture
#             """,
#             'redshift': """
# - Use Redshift's PostgreSQL-compatible syntax
# - Leverage columnar storage optimizations
# - Use proper LIMIT syntax for large datasets
# - Consider Redshift's distribution and sort keys
#             """
#         }
        
#         optimization_guide = db_optimizations.get(db_type, "Use standard SQL syntax")
        
#         prompt = f"""### Task
# Generate optimized SQL for {db_name} database.

# ### Database: {db_name} ({db_type.upper()})
# Optimization Guidelines:
# {optimization_guide}

# ### Database Schema
# {schema_text}

# ### User Request
# {user_query}

# ### Optimized {db_name} SQL
# ```sql"""

#         response = self.model(
#             prompt,
#             max_tokens=250,
#             temperature=0.0,
#             stop=["```", "</s>", "\n\n"],
#             repeat_penalty=1.1
#         )
        
#         return self._clean_sql_response(response['choices'][0]['text'])
    
#     def _generate_universal_sql(self, user_query: str, schema_json: Dict) -> str:
#         """
#         Generate universal SQL that works on most databases
#         """
#         schema_text = self._format_schema(schema_json)
        
#         prompt = f"""### Task
# Generate universal ANSI SQL that works on multiple databases.

# ### Universal SQL Rules
# - Use only standard SQL: SELECT, FROM, WHERE, ORDER BY, GROUP BY, HAVING
# - Use standard functions: COUNT(), AVG(), SUM(), MAX(), MIN()
# - Avoid database-specific syntax
# - Use single quotes for strings
# - Use standard comparison operators

# ### Schema
# {schema_text}

# ### Query
# {user_query}

# ### Universal SQL
# ```sql"""

#         response = self.model(
#             prompt,
#             max_tokens=200,
#             temperature=0.0,
#             stop=["```", "</s>", "\n\n"],
#             repeat_penalty=1.1
#         )
        
#         return self._clean_sql_response(response['choices'][0]['text'])
    
#     def _generate_pattern_based_sql(self, user_query: str, schema_json: Dict, db_info: Dict) -> str:
#         """
#         Generate SQL using pattern recognition (fallback method)
#         """
#         table_name = list(schema_json.keys())[0]
#         columns = schema_json[table_name]
#         query_lower = user_query.lower()
        
#         # Extract common patterns
#         if any(word in query_lower for word in ['top', 'highest', 'maximum']):
#             numeric_col = self._find_numeric_column(columns)
#             limit_match = re.search(r'\b(\d+)\b', user_query)
#             limit = limit_match.group(1) if limit_match else '10'
            
#             # Generate database-appropriate TOP N query
#             if db_info['supports_limit']:
#                 return f"SELECT * FROM {table_name} ORDER BY {numeric_col} DESC LIMIT {limit}"
#             elif db_info['type'] == 'mssql':
#                 return f"SELECT TOP {limit} * FROM {table_name} ORDER BY {numeric_col} DESC"
#             else:  # Oracle
#                 return f"SELECT * FROM {table_name} WHERE ROWNUM <= {limit} ORDER BY {numeric_col} DESC"
        
#         elif any(word in query_lower for word in ['count', 'total', 'how many']):
#             return f"SELECT COUNT(*) as total FROM {table_name}"
        
#         elif any(word in query_lower for word in ['average', 'mean']):
#             numeric_col = self._find_numeric_column(columns)
#             return f"SELECT AVG({numeric_col}) as average FROM {table_name}"
        
#         else:
#             # Default: show all with limit
#             if db_info['supports_limit']:
#                 return f"SELECT * FROM {table_name} LIMIT 100"
#             elif db_info['type'] == 'mssql':
#                 return f"SELECT TOP 100 * FROM {table_name}"
#             else:
#                 return f"SELECT * FROM {table_name} WHERE ROWNUM <= 100"
    
#     def _validate_request(self, user_query: str, schema_json: Dict) -> Dict[str, Any]:
#         """Validate user request"""
#         if not user_query or len(user_query.strip()) < 3:
#             return {
#                 'is_valid': False,
#                 'error_message': 'Query is too short or empty.'
#             }
        
#         if not schema_json:
#             return {
#                 'is_valid': False,
#                 'error_message': 'No database schema available.'
#             }
        
#         # Check for dangerous operations
#         dangerous_keywords = ['drop', 'delete', 'truncate', 'alter', 'create', 'insert', 'update']
#         query_lower = user_query.lower()
        
#         for keyword in dangerous_keywords:
#             if keyword in query_lower:
#                 return {
#                     'is_valid': False,
#                     'error_message': f'Cannot process "{keyword}" operations. Only SELECT queries are supported.'
#                 }
        
#         return {'is_valid': True, 'error_message': None}
    
#     def _validate_generated_sql(self, sql: str, schema_json: Dict) -> bool:
#         """Validate generated SQL"""
#         if not sql or len(sql.strip()) < 6:
#             return False
        
#         sql_upper = sql.upper().strip()
        
#         # Must start with SELECT
#         if not sql_upper.startswith('SELECT'):
#             return False
        
#         # Check table exists
#         table_names = list(schema_json.keys())
#         table_found = any(table.upper() in sql_upper for table in table_names)
        
#         return table_found
    
#     def _format_schema(self, schema_json: Dict) -> str:
#         """Format schema for prompts"""
#         formatted = []
#         for table, columns in schema_json.items():
#             formatted.append(f"Table {table} ({', '.join(columns)})")
#         return "\n".join(formatted)
    
#     def _clean_sql_response(self, response: str) -> str:
#         """Clean AI response to get pure SQL"""
#         if not response:
#             return ""
        
#         text = response.strip()
        
#         # Remove code blocks
#         text = re.sub(r'^```sql\n?', '', text, flags=re.IGNORECASE)
#         text = re.sub(r'^```\n?', '', text)
#         text = re.sub(r'\n?```$', '', text)
        
#         # Remove prefixes
#         prefixes = [r'^SQL:\s*', r'^Query:\s*', r'^Answer:\s*']
#         for prefix in prefixes:
#             text = re.sub(prefix, '', text, flags=re.IGNORECASE)
        
#         return text.strip().rstrip(';')
    
#     def _find_numeric_column(self, columns: list) -> str:
#         """Find likely numeric column for sorting"""
#         numeric_keywords = ['salary', 'price', 'amount', 'cost', 'value', 'score', 'id']
        
#         for keyword in numeric_keywords:
#             for col in columns:
#                 if keyword.lower() in col.lower():
#                     return col
        
#         return columns[0] if columns else 'id'

# aiqwal/ultimate_query_generator.py
"""
Ultimate Query Generator - Works with ANY database in the world
Uses database-aware prompts and generates database-specific SQL
"""

from pathlib import Path
from llama_cpp import Llama
from aiqwal.config import AI_MODEL_PATH
import re
from typing import Dict, Any

class UltimateQueryGenerator:
    """
    Ultimate SQL Generator that adapts to ANY database
    """
    
    def __init__(self, model_path: str = AI_MODEL_PATH):
        model_file = Path(model_path)
        if not model_file.exists():
            raise FileNotFoundError(f"Model not found at {model_path}")
        
        self.model = Llama(
            model_path=str(model_file), 
            n_ctx=4096,
            n_threads=8,
            verbose=False,
            temperature=0.0
        )
    
    def generate_sql(self, user_query: str, schema_json: Dict, database_manager) -> str:
        """
        Generate SQL optimized for the specific database
        """
        # Validation
        validation_result = self._validate_request(user_query, schema_json)
        if not validation_result['is_valid']:
            raise ValueError(validation_result['error_message'])
        
        db_info = database_manager.get_database_info()
        db_type = db_info['type']
        db_name = db_info['name']
        
        print(f"🎯 Generating SQL for {db_name} ({db_type})")
        
        # Try database-specific strategies
        strategies = [
            lambda: self._generate_database_optimized_sql(user_query, schema_json, db_info),
            lambda: self._generate_universal_sql(user_query, schema_json),
            lambda: self._generate_pattern_based_sql(user_query, schema_json, db_info)
        ]
        
        for i, strategy in enumerate(strategies, 1):
            try:
                print(f"  Trying {db_name} strategy {i}...")
                
                raw_sql = strategy()
                
                # Adapt SQL for the specific database
                adapted_sql = database_manager.adapt_sql_for_database(raw_sql)
                
                if self._validate_generated_sql(adapted_sql, schema_json):
                    print(f"  ✅ Strategy {i} succeeded: {adapted_sql}")
                    return adapted_sql
                else:
                    print(f"  ❌ Strategy {i} generated invalid SQL")
                    
            except Exception as e:
                print(f"  ❌ Strategy {i} failed: {e}")
                continue
        
        raise Exception(f"Failed to generate SQL for {db_name}: '{user_query}'")
    
    def _generate_database_optimized_sql(self, user_query: str, schema_json: Dict, db_info: Dict) -> str:
        """
        Generate SQL optimized for the specific database type
        """
        db_type = db_info['type']
        db_name = db_info['name']
        schema_text = self._format_schema(schema_json)
        
        # Database-specific optimization instructions
        db_optimizations = {
            'postgresql': """
- Use PostgreSQL advanced features: NULLS LAST, window functions, CTEs
- Use proper LIMIT/OFFSET for pagination
- Use single quotes for strings, double quotes for identifiers
- Leverage PostgreSQL's powerful aggregation functions
            """,
            'mysql': """
- Use MySQL syntax with backticks for identifiers if needed
- Use LIMIT for pagination (no OFFSET issues)
- Be aware of MySQL's GROUP BY requirements
- Use MySQL-specific functions where beneficial
            """,
            'sqlite': """
- Use simple SQLite syntax - avoid complex features
- Use LIMIT for pagination (simple and effective)
- Avoid window functions and advanced features
- Keep queries lightweight and efficient
            """,
            'mssql': """
- Use SQL Server TOP syntax instead of LIMIT
- Use square brackets for identifiers with spaces
- Leverage SQL Server's advanced analytics functions
- Use proper SQL Server pagination with OFFSET/FETCH
            """,
            'oracle': """
- Use Oracle ROWNUM for limiting results
- Use NULLS LAST for proper sorting
- Leverage Oracle's advanced SQL features
- Use dual table when needed for expressions
            """,
            'snowflake': """
- Use Snowflake's cloud-optimized SQL features
- Leverage powerful analytics and window functions
- Use proper LIMIT/OFFSET syntax
- Optimize for columnar storage patterns
            """,
            'bigquery': """
- Use BigQuery Standard SQL syntax
- Leverage BigQuery's powerful analytics functions
- Use proper dataset.table references
- Optimize for BigQuery's distributed architecture
            """,
            'redshift': """
- Use Redshift's PostgreSQL-compatible syntax
- Leverage columnar storage optimizations
- Use proper LIMIT syntax for large datasets
- Consider Redshift's distribution and sort keys
            """
        }
        
        optimization_guide = db_optimizations.get(db_type, "Use standard SQL syntax")
        
        prompt = f"""### Task
Generate optimized SQL for {db_name} database.

### Database: {db_name} ({db_type.upper()})
Optimization Guidelines:
{optimization_guide}

### Database Schema
{schema_text}

### User Request
{user_query}

### Optimized {db_name} SQL
```sql"""

        response = self.model(
            prompt,
            max_tokens=250,
            temperature=0.0,
            stop=["```", "</s>", "\n\n"],
            repeat_penalty=1.1
        )
        
        return self._clean_sql_response(response['choices'][0]['text'])
    
    def _generate_universal_sql(self, user_query: str, schema_json: Dict) -> str:
        """
        Generate universal SQL that works on most databases
        """
        schema_text = self._format_schema(schema_json)
        
        prompt = f"""### Task
Generate universal ANSI SQL that works on multiple databases.

### Universal SQL Rules
- Use only standard SQL: SELECT, FROM, WHERE, ORDER BY, GROUP BY, HAVING
- Use standard functions: COUNT(), AVG(), SUM(), MAX(), MIN()
- Avoid database-specific syntax
- Use single quotes for strings
- Use standard comparison operators

### Schema
{schema_text}

### Query
{user_query}

### Universal SQL
```sql"""

        response = self.model(
            prompt,
            max_tokens=200,
            temperature=0.0,
            stop=["```", "</s>", "\n\n"],
            repeat_penalty=1.1
        )
        
        return self._clean_sql_response(response['choices'][0]['text'])
    
    def _generate_pattern_based_sql(self, user_query: str, schema_json: Dict, db_info: Dict) -> str:
        """
        Generate SQL using pattern recognition (fallback method)
        """
        table_name = list(schema_json.keys())[0]
        columns = schema_json[table_name]
        query_lower = user_query.lower()
        
        # Extract common patterns
        if any(word in query_lower for word in ['top', 'highest', 'maximum']):
            numeric_col = self._find_numeric_column(columns)
            limit_match = re.search(r'\b(\d+)\b', user_query)
            limit = limit_match.group(1) if limit_match else '10'
            
            # Generate database-appropriate TOP N query
            if db_info['supports_limit']:
                return f"SELECT * FROM {table_name} ORDER BY {numeric_col} DESC LIMIT {limit}"
            elif db_info['type'] == 'mssql':
                return f"SELECT TOP {limit} * FROM {table_name} ORDER BY {numeric_col} DESC"
            else:  # Oracle
                return f"SELECT * FROM {table_name} WHERE ROWNUM <= {limit} ORDER BY {numeric_col} DESC"
        
        elif any(word in query_lower for word in ['count', 'total', 'how many']):
            return f"SELECT COUNT(*) as total FROM {table_name}"
        
        elif any(word in query_lower for word in ['average', 'mean']):
            numeric_col = self._find_numeric_column(columns)
            return f"SELECT AVG({numeric_col}) as average FROM {table_name}"
        
        else:
            # Default: show all with limit
            if db_info['supports_limit']:
                return f"SELECT * FROM {table_name} LIMIT 100"
            elif db_info['type'] == 'mssql':
                return f"SELECT TOP 100 * FROM {table_name}"
            else:
                return f"SELECT * FROM {table_name} WHERE ROWNUM <= 100"
    
    def _validate_request(self, user_query: str, schema_json: Dict) -> Dict[str, Any]:
        """Validate user request"""
        if not user_query or len(user_query.strip()) < 3:
            return {
                'is_valid': False,
                'error_message': 'Query is too short or empty.'
            }
        
        if not schema_json:
            return {
                'is_valid': False,
                'error_message': 'No database schema available.'
            }
        
        # Check for dangerous operations
        dangerous_keywords = ['drop', 'delete', 'truncate', 'alter', 'create', 'insert', 'update']
        query_lower = user_query.lower()
        
        for keyword in dangerous_keywords:
            if keyword in query_lower:
                return {
                    'is_valid': False,
                    'error_message': f'Cannot process "{keyword}" operations. Only SELECT queries are supported.'
                }
        
        return {'is_valid': True, 'error_message': None}
    
    def _validate_generated_sql(self, sql: str, schema_json: Dict) -> bool:
        """Validate generated SQL"""
        if not sql or len(sql.strip()) < 6:
            return False
        
        sql_upper = sql.upper().strip()
        
        # Must start with SELECT
        if not sql_upper.startswith('SELECT'):
            return False
        
        # Check table exists
        table_names = list(schema_json.keys())
        table_found = any(table.upper() in sql_upper for table in table_names)
        
        return table_found
    
    def _format_schema(self, schema_json: Dict) -> str:
        """Format schema for prompts"""
        formatted = []
        for table, columns in schema_json.items():
            formatted.append(f"Table {table} ({', '.join(columns)})")
        return "\n".join(formatted)
    
    def _clean_sql_response(self, response: str) -> str:
        """Clean AI response to get pure SQL"""
        if not response:
            return ""
        
        text = response.strip()
        
        # Remove code blocks
        text = re.sub(r'^```sql\n?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^```\n?', '', text)
        text = re.sub(r'\n?```$', '', text)
        
        # Remove prefixes
        prefixes = [r'^SQL:\s*', r'^Query:\s*', r'^Answer:\s*']
        for prefix in prefixes:
            text = re.sub(prefix, '', text, flags=re.IGNORECASE)
        
        return text.strip().rstrip(';')
    
    def _find_numeric_column(self, columns: list) -> str:
        """Find likely numeric column for sorting"""
        numeric_keywords = ['salary', 'price', 'amount', 'cost', 'value', 'score', 'id']
        
        for keyword in numeric_keywords:
            for col in columns:
                if keyword.lower() in col.lower():
                    return col
        
        return columns[0] if columns else 'id'
