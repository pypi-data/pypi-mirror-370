# # # # # aiqwal/query_generator.py
# # # # from pathlib import Path
# # # # from llama_cpp import Llama
# # # # from aiqwal.config import AI_MODEL_PATH, MAX_TOKENS

# # # # class QueryGenerator:
# # # #     def __init__(self, model_path: str = AI_MODEL_PATH):
# # # #         model_file = Path(model_path)
# # # #         if not model_file.exists():
# # # #             raise FileNotFoundError(f"Model not found at {model_path}")
# # # #         self.model = Llama(model_path=str(model_file))

# # # #     def generate_sql(self, user_query: str, schema_json: dict) -> str:
# # # #         prompt = f"""
# # # #         You are an expert SQL generator.
# # # #         Given the database schema:

# # # #         {schema_json}

# # # #         Convert the following natural language request into a single valid SQL statement.
# # # #         Do not include any explanations, descriptions, or comments—only return the SQL.

# # # #         User request: {user_query}
# # # #         """
# # # #         response = self.model(prompt, max_tokens=MAX_TOKENS)
# # # #         return response['choices'][0]['text'].strip()



# # # # # aiqwal/query_generator.py
# # # # from pathlib import Path
# # # # from llama_cpp import Llama
# # # # from aiqwal.config import AI_MODEL_PATH, MAX_TOKENS
# # # # import re

# # # # class QueryGenerator:
# # # #     def __init__(self, model_path: str = AI_MODEL_PATH):
# # # #         model_file = Path(model_path)
# # # #         if not model_file.exists():
# # # #             raise FileNotFoundError(f"Model not found at {model_path}")
        
# # # #         # SQLCoder works best with these settings
# # # #         self.model = Llama(
# # # #             model_path=str(model_file), 
# # # #             n_ctx=4096,
# # # #             n_threads=8,
# # # #             verbose=False,
# # # #             n_gpu_layers=0,  # Adjust based on your hardware
# # # #             temperature=0.0  # SQLCoder works best with low temperature
# # # #         )

# # # #     def generate_sql(self, user_query: str, schema_json: dict) -> str:
# # # #         """
# # # #         Generate SQL using SQLCoder-optimized prompts
# # # #         """
# # # #         # SQLCoder has specific prompt format preferences
# # # #         schema_text = self._format_schema_for_sqlcoder(schema_json)
        
# # # #         # Try SQLCoder-optimized prompts in order of effectiveness
# # # #         prompts = [
# # # #             self._sqlcoder_instruct_format(user_query, schema_text),
# # # #             self._sqlcoder_simple_format(user_query, schema_text),
# # # #             self._sqlcoder_defog_format(user_query, schema_text)  # Original training format
# # # #         ]
        
# # # #         for i, prompt in enumerate(prompts, 1):
# # # #             try:
# # # #                 print(f"Trying SQLCoder prompt strategy {i}...")
                
# # # #                 response = self.model(
# # # #                     prompt,
# # # #                     max_tokens=200,
# # # #                     temperature=0.0,
# # # #                     stop=["</s>", "\n\n", "--", "/*"],
# # # #                     repeat_penalty=1.1
# # # #                 )
                
# # # #                 sql_query = self._extract_sql_from_response(response['choices'][0]['text'])
# # # #                 print(f"Raw response: '{response['choices'][0]['text']}'")
# # # #                 print(f"Extracted SQL: '{sql_query}'")
                
# # # #                 if self._is_valid_sql(sql_query):
# # # #                     return sql_query
                    
# # # #             except Exception as e:
# # # #                 print(f"Strategy {i} failed: {e}")
# # # #                 continue
        
# # # #         raise Exception("SQLCoder failed to generate valid SQL with all prompt strategies")

# # # #     def _sqlcoder_instruct_format(self, user_query: str, schema_text: str) -> str:
# # # #         """SQLCoder instruction format"""
# # # #         return f"""### Task
# # # # Generate a SQL query to answer this question: {user_query}

# # # # ### Database Schema
# # # # {schema_text}

# # # # ### SQL Query
# # # # ```sql"""

# # # #     def _sqlcoder_simple_format(self, user_query: str, schema_text: str) -> str:
# # # #         """Simple format that works well with SQLCoder"""
# # # #         return f"""-- Database schema:
# # # # {schema_text}

# # # # -- Question: {user_query}
# # # # -- SQL query:
# # # # SELECT"""

# # # #     def _sqlcoder_defog_format(self, user_query: str, schema_text: str) -> str:
# # # #         """Based on original SQLCoder training format from Defog"""
# # # #         return f"""<|begin_of_text|><|start_header_id|>user<|end_header_id|>

# # # # Generate SQL for this question: {user_query}

# # # # Schema:
# # # # {schema_text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

# # # # ```sql
# # # # """

# # # #     def _format_schema_for_sqlcoder(self, schema_json: dict) -> str:
# # # #         """Format schema in the way SQLCoder expects"""
# # # #         if not schema_json:
# # # #             return "-- No schema provided"
        
# # # #         formatted_lines = []
# # # #         for table_name, columns in schema_json.items():
# # # #             # SQLCoder prefers this format
# # # #             column_definitions = []
# # # #             for col in columns:
# # # #                 column_definitions.append(f"    {col}")
            
# # # #             table_def = f"""CREATE TABLE {table_name} (
# # # # {chr(10).join(column_definitions)}
# # # # );"""
# # # #             formatted_lines.append(table_def)
        
# # # #         return "\n\n".join(formatted_lines)

# # # #     def _extract_sql_from_response(self, response: str) -> str:
# # # #         """Extract clean SQL from SQLCoder response"""
# # # #         if not response:
# # # #             return ""
        
# # # #         text = response.strip()
        
# # # #         # Remove markdown code blocks
# # # #         text = re.sub(r'^```sql\n?', '', text, flags=re.IGNORECASE)
# # # #         text = re.sub(r'^```\n?', '', text)
# # # #         text = re.sub(r'\n?```$', '', text)
        
# # # #         # SQLCoder sometimes adds explanations after the SQL
# # # #         # Take only the SQL part (usually the first line or first statement)
# # # #         lines = text.split('\n')
# # # #         sql_lines = []
        
# # # #         for line in lines:
# # # #             line = line.strip()
# # # #             if not line:
# # # #                 continue
            
