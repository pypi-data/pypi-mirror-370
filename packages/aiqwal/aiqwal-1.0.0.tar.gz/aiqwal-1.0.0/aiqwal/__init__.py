# # aiqwal/__init__.py - Simple one-line import setup

# """
# AIQWAL - AI Query Writer for Any Language
# Just one import: from aiqwal import AIQWAL
# """

# # Import all your existing components
# from .ultimate_database_manager import UltimateDatabaseManager
# from .ultimate_query_generator import UltimateQueryGenerator  
# from .ultimate_executor import UltimateExecutor
# from .nlp_response_generator import NLPResponseGenerator
# from .utils import log_info, log_error

# class AIQWAL:
#     """
#     Main AIQWAL class - One import to rule them all!
    
#     Usage:
#         from aiqwal import AIQWAL
#         ai = AIQWAL('your-connection-string')
#         results = ai.query('How many users do I have?')
#     """
    
#     def __init__(self, connection_string: str, **kwargs):
#         """Initialize AIQWAL with any database connection"""
#         self.connection_string = connection_string
#         self.db_manager = None
#         self.query_generator = None
#         self.executor = None
#         self.nlp_responder = None
#         self.connected = False
        
#         # Auto-connect by default
#         if kwargs.get('auto_connect', True):
#             self.connect()
    
#     def connect(self):
#         """Connect and initialize all components"""
#         try:
#             print("🔗 Connecting to database...")
            
#             # Initialize database manager
#             self.db_manager = UltimateDatabaseManager(self.connection_string)
#             connection_result = self.db_manager.connect()
            
#             if not connection_result['success']:
#                 raise Exception(f"Connection failed: {connection_result.get('error')}")
            
#             # Initialize AI components
#             print("🤖 Loading AI components...")
#             self.query_generator = UltimateQueryGenerator()
#             self.executor = UltimateExecutor(self.db_manager)
#             self.nlp_responder = NLPResponseGenerator()
            
#             self.connected = True
#             print("✅ AIQWAL ready!")
            
#             return connection_result
            
#         except Exception as e:
#             raise Exception(f"AIQWAL initialization failed: {str(e)}")
    
#     def query(self, natural_language_query: str, limit: int = None):
#         """
#         Ask your database anything in natural language!
        
#         Args:
#             natural_language_query: Your question in plain English
#             limit: Optional result limit
            
#         Returns:
#             Query results as list of dictionaries
#         """
#         if not self.connected:
#             self.connect()
        
#         try:
#             # Get schema
#             schema = self.db_manager.get_schema()
            
#             # Generate SQL using AI
#             sql = self.query_generator.generate_sql(
#                 natural_language_query, 
#                 schema, 
#                 self.db_manager
#             )
            
#             # Execute SQL
#             result = self.executor.run_query(sql, limit_results=limit)
            
#             if result['success']:
#                 return result['data']
#             else:
#                 raise Exception(f"Query failed: {result['error']}")
                
#         except Exception as e:
#             raise Exception(f"Query processing failed: {str(e)}")
    
#     def query_with_explanation(self, natural_language_query: str, limit: int = None):
#         """
#         Ask question and get AI explanation of results
        
#         Returns:
#             dict with 'results', 'explanation', 'sql', 'suggestions'
#         """
#         if not self.connected:
#             self.connect()
        
#         try:
#             # Get schema
#             schema = self.db_manager.get_schema()
            
#             # Generate SQL using AI
#             sql = self.query_generator.generate_sql(
#                 natural_language_query, 
#                 schema, 
#                 self.db_manager
#             )
            
#             # Execute SQL
#             result = self.executor.run_query(sql, limit_results=limit)
            
#             if result['success']:
#                 # Generate natural language explanation
#                 explanation = self.nlp_responder.generate_natural_response(
#                     original_question=natural_language_query,
#                     sql_query=sql,
#                     results=result['data'],
#                     execution_time=result['execution_time']
#                 )
                
