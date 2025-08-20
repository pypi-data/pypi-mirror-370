# # aiqwal/ultimate_executor.py
# """
# Ultimate Executor - Enhanced version of YOUR executor.py
# Now works with ANY database in the world with optimizations!
# """

# from sqlalchemy import text
# from typing import Dict, List, Any, Optional
# import time

# class UltimateExecutor:
#     """
#     Ultimate SQL Executor - Works with ANY database in the world!
#     Enhanced version of your existing executor.py
#     """
    
#     def __init__(self, database_manager):
#         self.database_manager = database_manager
#         self.engine = database_manager.engine
#         self.db_info = database_manager.get_database_info()
    
#     def run_query(self, sql_query: str, limit_results: Optional[int] = None) -> Dict[str, Any]:
#         """
#         Execute SQL query on ANY database with comprehensive error handling
#         Enhanced version of your original run_query method
#         """
#         start_time = time.time()
        
#         try:
#             print(f"🚀 Executing on {self.db_info['name']}...")
#             print(f"📝 SQL: {sql_query}")
            
#             # Apply any final database-specific adaptations
#             final_sql = self.database_manager.adapt_sql_for_database(sql_query)
            
#             if final_sql != sql_query:
#                 print(f"🔧 Adapted SQL: {final_sql}")
            
#             with self.engine.connect() as conn:
#                 # Execute the query
#                 result = conn.execute(text(final_sql))
                
#                 # Get column names
#                 columns = list(result.keys()) if result.keys() else []
                
#                 # Fetch results
#                 rows = result.fetchall()
                
#                 # Convert to list of dicts (same as your original format!)
#                 data = [dict(zip(columns, row)) for row in rows]
                
#                 # Apply result limiting if requested
#                 if limit_results and len(data) > limit_results:
#                     data = data[:limit_results]
#                     limited = True
#                 else:
#                     limited = False
                
#                 execution_time = round(time.time() - start_time, 3)
                
#                 return {
#                     'success': True,
#                     'data': data,
#                     'count': len(data),
#                     'total_rows': len(rows),
#                     'limited': limited,
#                     'columns': columns,
#                     'execution_time': execution_time,
#                     'database': self.db_info['name'],
#                     'original_sql': sql_query,
#                     'executed_sql': final_sql
#                 }
                
#         except Exception as e:
#             execution_time = round(time.time() - start_time, 3)
            
#             return {
#                 'success': False,
#                 'error': str(e),
#                 'error_type': type(e).__name__,
#                 'execution_time': execution_time,
#                 'database': self.db_info['name'],
#                 'sql': sql_query,
#                 'suggestion': self._get_error_suggestion(str(e))
#             }
    
#     def run_query_simple(self, sql_query: str) -> List[Dict[str, Any]]:
#         """
#         Simple version that returns just the data (compatible with your original executor)
#         """
#         result = self.run_query(sql_query)
#         if result['success']:
#             return result['data']
#         else:
#             raise Exception(f"Query failed: {result['error']}")
    
#     def test_database_features(self) -> Dict[str, Any]:
#         """
#         Test what features the database supports
#         """
#         tests = {
#             'basic_select': "SELECT 1 as test",
#             'limit_support': "SELECT 1 as test LIMIT 1",
#             'offset_support': "SELECT 1 as test LIMIT 1 OFFSET 0",
#             'nulls_last_support': "SELECT 1 as test ORDER BY test DESC NULLS LAST",
#             'window_functions': "SELECT 1 as test, ROW_NUMBER() OVER (ORDER BY test) as rn",
#             'cte_support': "WITH test AS (SELECT 1 as n) SELECT * FROM test"
#         }
        
#         results = {}
        
#         for test_name, test_sql in tests.items():
#             try:
#                 with self.engine.connect() as conn:
#                     conn.execute(text(test_sql))
#                 results[test_name] = True
#             except:
#                 results[test_name] = False
        
#         return {
#             'database': self.db_info['name'],
#             'features': results,
#             'recommendations': self._get_feature_recommendations(results)
#         }
    
#     def get_table_stats(self, table_name: str) -> Dict[str, Any]:
#         """
#         Get statistics about a table (works on any database)
#         """
#         try:
#             stats_queries = {
#                 'row_count': f"SELECT COUNT(*) as count FROM {table_name}",
#                 'table_info': f"SELECT * FROM {table_name} LIMIT 1"
#             }
            
#             stats = {}
            