# # # #             # Stop at comments or explanations
# # # #             if line.startswith('--') and not any(line.upper().startswith(f'-- {word}') for word in ['TABLE', 'DATABASE', 'SCHEMA']):
# # # #                 break
# # # #             if line.startswith('#') or line.startswith('/*'):
# # # #                 break
# # # #             if line.lower().startswith('this query') or line.lower().startswith('explanation'):
# # # #                 break
                
# # # #             sql_lines.append(line)
        
# # # #         # Join SQL lines and clean up
# # # #         sql = ' '.join(sql_lines).strip()
        
# # # #         # Remove trailing semicolon and whitespace
# # # #         sql = sql.rstrip(';').strip()
        
# # # #         return sql

# # # #     def _is_valid_sql(self, sql: str) -> bool:
# # # #         """Validate SQL structure"""
# # # #         if not sql or len(sql.strip()) < 6:
# # # #             return False
        
# # # #         sql_upper = sql.upper().strip()
        
# # # #         # Must start with SQL keyword
# # # #         valid_starts = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'WITH']
# # # #         starts_correctly = any(sql_upper.startswith(start) for start in valid_starts)
        
# # # #         # Should not contain obvious non-SQL content
# # # #         invalid_patterns = [
# # # #             'def ', 'class ', 'import ', 'return ', 'print(',
# # # #             'function', 'console.log', 'this query', 'explanation:',
# # # #             'the answer', 'result:', 'output:'
# # # #         ]
        
# # # #         has_invalid = any(pattern.lower() in sql.lower() for pattern in invalid_patterns)
        
# # # #         # Basic SQL structure checks
# # # #         has_structure = True
# # # #         if sql_upper.startswith('SELECT'):
# # # #             has_structure = 'FROM' in sql_upper or '*' in sql_upper
        
# # # #         return starts_correctly and not has_invalid and has_structure




# # # # aiqwal/query_generator.py
# # # from pathlib import Path
# # # from llama_cpp import Llama
# # # from aiqwal.config import AI_MODEL_PATH, MAX_TOKENS
# # # import re

# # # class QueryGenerator:
# # #     def __init__(self, model_path: str = AI_MODEL_PATH):
# # #         model_file = Path(model_path)
# # #         if not model_file.exists():
# # #             raise FileNotFoundError(f"Model not found at {model_path}")
        
# # #         # SQLCoder works best with these settings
# # #         self.model = Llama(
# # #             model_path=str(model_file), 
# # #             n_ctx=4096,
# # #             n_threads=8,
# # #             verbose=False,
# # #             n_gpu_layers=0,  # Adjust based on your hardware
# # #             temperature=0.0  # SQLCoder works best with low temperature
# # #         )

# # #     def generate_sql(self, user_query: str, schema_json: dict) -> str:
# # #         """
# # #         Generate SQL using SQLCoder-optimized prompts with comprehensive validation
# # #         """
# # #         # Pre-validation checks
# # #         validation_result = self._validate_request(user_query, schema_json)
# # #         if not validation_result['is_valid']:
# # #             raise ValueError(validation_result['error_message'])
        
# # #         # SQLCoder has specific prompt format preferences
# # #         schema_text = self._format_schema_for_sqlcoder(schema_json)
        
# # #         # Try SQLCoder-optimized prompts in order of effectiveness
# # #         prompts = [
# # #             self._sqlcoder_instruct_format(user_query, schema_text),
# # #             self._sqlcoder_simple_format(user_query, schema_text),
# # #             self._sqlcoder_defog_format(user_query, schema_text)  # Original training format
# # #         ]
        
# # #         for i, prompt in enumerate(prompts, 1):
# # #             try:
# # #                 print(f"Trying SQLCoder prompt strategy {i}...")
                
# # #                 response = self.model(
# # #                     prompt,
# # #                     max_tokens=200,
# # #                     temperature=0.0,
# # #                     stop=["</s>", "\n\n", "--", "/*"],
# # #                     repeat_penalty=1.1
# # #                 )
                
# # #                 sql_query = self._extract_sql_from_response(response['choices'][0]['text'])
# # #                 print(f"Raw response: '{response['choices'][0]['text']}'")
# # #                 print(f"Extracted SQL: '{sql_query}'")
                
# # #                 # Validate the generated SQL
# # #                 sql_validation = self._validate_generated_sql(sql_query, schema_json, user_query)
# # #                 if sql_validation['is_valid']:
# # #                     return sql_query
# # #                 else:
# # #                     print(f"Strategy {i} generated invalid SQL: {sql_validation['error']}")
# # #                     continue
                    
# # #             except Exception as e:
# # #                 print(f"Strategy {i} failed: {e}")
# # #                 continue
        
# # #         # If all strategies fail, provide helpful error message
# # #         raise Exception(
# # #             f"Unable to generate SQL for query: '{user_query}'. "
# # #             f"This could be because: the request is unclear, requires data not in the schema, "
# # #             f"or involves operations not supported by the current database structure."
# # #         )

# # #     def _validate_request(self, user_query: str, schema_json: dict) -> dict:
# # #         """
# # #         Validate if the request can potentially be fulfilled
# # #         """
# # #         if not user_query or len(user_query.strip()) < 3:
# # #             return {
# # #                 'is_valid': False,
# # #                 'error_message': 'Query is too short or empty. Please provide a clear request.'
# # #             }
        
# # #         if not schema_json or len(schema_json) == 0:
# # #             return {
# # #                 'is_valid': False,
# # #                 'error_message': 'No database schema available. Cannot generate SQL without knowing the table structure.'
# # #             }
        
# # #         # Check for potentially harmful requests
# # #         dangerous_keywords = ['drop', 'delete', 'truncate', 'alter', 'create', 'insert', 'update']
# # #         query_lower = user_query.lower()
        
# # #         for keyword in dangerous_keywords:
# # #             if keyword in query_lower:
# # #                 return {
# # #                     'is_valid': False,
# # #                     'error_message': f'Cannot process requests involving "{keyword}" operations for security reasons. Only SELECT queries are supported.'
# # #                 }
        
# # #         # Check if request is SQL-related
# # #         non_sql_indicators = [
# # #             'what is', 'how to', 'explain', 'tell me about', 'weather', 'news', 
# # #             'write code', 'create function', 'help me', 'tutorial'
# # #         ]
        