#                 # Generate follow-up suggestions
#                 suggestions = self.nlp_responder.generate_contextual_followup_suggestions(
#                     natural_language_query, result['data']
#                 )
                
#                 return {
#                     'results': result['data'],
#                     'explanation': explanation,
#                     'sql': sql,
#                     'suggestions': suggestions,
#                     'execution_time': result['execution_time'],
#                     'count': result['count']
#                 }
#             else:
#                 raise Exception(f"Query failed: {result['error']}")
                
#         except Exception as e:
#             raise Exception(f"Query processing failed: {str(e)}")
    
#     def get_schema(self):
#         """Get database schema"""
#         if not self.connected:
#             self.connect()
#         return self.db_manager.get_schema()
    
#     def get_info(self):
#         """Get database information"""
#         if not self.connected:
#             self.connect()
#         return self.db_manager.get_database_info()

# # Convenience functions for even simpler usage
# def quick_query(connection_string: str, question: str):
#     """One-liner for quick queries"""
#     ai = AIQWAL(connection_string)
#     return ai.query(question)

# def smart_query(connection_string: str, question: str):
#     """One-liner with AI explanations"""
#     ai = AIQWAL(connection_string)
#     return ai.query_with_explanation(question)

# # Export the main class and convenience functions
# __all__ = ['AIQWAL', 'quick_query', 'smart_query']

# # Version info
# __version__ = '1.0.0'
# __author__ = 'AIQWAL Team'



# # aiqwal_client/__init__.py
# """
# AIQWAL Client - AI Query Writer for Any Language
# Simple client interface for natural language database queries

# Usage:
#     from aiqwal_client import AIQwal
    
#     client = AIQwal('your-database-connection-string')
#     results = client.ask('How many users do I have?')
# """

# # Import your existing components (keep the internal structure)
# import sys
# import os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from aiqwal.ultimate_database_manager import UltimateDatabaseManager
# from aiqwal.ultimate_query_generator import UltimateQueryGenerator  
# from aiqwal.ultimate_executor import UltimateExecutor
# from aiqwal.nlp_response_generator import NLPResponseGenerator

# class AIQwal:
#     """
#     AIQwal Client - Your AI Database Assistant
    
#     Simple, clean interface for natural language database queries
    
#     Usage:
#         from aiqwal_client import AIQwal
        
#         client = AIQwal('postgresql://user:pass@host:5432/db')
#         results = client.ask('How many customers do I have?')
#         print(results)
#     """
    
#     def __init__(self, connection_string: str, auto_connect: bool = True):
#         """
#         Initialize AIQwal client
        
#         Args:
#             connection_string: Database connection string
#             auto_connect: Connect automatically on initialization
#         """
#         self.connection_string = connection_string
#         self.db_manager = None
#         self.query_generator = None
#         self.executor = None
#         self.nlp_responder = None
#         self.connected = False
        
#         if auto_connect:
#             self.connect()
    
#     def connect(self):
#         """Connect to database and load AI models"""
#         try:
#             print("🔗 Connecting to database...")
            
#             # Initialize database connection
#             self.db_manager = UltimateDatabaseManager(self.connection_string)
#             connection_result = self.db_manager.connect()
            
#             if not connection_result['success']:
#                 raise Exception(f"Connection failed: {connection_result.get('error')}")
            
#             print(f"✅ Connected to {connection_result['database']}")
            
#             # Initialize AI components
#             print("🤖 Loading AI models...")
#             self.query_generator = UltimateQueryGenerator()
#             self.executor = UltimateExecutor(self.db_manager)
#             self.nlp_responder = NLPResponseGenerator()
            
#             self.connected = True
#             print("🎉 AIQwal client ready!")
            
#             return True
            
#         except Exception as e:
#             raise Exception(f"AIQwal initialization failed: {str(e)}")
    
#     def ask(self, question: str, limit: int = None):
#         """
#         Ask your database a question in natural language
        
