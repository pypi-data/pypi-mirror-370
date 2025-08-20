"""
MySQL Connection Utility Class
This utility provides a connection manager for MySQL databases with configurable parameters.
"""

import mysql.connector
from mysql.connector import Error
import logging
import time
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class MySQLConnectionUtil:
    """Utility class for managing MySQL database connections."""
    
    def __init__(self, config: Dict[str, Any], max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize the MySQL connection utility with configuration.
        
        Args:
            config (Dict[str, Any]): Database connection configuration
            max_retries (int): Maximum number of connection retries
            retry_delay (float): Delay between retries in seconds
        """
        self.config = config
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connection = None
    
    def connect(self) -> bool:
        """
        Establish a connection to the MySQL database with retry logic.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        for attempt in range(self.max_retries):
            try:
                self.connection = mysql.connector.connect(**self.config)
                logger.info("Successfully connected to MySQL database")
                return True
            except Error as e:
                logger.warning(f"Attempt {attempt + 1} failed to connect to MySQL: {e}")
                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Failed to connect to MySQL after {self.max_retries} attempts")
                    return False
    
    def disconnect(self):
        """Close the MySQL database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("MySQL connection closed")
    
    def get_connection(self):
        """
        Get the active database connection.
        
        Returns:
            connection: MySQL connection object or None if not connected
        """
        return self.connection
    
    def execute_query(self, query: str, params: Optional[tuple] = None):
        """
        Execute a SELECT query and return results.
        
        Args:
            query (str): SQL query to execute
            params (tuple, optional): Query parameters
            
        Returns:
            list: Query results
        """
        if not self.connection or not self.connection.is_connected():
            logger.error("No active database connection")
            return []
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            logger.error(f"Error executing query: {e}")
            return []
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> bool:
        """
        Execute an INSERT, UPDATE, or DELETE query.
        
        Args:
            query (str): SQL query to execute
            params (tuple, optional): Query parameters
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connection or not self.connection.is_connected():
            logger.error("No active database connection")
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            logger.error(f"Error executing update: {e}")
            self.connection.rollback()
            return False

# Example usage (for reference):
# config = {
#     'host': 'localhost',
#     'database': 'mydb',
#     'user': 'username',
#     'password': 'password',
#     'port': 3306
# }
# 
# db_util = MySQLConnectionUtil(config)
# if db_util.connect():
#     # Perform operations
#     results = db_util.execute_query("SELECT * FROM users WHERE id = %s", (1,))
#     db_util.disconnect()