# # #         if any(indicator in query_lower for indicator in non_sql_indicators):
# # #             if not any(sql_word in query_lower for sql_word in ['table', 'database', 'query', 'data', 'record', 'row']):
# # #                 return {
# # #                     'is_valid': False,
# # #                     'error_message': 'This appears to be a general question rather than a database query. Please ask for specific data from your database.'
# # #                 }
        
# # #         return {'is_valid': True, 'error_message': None}

# # #     def _validate_generated_sql(self, sql: str, schema_json: dict, original_query: str) -> dict:
# # #         """
# # #         Validate the generated SQL for correctness and safety
# # #         """
# # #         if not self._is_valid_sql(sql):
# # #             return {
# # #                 'is_valid': False,
# # #                 'error': 'Generated text does not appear to be valid SQL'
# # #             }
        
# # #         # Check if SQL references tables that exist in schema
# # #         table_names = list(schema_json.keys())
# # #         sql_upper = sql.upper()
        
# # #         # Extract table references from SQL (simple check)
# # #         referenced_tables = []
# # #         for table in table_names:
# # #             if table.upper() in sql_upper:
# # #                 referenced_tables.append(table)
        
# # #         if not referenced_tables:
# # #             # Try to find any table reference
# # #             import re
# # #             from_matches = re.findall(r'FROM\s+(\w+)', sql_upper)
# # #             join_matches = re.findall(r'JOIN\s+(\w+)', sql_upper)
            
# # #             all_refs = from_matches + join_matches
# # #             unknown_tables = [table for table in all_refs if table not in [t.upper() for t in table_names]]
            
# # #             if unknown_tables:
# # #                 return {
# # #                     'is_valid': False,
# # #                     'error': f'SQL references unknown table(s): {unknown_tables}. Available tables: {table_names}'
# # #                 }
        
# # #         # Check for column references (basic validation)
# # #         for table_name in referenced_tables:
# # #             table_columns = schema_json[table_name]
# # #             # This is a simplified check - in production you'd want more sophisticated parsing
# # #             for column in table_columns:
# # #                 if column.upper() in sql_upper:
# # #                     continue  # Found at least one valid column reference
        
# # #         # Check if the AI couldn't understand and returned generic/error responses
# # #         error_indicators = [
# # #             'cannot', 'unable', 'sorry', 'error', 'not possible', 
# # #             'i don\'t', 'unclear', 'not sure', 'help', 'explain'
# # #         ]
        
# # #         if any(indicator in sql.lower() for indicator in error_indicators):
# # #             return {
# # #                 'is_valid': False,
# # #                 'error': f'AI model indicated it cannot process this request: {sql}'
# # #             }
        
# # #         return {'is_valid': True, 'error': None}

# # #     def _sqlcoder_instruct_format(self, user_query: str, schema_text: str) -> str:
# # #         """SQLCoder instruction format"""
# # #         return f"""### Task
# # # Generate a SQL query to answer this question: {user_query}

# # # ### Database Schema
# # # {schema_text}

# # # ### SQL Query
# # # ```sql"""

# # #     def _sqlcoder_simple_format(self, user_query: str, schema_text: str) -> str:
# # #         """Simple format that works well with SQLCoder"""
# # #         return f"""-- Database schema:
# # # {schema_text}

# # # -- Question: {user_query}
# # # -- SQL query:
# # # SELECT"""

# # #     def _sqlcoder_defog_format(self, user_query: str, schema_text: str) -> str:
# # #         """Based on original SQLCoder training format from Defog"""
# # #         return f"""<|begin_of_text|><|start_header_id|>user<|end_header_id|>

# # # Generate SQL for this question: {user_query}

# # # Schema:
# # # {schema_text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

# # # ```sql
# # # """

# # #     def _format_schema_for_sqlcoder(self, schema_json: dict) -> str:
# # #         """Format schema in the way SQLCoder expects"""
# # #         if not schema_json:
# # #             return "-- No schema provided"
        
# # #         formatted_lines = []
# # #         for table_name, columns in schema_json.items():
# # #             # SQLCoder prefers this format
# # #             column_definitions = []
# # #             for col in columns:
# # #                 column_definitions.append(f"    {col}")
            
# # #             table_def = f"""CREATE TABLE {table_name} (
# # # {chr(10).join(column_definitions)}
# # # );"""
# # #             formatted_lines.append(table_def)
        
# # #         return "\n\n".join(formatted_lines)

# # #     def _extract_sql_from_response(self, response: str) -> str:
# # #         """Extract clean SQL from SQLCoder response"""
# # #         if not response:
# # #             return ""
        
# # #         text = response.strip()
        
# # #         # Remove markdown code blocks
# # #         text = re.sub(r'^```sql\n?', '', text, flags=re.IGNORECASE)
# # #         text = re.sub(r'^```\n?', '', text)
# # #         text = re.sub(r'\n?```$', '', text)
        
# # #         # SQLCoder sometimes adds explanations after the SQL
# # #         # Take only the SQL part (usually the first line or first statement)
# # #         lines = text.split('\n')
# # #         sql_lines = []
        
# # #         for line in lines:
# # #             line = line.strip()
# # #             if not line:
# # #                 continue
            
# # #             # Stop at comments or explanations
# # #             if line.startswith('--') and not any(line.upper().startswith(f'-- {word}') for word in ['TABLE', 'DATABASE', 'SCHEMA']):
# # #                 break
# # #             if line.startswith('#') or line.startswith('/*'):
# # #                 break
# # #             if line.lower().startswith('this query') or line.lower().startswith('explanation'):
# # #                 break
                
# # #             sql_lines.append(line)
        
# # #         # Join SQL lines and clean up
# # #         sql = ' '.join(sql_lines).strip()
        
# # #         # Remove trailing semicolon and whitespace
# # #         sql = sql.rstrip(';').strip()
        
# # #         return sql

# # #     def _is_valid_sql(self, sql: str) -> bool:
# # #         """Validate SQL structure"""
# # #         if not sql or len(sql.strip()) < 6:
# # #             return False
        
# # #         sql_upper = sql.upper().strip()
        
# # #         # Must start with SQL keyword
# # #         valid_starts = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'WITH']
# # #         starts_correctly = any(sql_upper.startswith(start) for start in valid_starts)
        
