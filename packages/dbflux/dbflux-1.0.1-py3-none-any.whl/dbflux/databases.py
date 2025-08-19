from .base import BaseDB

class Sqlite(BaseDB):
    _dialect_driver = "sqlite"  
    _default_port = None
class PostgreSQL(BaseDB):
    _dialect_driver = "postgresql+psycopg"  
    _default_port = 5432

class MySQL(BaseDB):
    _dialect_driver = "mysql+mysqlclient"  
    _default_port = 3306

class MariaDB(BaseDB):
    _dialect_driver = "mariadb+mariadbconnector"  
    _default_port = 3306

class MSSQL(BaseDB):
    _dialect_driver = "mssql+pyodbc"  
    _default_port = 1433

class Oracle(BaseDB):
   
    _dialect_driver = "oracle+oracledb"  
    _default_port = 1521

class DB2(BaseDB):
    _dialect_driver = "ibm_db"  
    _default_port = 50000

class Firebird(BaseDB):
    _dialect_driver = "firebird+fdb"  
    _default_port = 3050
