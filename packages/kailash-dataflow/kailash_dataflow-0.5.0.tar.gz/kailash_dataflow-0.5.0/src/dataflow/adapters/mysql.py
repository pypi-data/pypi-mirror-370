"""
MySQL Database Adapter

MySQL-specific database adapter implementation.
"""

import logging
from typing import Any, Dict, List, Tuple

from .base import DatabaseAdapter
from .exceptions import AdapterError, ConnectionError, QueryError, TransactionError

logger = logging.getLogger(__name__)


class MySQLAdapter(DatabaseAdapter):
    """MySQL database adapter."""

    @property
    def database_type(self) -> str:
        return "mysql"

    @property
    def default_port(self) -> int:
        return 3306

    def __init__(self, connection_string: str, **kwargs):
        super().__init__(connection_string, **kwargs)

        # MySQL-specific configuration
        self.charset = kwargs.get(
            "charset", self.query_params.get("charset", "utf8mb4")
        )
        self.collation = kwargs.get("collation", "utf8mb4_unicode_ci")

        # Use actual port or default
        if self.port is None:
            self.port = self.default_port

    async def connect(self) -> None:
        """Establish MySQL connection."""
        try:
            # Mock connection for now
            self._connection = f"mysql_connection_{id(self)}"
            self.is_connected = True
            logger.info(f"Connected to MySQL at {self.host}:{self.port}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MySQL: {e}")

    async def disconnect(self) -> None:
        """Close MySQL connection."""
        if self._connection:
            self._connection = None
            self.is_connected = False
            logger.info("Disconnected from MySQL")

    async def execute_query(self, query: str, params: List[Any] = None) -> List[Dict]:
        """Execute MySQL query."""
        if not self.is_connected:
            raise ConnectionError("Not connected to database")

        try:
            # Format query for MySQL parameter style
            mysql_query, mysql_params = self.format_query(query, params)

            # Mock execution for now
            logger.debug(f"Executing query: {mysql_query} with params: {mysql_params}")

            # Return mock results
            return [{"result": "success", "rows_affected": 1}]
        except Exception as e:
            raise QueryError(f"Query execution failed: {e}")

    async def execute_transaction(
        self, queries: List[Tuple[str, List[Any]]]
    ) -> List[Any]:
        """Execute multiple queries in MySQL transaction."""
        if not self.is_connected:
            raise ConnectionError("Not connected to database")

        try:
            results = []
            logger.debug(f"Starting transaction with {len(queries)} queries")

            for query, params in queries:
                result = await self.execute_query(query, params)
                results.append(result)

            logger.debug("Transaction completed successfully")
            return results
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            raise TransactionError(f"Transaction failed: {e}")

    async def get_table_schema(self, table_name: str) -> Dict[str, Dict]:
        """Get MySQL table schema."""
        if not self.is_connected:
            raise ConnectionError("Not connected to database")

        # Mock schema information
        return {
            "id": {
                "type": "integer",
                "nullable": False,
                "primary_key": True,
                "auto_increment": True,
            },
            "name": {"type": "varchar", "nullable": True, "max_length": 255},
            "created_at": {
                "type": "timestamp",
                "nullable": False,
                "default": "CURRENT_TIMESTAMP",
            },
        }

    async def create_table(self, table_name: str, schema: Dict[str, Dict]) -> None:
        """Create MySQL table."""
        if not self.is_connected:
            raise ConnectionError("Not connected to database")

        # Mock table creation
        logger.info(f"Creating table: {table_name}")

    async def drop_table(self, table_name: str) -> None:
        """Drop MySQL table."""
        if not self.is_connected:
            raise ConnectionError("Not connected to database")

        # Mock table drop
        logger.info(f"Dropping table: {table_name}")

    def get_dialect(self) -> str:
        """Get MySQL dialect."""
        return "mysql"

    def supports_feature(self, feature: str) -> bool:
        """Check MySQL feature support."""
        mysql_features = {
            "json": True,  # MySQL 5.7+
            "arrays": False,
            "regex": True,
            "window_functions": True,  # MySQL 8.0+
            "cte": True,  # MySQL 8.0+
            "upsert": True,  # INSERT ... ON DUPLICATE KEY UPDATE
            "fulltext_search": True,
            "spatial_indexes": True,
            "hstore": False,  # PostgreSQL-specific
            "mysql_specific": True,
            "sqlite_specific": False,
        }
        return mysql_features.get(feature, False)

    def format_query(
        self, query: str, params: List[Any] = None
    ) -> Tuple[str, List[Any]]:
        """Format query for MySQL parameter style (%s)."""
        if params is None:
            params = []

        # Convert ? placeholders to %s
        formatted_query = query.replace("?", "%s")

        return formatted_query, params

    def encode_string(self, text: str) -> str:
        """Encode string for MySQL charset."""
        # Map MySQL charset names to Python encoding names
        charset_mapping = {"utf8mb4": "utf-8", "utf8": "utf-8", "latin1": "latin-1"}
        python_charset = charset_mapping.get(self.charset, self.charset)
        return text.encode(python_charset).decode(python_charset)

    def decode_string(self, text: str) -> str:
        """Decode string from MySQL charset."""
        return text

    async def get_storage_engines(self) -> Dict[str, Dict]:
        """Get available MySQL storage engines."""
        # Mock storage engines
        return {
            "InnoDB": {
                "support": "DEFAULT",
                "comment": "Supports transactions, row-level locking, and foreign keys",
            },
            "MyISAM": {"support": "YES", "comment": "MyISAM storage engine"},
            "MEMORY": {
                "support": "YES",
                "comment": "Hash based, stored in memory, useful for temporary tables",
            },
        }

    @property
    def supports_savepoints(self) -> bool:
        """MySQL supports savepoints with InnoDB."""
        return True
