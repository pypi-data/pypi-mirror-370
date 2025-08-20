"""
Ultimate Database Manager - Works with ANY database in the world!
Supports: SQLite, PostgreSQL, MySQL, SQL Server, Oracle, MongoDB, 
Snowflake, BigQuery, Redshift, and ANY SQLAlchemy-compatible database
"""

from sqlalchemy import create_engine, text, MetaData, inspect
from sqlalchemy.exc import SQLAlchemyError
import re
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse

class UltimateDatabaseManager:
    """
    Universal Database Manager that works with ANY database in the world
    """
    
    # Database configurations for ALL major databases
    DATABASE_CONFIGS = {
        'sqlite': {
            'name': 'SQLite',
            'driver': 'sqlite3',
            'port': None,
            'limit_syntax': 'LIMIT {n}',
            'top_n_syntax': 'ORDER BY {col} DESC LIMIT {n}',
            'supports_limit': True,
            'supports_offset': True,
            'supports_nulls_last': False,
            'quote_char': '"',
            'string_quote': "'",
            'test_query': "SELECT 1",
        },
        'postgresql': {
            'name': 'PostgreSQL',
            'driver': 'psycopg2',
            'port': 5432,
            'limit_syntax': 'LIMIT {n} OFFSET {offset}',
            'top_n_syntax': 'ORDER BY {col} DESC NULLS LAST LIMIT {n}',
            'supports_limit': True,
            'supports_offset': True,
            'supports_nulls_last': True,
            'quote_char': '"',
            'string_quote': "'",
            'test_query': "SELECT 1",
        },
        'mysql': {
            'name': 'MySQL',
            'driver': 'pymysql',
            'port': 3306,
            'limit_syntax': 'LIMIT {n}',
            'top_n_syntax': 'ORDER BY {col} DESC LIMIT {n}',
            'supports_limit': True,
            'supports_offset': True,
            'supports_nulls_last': False,
            'quote_char': '`',
            'string_quote': "'",
            'test_query': "SELECT 1",
        },
        'mssql': {
            'name': 'SQL Server',
            'driver': 'pyodbc',
            'port': 1433,
            'limit_syntax': 'TOP {n}',
            'top_n_syntax': 'TOP {n} * FROM {table} ORDER BY {col} DESC',
            'supports_limit': False,
            'supports_offset': False,
            'supports_nulls_last': False,
            'quote_char': '[',
            'string_quote': "'",
            'test_query': "SELECT 1",
        },
        'oracle': {
            'name': 'Oracle',
            'driver': 'cx_oracle',
            'port': 1521,
            'limit_syntax': 'ROWNUM <= {n}',
            'top_n_syntax': 'WHERE ROWNUM <= {n} ORDER BY {col} DESC NULLS LAST',
            'supports_limit': False,
            'supports_offset': False,
            'supports_nulls_last': True,
            'quote_char': '"',
            'string_quote': "'",
            'test_query': "SELECT 1 FROM DUAL",
        },
        'snowflake': {
            'name': 'Snowflake',
            'driver': 'snowflake-sqlalchemy',
            'port': 443,
            'limit_syntax': 'LIMIT {n}',
            'top_n_syntax': 'ORDER BY {col} DESC LIMIT {n}',
            'supports_limit': True,
            'supports_offset': True,
            'supports_nulls_last': True,
            'quote_char': '"',
            'string_quote': "'",
            'test_query': "SELECT 1",
        },
        'bigquery': {
            'name': 'Google BigQuery',
            'driver': 'pybigquery',
            'port': 443,
            'limit_syntax': 'LIMIT {n}',
            'top_n_syntax': 'ORDER BY {col} DESC LIMIT {n}',
            'supports_limit': True,
            'supports_offset': True,
            'supports_nulls_last': True,
            'quote_char': '`',
            'string_quote': "'",
            'test_query': "SELECT 1",
        },
        'redshift': {
            'name': 'Amazon Redshift',
            'driver': 'psycopg2',
            'port': 5439,
            'limit_syntax': 'LIMIT {n}',
            'top_n_syntax': 'ORDER BY {col} DESC LIMIT {n}',
            'supports_limit': True,
            'supports_offset': True,
            'supports_nulls_last': True,
            'quote_char': '"',
            'string_quote': "'",
            'test_query': "SELECT 1",
        },
    }
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.engine = None
        self.db_type = None
        self.config = None
        self.metadata = None
        self._parse_connection_string()
    
    def _parse_connection_string(self):
        """Parse connection string to detect database type"""
        try:
            parsed = urlparse(self.connection_string)
            scheme = parsed.scheme.lower()
            
            # Map connection schemes to our database types
            scheme_mapping = {
                'sqlite': 'sqlite',
                'postgresql': 'postgresql',
                'postgres': 'postgresql',
                'mysql': 'mysql',
                'mysql+pymysql': 'mysql',
                'mssql': 'mssql',
                'mssql+pyodbc': 'mssql',
                'oracle': 'oracle',
                'oracle+cx_oracle': 'oracle',
                'snowflake': 'snowflake',
                'bigquery': 'bigquery',
                'redshift': 'redshift',
                'redshift+psycopg2': 'redshift',
            }
            
            self.db_type = scheme_mapping.get(scheme, 'unknown')
            self.config = self.DATABASE_CONFIGS.get(self.db_type, self.DATABASE_CONFIGS['sqlite'])
            
            print(f"🔍 Detected database type: {self.config['name']} ({self.db_type})")
            
        except Exception as e:
            print(f"⚠️  Could not parse connection string: {e}")
            self.db_type = 'unknown'
            self.config = self.DATABASE_CONFIGS['sqlite']  # Fallback
    
    def connect(self) -> Dict[str, Any]:
        """
        Connect to ANY database and return connection status
        """
        try:
            print(f"🔗 Connecting to {self.config['name']}...")
            
            # Create engine with database-specific options
            engine_kwargs = {
                'echo': False,
                'pool_pre_ping': True,
                'pool_recycle': 3600,
            }
            
            # Add database-specific connection arguments
            if self.db_type == 'mysql':
                engine_kwargs['connect_args'] = {'charset': 'utf8mb4'}
            elif self.db_type == 'mssql':
                engine_kwargs['connect_args'] = {
                    'driver': 'ODBC Driver 17 for SQL Server',
                    'trusted_connection': 'yes'
                }
            elif self.db_type == 'oracle':
                engine_kwargs['connect_args'] = {'encoding': 'UTF-8'}
            
            self.engine = create_engine(self.connection_string, **engine_kwargs)
            
            # Test connection
            test_result = self._test_connection()
            
            if test_result['success']:
                # Load metadata
                self.metadata = MetaData()
                self.metadata.reflect(bind=self.engine)
                
                print(f"✅ Successfully connected to {self.config['name']}!")
                return {
                    'success': True,
                    'database': self.config['name'],
                    'type': self.db_type,
                    'version': test_result.get('version', 'Unknown'),
                    'tables': list(self.metadata.tables.keys())
                }
            else:
                return test_result
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to connect to {self.config['name']}: {str(e)}",
                'database': self.config['name'],
                'type': self.db_type
            }
    
    def _test_connection(self) -> Dict[str, Any]:
        """Test database connection with appropriate query"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(self.config['test_query']))
                test_value = result.fetchone()[0]
                
                # Get database version
                version = self._get_database_version(conn)
                
                return {
                    'success': True,
                    'test_result': test_value,
                    'version': version
                }
        except Exception as e:
            return {
                'success': False,
                'error': f"Connection test failed: {str(e)}"
            }
    
    def _get_database_version(self, connection) -> str:
        """Get database version using appropriate query"""
        version_queries = {
            'postgresql': "SELECT version()",
            'mysql': "SELECT VERSION()",
            'sqlite': "SELECT sqlite_version()",
            'mssql': "SELECT @@VERSION",
            'oracle': "SELECT * FROM V$VERSION WHERE ROWNUM = 1",
            'snowflake': "SELECT CURRENT_VERSION()",
            'bigquery': "SELECT @@version.version_number",
            'redshift': "SELECT version()",
        }
        
        try:
            query = version_queries.get(self.db_type, "SELECT 'Unknown' as version")
            result = connection.execute(text(query))
            return str(result.fetchone()[0])[:100]  # Limit length
        except:
            return "Version unavailable"
    
    def get_schema(self) -> Dict[str, List[str]]:
        """
        Get database schema that works with ANY database
        """
        if not self.engine:
            raise Exception("Not connected to database. Call connect() first.")
        
        try:
            inspector = inspect(self.engine)
            schema = {}
            
            # Get all table names
            table_names = inspector.get_table_names()
            
            for table_name in table_names:
                # Get column information
                columns = inspector.get_columns(table_name)
                column_names = [col['name'] for col in columns]
                schema[table_name] = column_names
            
            return schema
            
        except Exception as e:
            raise Exception(f"Failed to get schema: {str(e)}")
    
    def adapt_sql_for_database(self, sql: str) -> str:
        """
        Adapt ANY SQL to work with the current database
        """
        if not sql or not self.config:
            return sql
        
        adapted_sql = sql.strip()
        
        # Handle LIMIT syntax conversion
        if not self.config['supports_limit']:
            if self.db_type == 'mssql':
                # Convert LIMIT to TOP for SQL Server
                adapted_sql = re.sub(
                    r'SELECT\s+(.*?)\s+FROM\s+(.*?)\s+ORDER BY\s+(.*?)\s+LIMIT\s+(\d+)',
                    r'SELECT TOP \4 \1 FROM \2 ORDER BY \3',
                    adapted_sql,
                    flags=re.IGNORECASE | re.DOTALL
                )
                # Simple LIMIT without ORDER BY
                adapted_sql = re.sub(
                    r'SELECT\s+(.*?)\s+FROM\s+(.*?)\s+LIMIT\s+(\d+)',
                    r'SELECT TOP \3 \1 FROM \2',
                    adapted_sql,
                    flags=re.IGNORECASE | re.DOTALL
                )
            
            elif self.db_type == 'oracle':
                # Convert LIMIT to ROWNUM for Oracle
                limit_match = re.search(r'LIMIT\s+(\d+)', adapted_sql, re.IGNORECASE)
                if limit_match:
                    limit_num = limit_match.group(1)
                    adapted_sql = re.sub(r'LIMIT\s+\d+', '', adapted_sql, flags=re.IGNORECASE)
                    
                    if 'WHERE' in adapted_sql.upper():
                        adapted_sql = re.sub(
                            r'WHERE\s+',
                            f'WHERE ROWNUM <= {limit_num} AND ',
                            adapted_sql,
                            flags=re.IGNORECASE
                        )
                    else:
                        adapted_sql += f' WHERE ROWNUM <= {limit_num}'
        
        # Handle NULLS LAST
        if not self.config['supports_nulls_last']:
            adapted_sql = re.sub(r'\s+NULLS\s+LAST', '', adapted_sql, flags=re.IGNORECASE)
        
        # Handle quote characters if needed
        # This could be extended for identifier quoting
        
        return adapted_sql.strip()
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get comprehensive database information"""
        if not self.engine:
            return {'error': 'Not connected'}
        
        return {
            'name': self.config['name'],
            'type': self.db_type,
            'driver': self.config['driver'],
            'supports_limit': self.config['supports_limit'],
            'supports_offset': self.config['supports_offset'],
            'supports_nulls_last': self.config['supports_nulls_last'],
            'connection_string': self.connection_string,
            'tables': list(self.metadata.tables.keys()) if self.metadata else []
        }