#         Args:
#             question: Your question in plain English
#             limit: Optional limit on number of results
            
#         Returns:
#             List of results as dictionaries
            
#         Example:
#             results = client.ask("How many orders were placed today?")
#             results = client.ask("Show me top 10 customers by revenue")
#         """
#         if not self.connected:
#             self.connect()
        
#         try:
#             schema = self.db_manager.get_schema()
            
#             # Generate SQL from natural language
#             sql = self.query_generator.generate_sql(question, schema, self.db_manager)
            
#             # Execute the query
#             result = self.executor.run_query(sql, limit_results=limit)
            
#             if result['success']:
#                 return result['data']
#             else:
#                 raise Exception(f"Query execution failed: {result['error']}")
                
#         except Exception as e:
#             raise Exception(f"Failed to process question: {str(e)}")
    
#     def ask_smart(self, question: str, limit: int = None):
#         """
#         Ask question and get AI explanation of the results
        
#         Args:
#             question: Your question in plain English
#             limit: Optional limit on results
            
#         Returns:
#             Dictionary with results, explanation, and suggestions
            
#         Example:
#             response = client.ask_smart("What's our customer retention rate?")
#             print(response['explanation'])  # AI explanation
#             print(response['results'])      # Raw data
#             print(response['suggestions'])  # Follow-up questions
#         """
#         if not self.connected:
#             self.connect()
        
#         try:
#             schema = self.db_manager.get_schema()
            
#             # Generate SQL
#             sql = self.query_generator.generate_sql(question, schema, self.db_manager)
            
#             # Execute query
#             result = self.executor.run_query(sql, limit_results=limit)
            
#             if result['success']:
#                 # Generate natural language explanation
#                 explanation = self.nlp_responder.generate_natural_response(
#                     original_question=question,
#                     sql_query=sql,
#                     results=result['data'],
#                     execution_time=result['execution_time']
#                 )
                
#                 # Generate follow-up suggestions
#                 suggestions = self.nlp_responder.generate_contextual_followup_suggestions(
#                     question, result['data']
#                 )
                
#                 return {
#                     'results': result['data'],
#                     'explanation': explanation,
#                     'sql_generated': sql,
#                     'suggestions': suggestions,
#                     'execution_time': result['execution_time'],
#                     'row_count': result['count']
#                 }
#             else:
#                 raise Exception(f"Query execution failed: {result['error']}")
                
#         except Exception as e:
#             raise Exception(f"Failed to process smart question: {str(e)}")
    
#     def show_tables(self):
#         """Show all tables in the database"""
#         if not self.connected:
#             self.connect()
        
#         schema = self.db_manager.get_schema()
#         return list(schema.keys())
    
#     def show_columns(self, table_name: str):
#         """Show columns for a specific table"""
#         if not self.connected:
#             self.connect()
        
#         schema = self.db_manager.get_schema()
#         return schema.get(table_name, [])
    
#     def get_database_info(self):
#         """Get information about the connected database"""
#         if not self.connected:
#             self.connect()
        
#         return self.db_manager.get_database_info()
    
#     def execute_sql(self, sql: str, limit: int = None):
#         """
#         Execute raw SQL query (for advanced users)
        
#         Args:
#             sql: Raw SQL query to execute
#             limit: Optional result limit
            
#         Returns:
#             Query results
#         """
#         if not self.connected:
#             self.connect()
        
#         try:
#             result = self.executor.run_query(sql, limit_results=limit)
            
#             if result['success']:
#                 return result['data']
#             else:
#                 raise Exception(f"SQL execution failed: {result['error']}")
                
#         except Exception as e:
#             raise Exception(f"Failed to execute SQL: {str(e)}")

# # Convenience functions for one-liners
# def quick_ask(connection_string: str, question: str):
#     """
#     One-liner to ask a database question
    
#     Args:
#         connection_string: Database connection
#         question: Natural language question
        
#     Returns:
#         Query results
        