#             with self.engine.connect() as conn:
#                 # Get row count
#                 result = conn.execute(text(stats_queries['row_count']))
#                 stats['row_count'] = result.fetchone()[0]
                
#                 # Get column info
#                 result = conn.execute(text(stats_queries['table_info']))
#                 stats['columns'] = list(result.keys()) if result.keys() else []
                
#                 # Try to get column statistics
#                 if stats['columns']:
#                     numeric_columns = []
#                     for col in stats['columns']:
#                         try:
#                             # Test if column is numeric
#                             test_query = f"SELECT AVG({col}) FROM {table_name} LIMIT 1"
#                             conn.execute(text(test_query))
#                             numeric_columns.append(col)
#                         except:
#                             pass
                    
#                     stats['numeric_columns'] = numeric_columns
                
#                 return {
#                     'success': True,
#                     'table': table_name,
#                     'database': self.db_info['name'],
#                     'stats': stats
#                 }
                
#         except Exception as e:
#             return {
#                 'success': False,
#                 'table': table_name,
#                 'error': str(e)
#             }
    
#     def _get_error_suggestion(self, error_message: str) -> str:
#         """
#         Provide helpful suggestions based on error message
#         """
#         error_lower = error_message.lower()
        
#         if 'syntax error' in error_lower:
#             return f"SQL syntax may not be compatible with {self.db_info['name']}. Try simpler SQL syntax."
        
#         elif 'table' in error_lower and 'exist' in error_lower:
#             return "Table does not exist. Check table name and schema."
        
#         elif 'column' in error_lower:
#             return "Column does not exist or is misspelled. Check column names."
        
#         elif 'limit' in error_lower:
#             return f"{self.db_info['name']} may not support LIMIT syntax. Using database-specific pagination."
        
#         elif 'connection' in error_lower:
#             return "Database connection issue. Check network and credentials."
        
#         else:
#             return "Try simplifying the query or check database-specific syntax requirements."
    
#     def _get_feature_recommendations(self, features: Dict[str, bool]) -> List[str]:
#         """
#         Get recommendations based on supported features
#         """
#         recommendations = []
        
#         if not features.get('limit_support', True):
#             recommendations.append(f"Use {self.db_info['name']}-specific pagination instead of LIMIT")
        
#         if not features.get('nulls_last_support', True):
#             recommendations.append("Avoid NULLS LAST syntax - not supported")
        
#         if features.get('window_functions', False):
#             recommendations.append("Window functions are available - use for advanced analytics")
        
#         if features.get('cte_support', False):
#             recommendations.append("Common Table Expressions (CTEs) are supported")
        
#         if not recommendations:
#             recommendations.append(f"All basic SQL features work well with {self.db_info['name']}")
        
#         return recommendations



# aiqwal/ultimate_executor.py
"""
Ultimate Executor - Enhanced version of YOUR executor.py
Now works with ANY database in the world with optimizations!
"""

from sqlalchemy import text
from typing import Dict, List, Any, Optional
import time

