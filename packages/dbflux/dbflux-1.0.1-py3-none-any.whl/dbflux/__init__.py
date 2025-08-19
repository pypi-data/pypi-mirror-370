# __init__.py

from .databases import Sqlite, MySQL, PostgreSQL, MariaDB, Oracle, DB2, Firebird, MSSQL
from .model import DBModel
import difflib,sys
from .base import BaseDB 

class DBFactory:
    """
    🔹 Dynamic Database Factory for DBFlux

    Usage:
        factory = DBFactory(username="user", password="pass", db_name="testdb")

        # Create a database instance easily
        sqlite_db   = factory.create("sqlite")
        mysql_db    = factory.create("mysql")
        postgres_db = factory.create("postgresql")

    Supported databases (case-insensitive):
        - sqlite, mysql, postgres/postgresql, mariadb, oracle, db2/ibmdb2, firebird, mssql/sqlserver
    """
    
    def __init__(self, db_name=None, username=None, password=None, host='localhost', port=None,
                 echo=False, pool_size=10, max_overflow=20):
        self._kwargs = {
            'db_name': db_name,
            'username': username,
            'password': password,
            'host': host,
            'port': port,
            'echo': echo,
            'pool_size': pool_size,
            'max_overflow': max_overflow
        }

        self._mapping = {
            "sqlite": Sqlite,
            "mysql": MySQL,
            "postgres": PostgreSQL,
            "postgresql": PostgreSQL,
            "mariadb": MariaDB,
            "oracle": Oracle,
            "db2": DB2,
            "ibmdb2": DB2,
            "firebird": Firebird,
            "mssql": MSSQL,
            "sqlserver": MSSQL
        }

    def create(self, db_type: str)->BaseDB:
        """
        Create and return a database instance based on the given type.

        Args:
            db_type (str): Name of the database type (e.g., "sqlite", "mysql", "postgresql").

        Returns:
            BaseDB: Instance of the corresponding database class.

        Raises:
            ValueError: If the provided database type is unsupported. Suggests the closest valid option.

        Examples:
            >>> factory.create("sqlite")
            <SQLiteDB object>

            >>> factory.create("mysq")
            # Raises ValueError: Unsupported database type: 'mysq'. Did you mean 'mysql'?
        """
        db_type_lower = db_type.lower()
        if db_type_lower not in self._mapping:
            closest = difflib.get_close_matches(db_type_lower, self._mapping.keys(), n=1, cutoff=0.6)
            if closest:
                print(f"❌ Unsupported database type: '{db_type}'. Did you mean '{closest[0]}'?")
            else:
                print(f"❌ Unsupported database type: '{db_type}'")
            sys.exit(1)  

        db_class = self._mapping[db_type_lower]
        return db_class(**self._kwargs)