#     Example:
#         results = quick_ask('sqlite:///data.db', 'How many users signed up today?')
#     """
#     client = AIQwal(connection_string)
#     return client.ask(question)

# def smart_ask(connection_string: str, question: str):
#     """
#     One-liner to ask with AI explanation
    
#     Args:
#         connection_string: Database connection
#         question: Natural language question
        
#     Returns:
#         Dictionary with results and AI explanation
        
#     Example:
#         response = smart_ask('postgresql://...', 'Show revenue trends')
#         print(response['explanation'])
#     """
#     client = AIQwal(connection_string)
#     return client.ask_smart(question)

# # Export public API
# __all__ = ['AIQwal', 'quick_ask', 'smart_ask']

# # Package metadata
# __version__ = '1.0.0'
# __title__ = 'AIQWAL Client'
# __description__ = 'AI-powered natural language database client'
# __author__ = 'AIQWAL Team'


# aiqwal/__init__.py - Simple one-line import setup

"""
AIQWAL - AI Query Writer for Any Language
Just one import: from aiqwal import AIQWAL
"""

# Import all your existing components
from .ultimate_database_manager import UltimateDatabaseManager
from .ultimate_query_generator import UltimateQueryGenerator  
from .ultimate_executor import UltimateExecutor
from .nlp_response_generator import NLPResponseGenerator
from .utils import log_info, log_error