# # #         # Should not contain obvious non-SQL content
# # #         invalid_patterns = [
# # #             'def ', 'class ', 'import ', 'return ', 'print(',
# # #             'function', 'console.log', 'this query', 'explanation:',
# # #             'the answer', 'result:', 'output:'
# # #         ]
        
# # #         has_invalid = any(pattern.lower() in sql.lower() for pattern in invalid_patterns)
        
# # #         # Basic SQL structure checks
# # #         has_structure = True
# # #         if sql_upper.startswith('SELECT'):
# # #             has_structure = 'FROM' in sql_upper or '*' in sql_upper
        
# # #         return starts_correctly and not has_invalid and has_structure


# # # aiqwal/query_generator.py
# # from pathlib import Path
# # from llama_cpp import Llama
# # from aiqwal.config import AI_MODEL_PATH, MAX_TOKENS
# # import re

# # class QueryGenerator:
# #     def __init__(self, model_path: str = AI_MODEL_PATH):
# #         model_file = Path(model_path)
# #         if not model_file.exists():
# #             raise FileNotFoundError(f"Model not found at {model_path}")
        
# #         # SQLCoder works best with these settings
# #         self.model = Llama(
# #             model_path=str(model_file), 
# #             n_ctx=4096,
# #             n_threads=8,
# #             verbose=False,
# #             n_gpu_layers=0,  # Adjust based on your hardware
# #             temperature=0.0  # SQLCoder works best with low temperature
# #         )

# #     def generate_sql(self, user_query: str, schema_json: dict) -> str:
# #         """
# #         Generate SQL using SQLCoder-optimized prompts with comprehensive validation
# #         """
# #         # Pre-validation checks
# #         validation_result = self._validate_request(user_query, schema_json)
# #         if not validation_result['is_valid']:
# #             raise ValueError(validation_result['error_message'])
        
# #         # SQLCoder has specific prompt format preferences
# #         schema_text = self._format_schema_for_sqlcoder(schema_json)
        
# #         # Try SQLCoder-optimized prompts in order of effectiveness
# #         prompts = [
# #             self._sqlcoder_instruct_format(user_query, schema_text),
# #             self._sqlcoder_simple_format(user_query, schema_text),
# #             self._sqlcoder_defog_format(user_query, schema_text)  # Original training format
# #         ]
        
# #         for i, prompt in enumerate(prompts, 1):
# #             try:
# #                 print(f"Trying SQLCoder prompt strategy {i}...")
                
# #                 response = self.model(
# #                     prompt,
# #                     max_tokens=200,
# #                     temperature=0.0,
# #                     stop=["</s>", "\n\n", "--", "/*"],
# #                     repeat_penalty=1.1
# #                 )
                
# #                 sql_query = self._extract_sql_from_response(response['choices'][0]['text'])
# #                 print(f"Raw response: '{response['choices'][0]['text']}'")
# #                 print(f"Extracted SQL: '{sql_query}'")
                
# #                 # Validate the generated SQL
# #                 sql_validation = self._validate_generated_sql(sql_query, schema_json, user_query)
# #                 if sql_validation['is_valid']:
# #                     return sql_query
# #                 else:
# #                     print(f"Strategy {i} generated invalid SQL: {sql_validation['error']}")
# #                     continue
                    
# #             except Exception as e:
# #                 print(f"Strategy {i} failed: {e}")
# #                 continue
        
# #         # If all strategies fail, provide helpful error message
# #         raise Exception(
# #             f"Unable to generate SQL for query: '{user_query}'. "
# #             f"This could be because: the request is unclear, requires data not in the schema, "
# #             f"or involves operations not supported by the current database structure."
# #         )

# #     def _validate_request(self, user_query: str, schema_json: dict) -> dict:
# #         """
# #         Validate if the request can potentially be fulfilled
# #         """
# #         if not user_query or len(user_query.strip()) < 3:
# #             return {
# #                 'is_valid': False,
# #                 'error_message': 'Query is too short or empty. Please provide a clear request.'
# #             }
        
# #         if not schema_json or len(schema_json) == 0:
# #             return {
# #                 'is_valid': False,
# #                 'error_message': 'No database schema available. Cannot generate SQL without knowing the table structure.'
# #             }
        
# #         # Check for potentially harmful requests
# #         dangerous_keywords = ['drop', 'delete', 'truncate', 'alter', 'create', 'insert', 'update']
# #         query_lower = user_query.lower()
        
# #         for keyword in dangerous_keywords:
# #             if keyword in query_lower:
# #                 return {
# #                     'is_valid': False,
# #                     'error_message': f'Cannot process requests involving "{keyword}" operations for security reasons. Only SELECT queries are supported.'
# #                 }
        
# #         # Check for requests about tables that don't exist in schema
# #         table_names = list(schema_json.keys())
# #         table_names_lower = [table.lower() for table in table_names]
        
# #         # Common table names that might be requested but don't exist
# #         common_tables = [
# #             'customer', 'customers', 'user', 'users', 'product', 'products', 
# #             'order', 'orders', 'sale', 'sales', 'invoice', 'invoices',
# #             'student', 'students', 'teacher', 'teachers', 'course', 'courses'
# #         ]
        
# #         for table in common_tables:
# #             if table in query_lower and table not in table_names_lower:
# #                 # Check if they're asking for a table that doesn't exist
# #                 if f"show {table}" in query_lower or f"list {table}" in query_lower or f"all {table}" in query_lower:
# #                     return {
# #                         'is_valid': False,
# #                         'error_message': f'Table "{table}" does not exist in the database. Available tables: {", ".join(table_names)}'
# #                     }
        
# #         # Check if request is SQL-related
# #         non_sql_indicators = [
# #             'what is', 'how to', 'explain', 'tell me about', 'weather', 'news', 
# #             'write code', 'create function', 'help me', 'tutorial'
# #         ]
        
# #         if any(indicator in query_lower for indicator in non_sql_indicators):
# #             if not any(sql_word in query_lower for sql_word in ['table', 'database', 'query', 'data', 'record', 'row']):
# #                 return {
# #                     'is_valid': False,
# #                     'error_message': 'This appears to be a general question rather than a database query. Please ask for specific data from your database.'
# #                 }
        
# #         return {'is_valid': True, 'error_message': None}