class UltimateExecutor:
    """
    Ultimate SQL Executor - Works with ANY database in the world!
    Enhanced version of your existing executor.py
    """
    
    def __init__(self, database_manager):
        self.database_manager = database_manager
        self.engine = database_manager.engine
        self.db_info = database_manager.get_database_info()
    
    def run_query(self, sql_query: str, limit_results: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute SQL query on ANY database with comprehensive error handling
        Enhanced version of your original run_query method
        """
        start_time = time.time()
        
        try:
            print(f"🚀 Executing on {self.db_info['name']}...")
            print(f"📝 SQL: {sql_query}")
            
            # Apply any final database-specific adaptations
            final_sql = self.database_manager.adapt_sql_for_database(sql_query)
            
            if final_sql != sql_query:
                print(f"🔧 Adapted SQL: {final_sql}")
            
            with self.engine.connect() as conn:
                # Execute the query
                result = conn.execute(text(final_sql))
                
                # Get column names
                columns = list(result.keys()) if result.keys() else []
                
                # Fetch results
                rows = result.fetchall()
                
                # Convert to list of dicts (same as your original format!)
                data = [dict(zip(columns, row)) for row in rows]
                
                # Apply result limiting if requested
                if limit_results and len(data) > limit_results:
                    data = data[:limit_results]
                    limited = True
                else:
                    limited = False
                
                execution_time = round(time.time() - start_time, 3)
                
                return {
                    'success': True,
                    'data': data,
                    'count': len(data),
                    'total_rows': len(rows),
                    'limited': limited,
                    'columns': columns,
                    'execution_time': execution_time,
                    'database': self.db_info['name'],
                    'original_sql': sql_query,
                    'executed_sql': final_sql
                }
                
        except Exception as e:
            execution_time = round(time.time() - start_time, 3)
            
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__,
                'execution_time': execution_time,
                'database': self.db_info['name'],
                'sql': sql_query,
                'suggestion': self._get_error_suggestion(str(e))
            }
    
    def run_query_simple(self, sql_query: str) -> List[Dict[str, Any]]:
        """
        Simple version that returns just the data (compatible with your original executor)
        """
        result = self.run_query(sql_query)
        if result['success']:
            return result['data']
        else:
            raise Exception(f"Query failed: {result['error']}")
    
    def test_database_features(self) -> Dict[str, Any]:
        """
        Test what features the database supports
        """
        tests = {
            'basic_select': "SELECT 1 as test",
            'limit_support': "SELECT 1 as test LIMIT 1",
            'offset_support': "SELECT 1 as test LIMIT 1 OFFSET 0",
            'nulls_last_support': "SELECT 1 as test ORDER BY test DESC NULLS LAST",
            'window_functions': "SELECT 1 as test, ROW_NUMBER() OVER (ORDER BY test) as rn",
            'cte_support': "WITH test AS (SELECT 1 as n) SELECT * FROM test"
        }
        
        results = {}
        
        for test_name, test_sql in tests.items():
            try:
                with self.engine.connect() as conn:
                    conn.execute(text(test_sql))
                results[test_name] = True
            except:
                results[test_name] = False
        
        return {
            'database': self.db_info['name'],
            'features': results,
            'recommendations': self._get_feature_recommendations(results)
        }
    
    def get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """
        Get statistics about a table (works on any database)
        """
        try:
            stats_queries = {
                'row_count': f"SELECT COUNT(*) as count FROM {table_name}",
                'table_info': f"SELECT * FROM {table_name} LIMIT 1"
            }
            
            stats = {}
            
            with self.engine.connect() as conn:
                # Get row count
                result = conn.execute(text(stats_queries['row_count']))
                stats['row_count'] = result.fetchone()[0]
                
                # Get column info
                result = conn.execute(text(stats_queries['table_info']))
                stats['columns'] = list(result.keys()) if result.keys() else []
                
                # Try to get column statistics
                if stats['columns']:
                    numeric_columns = []
                    for col in stats['columns']:
                        try:
                            # Test if column is numeric
                            test_query = f"SELECT AVG({col}) FROM {table_name} LIMIT 1"
                            conn.execute(text(test_query))
                            numeric_columns.append(col)
                        except:
                            pass
                    
                    stats['numeric_columns'] = numeric_columns
                
                return {
                    'success': True,
                    'table': table_name,
                    'database': self.db_info['name'],
                    'stats': stats
                }
                
        except Exception as e:
            return {
                'success': False,
                'table': table_name,
                'error': str(e)
            }
    
    def _get_error_suggestion(self, error_message: str) -> str:
        """
        Provide helpful suggestions based on error message
        """
        error_lower = error_message.lower()
        
        if 'syntax error' in error_lower:
            return f"SQL syntax may not be compatible with {self.db_info['name']}. Try simpler SQL syntax."
        
        elif 'table' in error_lower and 'exist' in error_lower:
            return "Table does not exist. Check table name and schema."
        
        elif 'column' in error_lower:
            return "Column does not exist or is misspelled. Check column names."
        
        elif 'limit' in error_lower:
            return f"{self.db_info['name']} may not support LIMIT syntax. Using database-specific pagination."
        
        elif 'connection' in error_lower:
            return "Database connection issue. Check network and credentials."
        
        else:
            return "Try simplifying the query or check database-specific syntax requirements."
    
    def _get_feature_recommendations(self, features: Dict[str, bool]) -> List[str]:
        """
        Get recommendations based on supported features
        """
        recommendations = []
        
        if not features.get('limit_support', True):
            recommendations.append(f"Use {self.db_info['name']}-specific pagination instead of LIMIT")
        
        if not features.get('nulls_last_support', True):
            recommendations.append("Avoid NULLS LAST syntax - not supported")
        
        if features.get('window_functions', False):
            recommendations.append("Window functions are available - use for advanced analytics")
        
        if features.get('cte_support', False):
            recommendations.append("Common Table Expressions (CTEs) are supported")
        
        if not recommendations:
            recommendations.append(f"All basic SQL features work well with {self.db_info['name']}")
        
        return recommendations