class AIQwal:
    """
    Main AIQWAL class - One import to rule them all!
    
    Usage:
        from aiqwal import AIQWAL
        ai = AIQWAL('your-connection-string')                    # Silent mode
        ai = AIQWAL('your-connection-string', verbose=True)      # Show all logs
        results = ai.query('How many users do I have?')
    """
    
    def __init__(self, connection_string: str, verbose: bool = False, **kwargs):
        """Initialize AIQWAL with any database connection"""
        self.connection_string = connection_string
        self.verbose = verbose  # Control logging
        self.db_manager = None
        self.query_generator = None
        self.executor = None
        self.nlp_responder = None
        self.connected = False
        
        # Auto-connect by default
        if kwargs.get('auto_connect', True):
            self.connect()
    
    def _log(self, message: str, force: bool = False):
        """Internal logging method - only shows if verbose=True"""
        if self.verbose or force:
            print(message)
    
    def connect(self):
        """Connect and initialize all components"""
        try:
            self._log("🔗 Connecting to database...")
            
            # Initialize database manager
            self.db_manager = UltimateDatabaseManager(self.connection_string)
            connection_result = self.db_manager.connect()
            
            if not connection_result['success']:
                raise Exception(f"Connection failed: {connection_result.get('error')}")
            
            self._log(f"✅ Connected to {connection_result['database']}")
            
            # Initialize AI components
            self._log("🤖 Loading AI components...")
            self.query_generator = UltimateQueryGenerator()
            self.executor = UltimateExecutor(self.db_manager)
            self.nlp_responder = NLPResponseGenerator()
            
            self.connected = True
            self._log("✅ AIQWAL ready!")
            
            return connection_result
            
        except Exception as e:
            # Always show errors
            self._log(f"❌ Connection failed: {str(e)}", force=True)
            raise Exception(f"AIQWAL initialization failed: {str(e)}")
    
    def query(self, natural_language_query: str, limit: int = None):
        """
        Ask your database anything in natural language!
        
        Args:
            natural_language_query: Your question in plain English
            limit: Optional result limit
            
        Returns:
            Query results as list of dictionaries
        """
        if not self.connected:
            self.connect()
        
        try:
            # Get schema
            schema = self.db_manager.get_schema()
            
            # Generate SQL using AI (with verbose logging)
            self._log(f"🧠 Generating SQL for: '{natural_language_query}'")
            
            # Temporarily patch the query generator to respect verbose mode
            original_print = print
            if not self.verbose:
                # Silence the internal generator logs
                import builtins
                builtins.print = lambda *args, **kwargs: None
            
            sql = self.query_generator.generate_sql(
                natural_language_query, 
                schema, 
                self.db_manager
            )
            
            # Restore print
            if not self.verbose:
                builtins.print = original_print
            
            self._log(f"✅ Generated SQL: {sql}")
            
            # Execute SQL
            self._log("🚀 Executing query...")
            result = self.executor.run_query(sql, limit_results=limit)
            
            if result['success']:
                self._log(f"✅ Query successful! Found {result['count']} results")
                return result['data']
            else:
                self._log(f"❌ Query failed: {result['error']}", force=True)
                raise Exception(f"Query failed: {result['error']}")
                
        except Exception as e:
            self._log(f"❌ Query processing failed: {str(e)}", force=True)
            raise Exception(f"Query processing failed: {str(e)}")
    
    def query_with_explanation(self, natural_language_query: str, limit: int = None):
        """
        Ask question and get AI explanation of results
        
        Returns:
            dict with 'results', 'explanation', 'sql', 'suggestions'
        """
        if not self.connected:
            self.connect()
        
        try:
            # Get schema
            schema = self.db_manager.get_schema()
            
            # Generate SQL using AI
            self._log(f"🧠 Generating SQL for: '{natural_language_query}'")
            
            # Handle verbose logging for internal components
            original_print = print
            if not self.verbose:
                import builtins
                builtins.print = lambda *args, **kwargs: None
            
            sql = self.query_generator.generate_sql(
                natural_language_query, 
                schema, 
                self.db_manager
            )
            
            if not self.verbose:
                builtins.print = original_print
                
            self._log(f"✅ Generated SQL: {sql}")
            
            # Execute SQL
            self._log("🚀 Executing query...")
            result = self.executor.run_query(sql, limit_results=limit)
            
            if result['success']:
                self._log(f"✅ Query successful! Found {result['count']} results")
                
                # Generate natural language explanation
                self._log("🧠 Generating AI explanation...")
                explanation = self.nlp_responder.generate_natural_response(
                    original_question=natural_language_query,
                    sql_query=sql,
                    results=result['data'],
                    execution_time=result['execution_time']
                )
                
                # Generate follow-up suggestions
                suggestions = self.nlp_responder.generate_contextual_followup_suggestions(
                    natural_language_query, result['data']
                )
                
                self._log("✅ AI explanation generated!")
                
                return {
                    'results': result['data'],
                    'explanation': explanation,
                    'sql': sql,
                    'suggestions': suggestions,
                    'execution_time': result['execution_time'],
                    'count': result['count']
                }
            else:
                self._log(f"❌ Query failed: {result['error']}", force=True)
                raise Exception(f"Query failed: {result['error']}")
                
        except Exception as e:
            self._log(f"❌ Query processing failed: {str(e)}", force=True)
            raise Exception(f"Query processing failed: {str(e)}")
    
    def get_schema(self):
        """Get database schema"""
        if not self.connected:
            self.connect()
        
        self._log("📋 Retrieving database schema...")
        schema = self.db_manager.get_schema()
        self._log(f"✅ Schema retrieved: {len(schema)} tables found")
        return schema
    
    def get_info(self):
        """Get database information"""
        if not self.connected:
            self.connect()
        
        self._log("ℹ️ Retrieving database information...")
        info = self.db_manager.get_database_info()
        self._log("✅ Database information retrieved")
        return info

# Convenience functions for even simpler usage
def quick_query(connection_string: str, question: str):
    """One-liner for quick queries"""
    ai = AIQwal(connection_string)
    return ai.query(question)

def smart_query(connection_string: str, question: str):
    """One-liner with AI explanations"""
    ai = AIQwal(connection_string)
    return ai.query_with_explanation(question)

# Export the main class and convenience functions
__all__ = ['AIQwal', 'quick_query', 'smart_query']

# Version info
__version__ = '1.0.0'
__author__ = 'AIQWAL Team'