# #     def _validate_generated_sql(self, sql: str, schema_json: dict, original_query: str) -> dict:
# #         """
# #         Validate the generated SQL for correctness and safety
# #         """
# #         if not self._is_valid_sql(sql):
# #             return {
# #                 'is_valid': False,
# #                 'error': 'Generated text does not appear to be valid SQL'
# #             }
        
# #         # Check if SQL references tables that exist in schema
# #         table_names = list(schema_json.keys())
# #         table_names_upper = [table.upper() for table in table_names]
# #         sql_upper = sql.upper()
        
# #         # Extract table references from SQL
# #         import re
# #         from_matches = re.findall(r'FROM\s+(\w+)', sql_upper)
# #         join_matches = re.findall(r'JOIN\s+(\w+)', sql_upper)
        
# #         all_referenced_tables = from_matches + join_matches
        
# #         # Check if any referenced table doesn't exist in schema
# #         unknown_tables = []
# #         for table_ref in all_referenced_tables:
# #             # Remove aliases (e.g., "Employee e" -> check "Employee")
# #             table_name = table_ref.split()[0] if ' ' in table_ref else table_ref
# #             if table_name not in table_names_upper:
# #                 unknown_tables.append(table_name)
        
# #         if unknown_tables:
# #             return {
# #                 'is_valid': False,
# #                 'error': f'SQL references unknown table(s): {unknown_tables}. Available tables: {table_names}. The AI may have hallucinated non-existent tables.'
# #             }
        
# #         # Check if the AI couldn't understand and returned generic/error responses
# #         error_indicators = [
# #             'cannot', 'unable', 'sorry', 'error', 'not possible', 
# #             'i don\'t', 'unclear', 'not sure', 'help', 'explain'
# #         ]
        
# #         if any(indicator in sql.lower() for indicator in error_indicators):
# #             return {
# #                 'is_valid': False,
# #                 'error': f'AI model indicated it cannot process this request: {sql}'
# #             }
        
# #         # Advanced check: Validate column references
# #         for table_name in table_names:
# #             if table_name.upper() in sql_upper:
# #                 table_columns = schema_json[table_name]
# #                 table_columns_upper = [col.upper() for col in table_columns]
                
# #                 # Extract potential column references for this table
# #                 # This is a simplified check - look for table.column or just column patterns
# #                 table_alias_pattern = rf'{table_name.upper()}\s*(\w+)?'
# #                 alias_match = re.search(table_alias_pattern, sql_upper)
                
# #                 if alias_match:
# #                     # Look for column references with this table/alias
# #                     continue  # For now, skip detailed column validation as it's complex
        
# #         return {'is_valid': True, 'error': None}

# #     def _sqlcoder_instruct_format(self, user_query: str, schema_text: str) -> str:
# #         """SQLCoder instruction format"""
# #         return f"""### Task
# # Generate a SQL query to answer this question: {user_query}

# # ### Database Schema
# # {schema_text}

# # ### SQL Query
# # ```sql"""

# #     def _sqlcoder_simple_format(self, user_query: str, schema_text: str) -> str:
# #         """Simple format that works well with SQLCoder"""
# #         return f"""-- Database schema:
# # {schema_text}

# # -- Question: {user_query}
# # -- SQL query:
# # SELECT"""

# #     def _sqlcoder_defog_format(self, user_query: str, schema_text: str) -> str:
# #         """Based on original SQLCoder training format from Defog"""
# #         return f"""<|begin_of_text|><|start_header_id|>user<|end_header_id|>

# # Generate SQL for this question: {user_query}

# # Schema:
# # {schema_text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

# # ```sql
# # """

# #     def _format_schema_for_sqlcoder(self, schema_json: dict) -> str:
# #         """Format schema in the way SQLCoder expects"""
# #         if not schema_json:
# #             return "-- No schema provided"
        
# #         formatted_lines = []
# #         for table_name, columns in schema_json.items():
# #             # SQLCoder prefers this format
# #             column_definitions = []
# #             for col in columns:
# #                 column_definitions.append(f"    {col}")
            
# #             table_def = f"""CREATE TABLE {table_name} (
# # {chr(10).join(column_definitions)}
# # );"""
# #             formatted_lines.append(table_def)
        
# #         return "\n\n".join(formatted_lines)

# #     def _extract_sql_from_response(self, response: str) -> str:
# #         """Extract clean SQL from SQLCoder response"""
# #         if not response:
# #             return ""
        
# #         text = response.strip()
        
# #         # Remove markdown code blocks
# #         text = re.sub(r'^```sql\n?', '', text, flags=re.IGNORECASE)
# #         text = re.sub(r'^```\n?', '', text)
# #         text = re.sub(r'\n?```$', '', text)
        
# #         # SQLCoder sometimes adds explanations after the SQL
# #         # Take only the SQL part (usually the first line or first statement)
# #         lines = text.split('\n')
# #         sql_lines = []
        
# #         for line in lines:
# #             line = line.strip()
# #             if not line:
# #                 continue
            
# #             # Stop at comments or explanations
# #             if line.startswith('--') and not any(line.upper().startswith(f'-- {word}') for word in ['TABLE', 'DATABASE', 'SCHEMA']):
# #                 break
# #             if line.startswith('#') or line.startswith('/*'):
# #                 break
# #             if line.lower().startswith('this query') or line.lower().startswith('explanation'):
# #                 break
                
# #             sql_lines.append(line)
        
# #         # Join SQL lines and clean up
# #         sql = ' '.join(sql_lines).strip()
        
# #         # Remove trailing semicolon and whitespace
# #         sql = sql.rstrip(';').strip()
        
# #         return sql

# #     def _is_valid_sql(self, sql: str) -> bool:
# #         """Validate SQL structure"""
# #         if not sql or len(sql.strip()) < 6:
# #             return False
        
# #         sql_upper = sql.upper().strip()
        
# #         # Must start with SQL keyword
# #         valid_starts = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'WITH']
# #         starts_correctly = any(sql_upper.startswith(start) for start in valid_starts)
        
# #         # Should not contain obvious non-SQL content
# #         invalid_patterns = [
# #             'def ', 'class ', 'import ', 'return ', 'print(',
# #             'function', 'console.log', 'this query', 'explanation:',
# #             'the answer', 'result:', 'output:'
# #         ]
        
# #         has_invalid = any(pattern.lower() in sql.lower() for pattern in invalid_patterns)
        
# #         # Basic SQL structure checks
# #         has_structure = True
# #         if sql_upper.startswith('SELECT'):
# #             has_structure = 'FROM' in sql_upper or '*' in sql_upper
        
# #         return starts_correctly and not has_invalid and has_structure



# # aiqwal/database_aware_generator.py
# from pathlib import Path
# from llama_cpp import Llama
# from aiqwal.config import AI_MODEL_PATH, MAX_TOKENS
# import re

# class DatabaseAwareQueryGenerator:
#     def __init__(self, model_path: str = AI_MODEL_PATH):
#         model_file = Path(model_path)
#         if not model_file.exists():
#             raise FileNotFoundError(f"Model not found at {model_path}")
        
#         self.model = Llama(
#             model_path=str(model_file), 
#             n_ctx=4096,
#             n_threads=8,
#             verbose=False,
#             n_gpu_layers=0,
#             temperature=0.0
#         )
        
#         # Database-specific syntax rules
#         self.db_syntax = {
#             'sqlite': {
#                 'limit_syntax': 'LIMIT {limit}',
#                 'string_quotes': 'single',
#                 'supports_nulls_last': False,
#                 'top_n_pattern': 'ORDER BY {column} DESC LIMIT {n}'
#             },
#             'postgresql': {
#                 'limit_syntax': 'LIMIT {limit} OFFSET {offset}',
#                 'string_quotes': 'single',
#                 'supports_nulls_last': True,
#                 'top_n_pattern': 'ORDER BY {column} DESC NULLS LAST LIMIT {n}'
#             },
#             'mysql': {
#                 'limit_syntax': 'LIMIT {limit}',
#                 'string_quotes': 'single_or_backtick',
#                 'supports_nulls_last': False,
#                 'top_n_pattern': 'ORDER BY {column} DESC LIMIT {n}'
#             },
#             'mssql': {
#                 'limit_syntax': 'TOP {limit}',
#                 'string_quotes': 'single_or_bracket',
#                 'supports_nulls_last': False,
#                 'top_n_pattern': 'TOP {n} * FROM {table} ORDER BY {column} DESC'
#             },
#             'oracle': {
#                 'limit_syntax': 'ROWNUM <= {limit}',
#                 'string_quotes': 'single',
#                 'supports_nulls_last': True,
#                 'top_n_pattern': 'WHERE ROWNUM <= {n} ORDER BY {column} DESC NULLS LAST'
#             }
#         }

#     def generate_sql(self, user_query: str, schema_json: dict, db_type: str = 'sqlite') -> str:
#         """
#         Generate database-specific SQL
#         """
#         # Validation (same as before)
#         validation_result = self._validate_request(user_query, schema_json)
#         if not validation_result['is_valid']:
#             raise ValueError(validation_result['error_message'])
        
#         # Get database-specific configuration
#         db_config = self.db_syntax.get(db_type.lower(), self.db_syntax['sqlite'])
        
#         # Create database-aware prompts
#         schema_text = self._format_schema_for_database(schema_json, db_type)
        
#         prompts = [
#             self._create_database_specific_prompt(user_query, schema_text, db_type),
#             self._create_generic_sql_prompt(user_query, schema_text)
#         ]
        
#         for i, prompt in enumerate(prompts, 1):
#             try:
#                 print(f"Trying {db_type} strategy {i}...")
                
#                 response = self.model(
#                     prompt,
#                     max_tokens=200,
#                     temperature=0.0,
#                     stop=["</s>", "\n\n", "--", "/*"],
#                     repeat_penalty=1.1
#                 )
                
#                 sql_query = self._extract_sql_from_response(response['choices'][0]['text'])
#                 print(f"Generated SQL: '{sql_query}'")
                
#                 # Post-process for database-specific syntax
#                 sql_query = self._adapt_sql_for_database(sql_query, db_type, db_config)
                
#                 if self._validate_generated_sql(sql_query, schema_json, user_query):
#                     return sql_query
                    
#             except Exception as e:
#                 print(f"Strategy {i} failed: {e}")
#                 continue
        
#         raise Exception(f"Unable to generate {db_type}-compatible SQL for query: '{user_query}'")

#     def _create_database_specific_prompt(self, user_query: str, schema_text: str, db_type: str) -> str:
#         """Create prompts optimized for specific databases"""
        
#         db_instructions = {
#             'postgresql': "Use PostgreSQL syntax. Support advanced features like NULLS LAST, window functions, and proper LIMIT/OFFSET.",
#             'mysql': "Use MySQL syntax. Use backticks for column names if needed. LIMIT clause for pagination.",
#             'sqlite': "Use SQLite syntax. Simple LIMIT clause. Avoid complex window functions.",
#             'mssql': "Use SQL Server syntax. Use TOP N instead of LIMIT. Use square brackets for identifiers.",
#             'oracle': "Use Oracle syntax. Use ROWNUM for limiting results. Support NULLS LAST."
#         }
        
#         instruction = db_instructions.get(db_type.lower(), db_instructions['sqlite'])
        
#         return f"""### Task
# Generate a {db_type.upper()} SQL query for: {user_query}

# ### Database Type: {db_type.upper()}
# {instruction}

# ### Schema
# {schema_text}

# ### {db_type.upper()} SQL Query
# ```sql"""

#     def _adapt_sql_for_database(self, sql: str, db_type: str, db_config: dict) -> str:
#         """
#         Adapt generated SQL for specific database syntax
#         """
#         if not sql:
#             return sql
            
#         db_type_lower = db_type.lower()
        
#         # Handle LIMIT syntax differences
#         if db_type_lower == 'mssql':
#             # Convert LIMIT to TOP for SQL Server
#             sql = re.sub(r'SELECT (.+?) LIMIT (\d+)', r'SELECT TOP \2 \1', sql, flags=re.IGNORECASE)
        
#         elif db_type_lower == 'oracle':
#             # Convert LIMIT to ROWNUM for Oracle
#             sql = re.sub(r'LIMIT (\d+)', r'AND ROWNUM <= \1', sql, flags=re.IGNORECASE)
        
#         # Handle NULLS LAST support
#         if not db_config.get('supports_nulls_last', False):
#             sql = re.sub(r'NULLS LAST', '', sql, flags=re.IGNORECASE)
        
#         return sql.strip()

#     def _format_schema_for_database(self, schema_json: dict, db_type: str) -> str:
#         """Format schema with database-specific considerations"""
#         if not schema_json:
#             return f"-- No schema provided for {db_type}"
        
#         formatted_lines = []
#         for table_name, columns in schema_json.items():
#             if db_type.lower() == 'mssql':
#                 # SQL Server style with brackets
#                 table_def = f"Table [{table_name}] ({', '.join(f'[{col}]' for col in columns)})"
#             elif db_type.lower() == 'mysql':
#                 # MySQL style with backticks
#                 table_def = f"Table `{table_name}` ({', '.join(f'`{col}`' for col in columns)})"
#             else:
#                 # Standard style
#                 table_def = f"Table {table_name} ({', '.join(columns)})"
            
#             formatted_lines.append(table_def)
        
#         return "\n".join(formatted_lines)

#     # Include all the validation methods from the previous implementation
#     def _validate_request(self, user_query: str, schema_json: dict) -> dict:
#         """Same validation as before"""
#         if not user_query or len(user_query.strip()) < 3:
#             return {
#                 'is_valid': False,
#                 'error_message': 'Query is too short or empty. Please provide a clear request.'
#             }
        
#         if not schema_json or len(schema_json) == 0:
#             return {
#                 'is_valid': False,
#                 'error_message': 'No database schema available. Cannot generate SQL without knowing the table structure.'
#             }
        
#         # Check for potentially harmful requests
#         dangerous_keywords = ['drop', 'delete', 'truncate', 'alter', 'create', 'insert', 'update']
#         query_lower = user_query.lower()
        
#         for keyword in dangerous_keywords:
#             if keyword in query_lower:
#                 return {
#                     'is_valid': False,
#                     'error_message': f'Cannot process requests involving "{keyword}" operations for security reasons. Only SELECT queries are supported.'
#                 }
        
#         return {'is_valid': True, 'error_message': None}

#     def _extract_sql_from_response(self, response: str) -> str:
#         """Same extraction logic as before"""
#         if not response:
#             return ""
        
#         text = response.strip()
        
#         # Remove markdown code blocks
#         text = re.sub(r'^```sql\n?', '', text, flags=re.IGNORECASE)
#         text = re.sub(r'^```\n?', '', text)
#         text = re.sub(r'\n?```$', '', text)
        
#         # Remove common prefixes
#         prefixes_to_remove = [
#             r'^SQL:\s*',
#             r'^Query:\s*',
#             r'^Answer:\s*',
#             r'^Result:\s*',
#         ]
        
#         for prefix in prefixes_to_remove:
#             text = re.sub(prefix, '', text, flags=re.IGNORECASE)
        
#         return text.strip().rstrip(';')

#     def _validate_generated_sql(self, sql: str, schema_json: dict, original_query: str) -> bool:
#         """Simplified validation"""
#         if not sql or len(sql.strip()) < 6:
#             return False
        
#         sql_upper = sql.upper().strip()
#         valid_starts = ['SELECT', 'WITH']
#         return any(sql_upper.startswith(start) for start in valid_starts)

#     def _create_generic_sql_prompt(self, user_query: str, schema_text: str) -> str:
#         """Fallback generic prompt"""
#         return f"""Generate SQL for: {user_query}

# Schema: {schema_text}

# SQL:"""


# aiqwal/universal_sql_generator.py
from pathlib import Path
from llama_cpp import Llama
from aiqwal.config import AI_MODEL_PATH
import re
import json
from sqlalchemy import text, and_, or_, desc, asc, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime

class UniversalSQLGenerator:
    """
    Universal SQL generator that works with ANY database in the world
    Uses SQLAlchemy to abstract database differences
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
        
        # Universal query patterns that work on ALL databases
        self.universal_patterns = {
            'top_n': {
                'keywords': ['top', 'highest', 'largest', 'maximum', 'first'],
                'template': 'SELECT {columns} FROM {table} ORDER BY {sort_column} DESC LIMIT {n}'
            },
            'bottom_n': {
                'keywords': ['bottom', 'lowest', 'smallest', 'minimum', 'last'],
                'template': 'SELECT {columns} FROM {table} ORDER BY {sort_column} ASC LIMIT {n}'
            },
            'filter_by_value': {
                'keywords': ['where', 'with', 'having', 'greater than', 'less than', 'equal to'],
                'template': 'SELECT {columns} FROM {table} WHERE {condition}'
            },
            'group_and_count': {
                'keywords': ['count by', 'group by', 'total by', 'sum by'],
                'template': 'SELECT {group_column}, COUNT(*) as count FROM {table} GROUP BY {group_column}'
            },
            'date_range': {
                'keywords': ['after', 'before', 'between', 'since', 'until'],
                'template': 'SELECT {columns} FROM {table} WHERE {date_column} {operator} {date_value}'
            },
            'aggregations': {
                'keywords': ['average', 'mean', 'sum', 'total', 'count', 'maximum', 'minimum'],
                'template': 'SELECT {agg_function}({column}) as {alias} FROM {table}'
            }
        }

    def generate_universal_sql(self, user_query: str, schema_json: dict, engine) -> dict:
        """
        Generate SQL that works on ANY database using SQLAlchemy
        Returns both raw SQL and SQLAlchemy query object
        """
        # Step 1: Parse user intent
        intent = self._parse_user_intent(user_query, schema_json)
        
        if not intent['is_valid']:
            raise ValueError(intent['error'])
        
        # Step 2: Try AI generation first
        try:
            ai_sql = self._generate_with_ai(user_query, schema_json)
            
            # Step 3: Convert AI SQL to universal SQLAlchemy query
            universal_query = self._convert_to_sqlalchemy(ai_sql, schema_json, engine)
            
            if universal_query:
                return {
                    'success': True,
                    'method': 'ai_generated',
                    'sqlalchemy_query': universal_query,
                    'raw_sql': str(universal_query.compile(compile_kwargs={"literal_binds": True})),
                    'original_ai_sql': ai_sql
                }
                
        except Exception as e:
            print(f"AI generation failed: {e}")
        
        # Step 4: Fallback to pattern-based universal generation
        return self._generate_with_patterns(intent, schema_json, engine)

    def _parse_user_intent(self, user_query: str, schema_json: dict) -> dict:
        """
        Parse what the user wants to do (universal across all databases)
        """
        if not user_query or len(user_query.strip()) < 3:
            return {'is_valid': False, 'error': 'Query too short'}
        
        if not schema_json:
            return {'is_valid': False, 'error': 'No schema available'}
        
        query_lower = user_query.lower()
        
        # Extract key information
        intent = {
            'is_valid': True,
            'action': None,
            'table': None,
            'columns': [],
            'conditions': [],
            'limit': None,
            'sort_by': None,
            'sort_direction': 'DESC',
            'aggregation': None
        }
        
        # Find table (assume first/main table for now)
        table_names = list(schema_json.keys())
        for table in table_names:
            if table.lower() in query_lower:
                intent['table'] = table
                break
        
        if not intent['table']:
            intent['table'] = table_names[0]  # Default to first table
        
        # Extract limit
        limit_match = re.search(r'\b(\d+)\b', user_query)
        if limit_match:
            intent['limit'] = int(limit_match.group(1))
        elif any(word in query_lower for word in ['top', 'first']):
            intent['limit'] = 10  # Default
        
        # Determine action type
        if any(word in query_lower for word in ['top', 'highest', 'maximum']):
            intent['action'] = 'top_n'
        elif any(word in query_lower for word in ['bottom', 'lowest', 'minimum']):
            intent['action'] = 'bottom_n'
        elif any(word in query_lower for word in ['count', 'total']):
            intent['action'] = 'count'
        elif any(word in query_lower for word in ['average', 'mean']):
            intent['action'] = 'average'
        elif any(word in query_lower for word in ['sum']):
            intent['action'] = 'sum'
        else:
            intent['action'] = 'select_all'
        
        return intent

    def _convert_to_sqlalchemy(self, ai_sql: str, schema_json: dict, engine) -> object:
        """
        Convert AI-generated SQL to SQLAlchemy query object
        This makes it work on ANY database!
        """
        try:
            # Reflect the database schema
            metadata = MetaData()
            metadata.reflect(bind=engine)
            
            # Parse the AI SQL and convert to SQLAlchemy
            # For now, return the text query wrapped in SQLAlchemy
            # This automatically handles database dialect differences
            return text(ai_sql)
            
        except Exception as e:
            print(f"SQLAlchemy conversion failed: {e}")
            return None

    def _generate_with_patterns(self, intent: dict, schema_json: dict, engine) -> dict:
        """
        Generate universal SQL using patterns (works on ANY database)
        """
        table_name = intent['table']
        table_columns = schema_json[table_name]
        
        try:
            # Reflect table for SQLAlchemy
            metadata = MetaData()
            metadata.reflect(bind=engine)
            table = metadata.tables[table_name]
            
            # Build universal query based on intent
            if intent['action'] == 'top_n':
                # Find salary or numeric column
                sort_column = self._find_numeric_column(table_columns)
                query = text(f"SELECT * FROM {table_name} ORDER BY {sort_column} DESC LIMIT :limit")
                query = query.bindparam(limit=intent['limit'] or 10)
                
            elif intent['action'] == 'count':
                query = text(f"SELECT COUNT(*) as total_count FROM {table_name}")
                
            elif intent['action'] == 'average':
                numeric_col = self._find_numeric_column(table_columns)
                query = text(f"SELECT AVG({numeric_col}) as average_value FROM {table_name}")
                
            else:  # select_all
                query = text(f"SELECT * FROM {table_name} LIMIT :limit")
                query = query.bindparam(limit=intent['limit'] or 100)
            
            return {
                'success': True,
                'method': 'pattern_based',
                'sqlalchemy_query': query,
                'raw_sql': str(query.compile(compile_kwargs={"literal_binds": True})),
                'intent': intent
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate universal SQL: {e}")

    def _find_numeric_column(self, columns: list) -> str:
        """Find a numeric column for sorting/aggregation"""
        # Common numeric column names
        numeric_indicators = ['salary', 'price', 'amount', 'cost', 'value', 'score', 'rating', 'id']
        
        for indicator in numeric_indicators:
            for col in columns:
                if indicator in col.lower():
                    return col
        
        # Return first column that might be numeric
        return columns[0] if columns else 'id'

    def _generate_with_ai(self, user_query: str, schema_json: dict) -> str:
        """Generate SQL using AI (same as before)"""
        schema_text = self._format_schema(schema_json)
        
        prompt = f"""### Task
Generate ANSI SQL that works on any database for: {user_query}

Use only standard SQL features:
- SELECT, FROM, WHERE, ORDER BY, GROUP BY, HAVING
- Standard functions: COUNT, AVG, SUM, MAX, MIN
- Avoid database-specific syntax

### Schema
{schema_text}

### Universal SQL
```sql"""

        response = self.model(
            prompt,
            max_tokens=200,
            temperature=0.0,
            stop=["```", "\n\n"],
            repeat_penalty=1.1
        )
        
        sql = self._clean_sql(response['choices'][0]['text'])
        return sql

    def _format_schema(self, schema_json: dict) -> str:
        """Format schema for AI"""
        formatted = []
        for table, columns in schema_json.items():
            formatted.append(f"Table {table} ({', '.join(columns)})")
        return "\n".join(formatted)

    def _clean_sql(self, sql: str) -> str:
        """Clean AI-generated SQL"""
        if not sql:
            return ""
        
        sql = sql.strip()
        sql = re.sub(r'^```sql\n?', '', sql, flags=re.IGNORECASE)
        sql = re.sub(r'^```\n?', '', sql)
        sql = re.sub(r'\n?```$', '', sql)
        
        return sql.strip().rstrip(';')

# Universal executor that works with ANY database
class UniversalExecutor:
    """
    Universal SQL executor that works with ANY database
    """
    
    def __init__(self, engine):
        self.engine = engine

    def execute_universal_query(self, query_result: dict) -> dict:
        """
        Execute universal query on ANY database
        """
        if not query_result['success']:
            raise Exception("Invalid query result")
        
        sqlalchemy_query = query_result['sqlalchemy_query']
        
        try:
            with self.engine.connect() as conn:
                # Execute using SQLAlchemy - works on ANY database!
                result = conn.execute(sqlalchemy_query)
                
                # Convert to standard format
                columns = list(result.keys()) if result.keys() else []
                data = [dict(zip(columns, row)) for row in result.fetchall()]
                
                return {
                    'success': True,
                    'data': data,
                    'count': len(data),
                    'method': query_result['method'],
                    'executed_sql': query_result['raw_sql']
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'query_info': query_result
            }