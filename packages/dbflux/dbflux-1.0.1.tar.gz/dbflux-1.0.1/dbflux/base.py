from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict,Any,Union,Optional,Type
from sqlalchemy import  or_, and_,insert,func
from sqlalchemy import update
import importlib
from .utils import Data
import logging,sys

logging.basicConfig(level=logging.ERROR,  format="%(asctime)s - %(levelname)s - %(message)s")

class BaseDB:
    _dialect_driver = None
    _default_port = None
    
    def __init__(self,db_name=None, username=None, password=None, host='localhost', port=None,  echo=False, pool_size=10, max_overflow=20):
        self._check_driver_installed(self._dialect_driver)
        self._username = username or ""
        self._password = password or ""
        self._host = host
        self._port = port or self._default_port
        self._db_name = db_name
        self._echo = echo
        self._pool_size = pool_size
        self._max_overflow = max_overflow
        self._logger = logging.getLogger(__name__)

    @property
    def engine(self):
        if hasattr(self, "_engine"):
            return self._engine
        
        if self._dialect_driver == "sqlite":
                url = "sqlite:///:memory:" if not self._db_name else f"sqlite:///{self._db_name}"
                self._engine = create_engine(url, echo=self._echo)
        else:
                port = self._port or self._default_port
                auth_part = f"{self._username}:{self._password}@" if self._username else ""
                url = f"{self._dialect_driver}://{auth_part}{self._host}:{port}/{self._db_name}"
                self._engine = create_engine(
                    url,
                    echo=self._echo,
                    pool_size=self._pool_size,
                    max_overflow=self._max_overflow
                )
        return self._engine
        
           
    @property
    def _session_maker(self):
        if not hasattr(self, "_session"):
            self._session = sessionmaker(bind=self.engine, expire_on_commit=False)
        return self._session
    @staticmethod
    def _check_driver_installed(dialect_driver: str):
        if dialect_driver.startswith("sqlite"):
          
            return

        module_name = dialect_driver.split('+', 1)[1] if '+' in dialect_driver else dialect_driver
        try:
            importlib.import_module(module_name)
        except ImportError:
            print(f"❌ Driver '{dialect_driver}' is not installed.\n"
                  f"📦 Please install it using:\n"
                  f"    pip install {module_name}")
            sys.exit(1)

   
    
    

    def execute_transaction(self, operation, *args, **kwargs):
        """Automatically manages database transactions.
        
        ## Usage:
        ```
            def operation(session):
                session.add(model_instance)
                return True

            result= execute_transaction(operation)
        ```
        
        """
        
        with self._session_maker() as session:
            try:
                result = operation(session, *args, **kwargs)
                session.commit()
                return result
            except SQLAlchemyError as e:
                session.rollback()
                self._logger.error(str(e))
               
                return None
    
    def create_tables(self, Base)-> bool:
        
        """Create tables if they don't exist"""
        try:
            Base.metadata.create_all(self.engine)
            return True
        except SQLAlchemyError as e:
            self._logger.error(str(e))
            return False
    
    def insert(self, model_class, data: Union[Dict[str, Any], object, List[Dict[str, Any]], List[object]]):
        """
            Insert one or multiple records into the database table associated with the specified SQLAlchemy model class.

            Parameters
            ----------
            model_class : SQLAlchemy model class
                The ORM model class representing the target database table into which data will be inserted.

            data : dict, object, list of dict, or list of objects
                The data to insert. It can be:
                - A single dictionary representing a record
                - A single model instance
                - A list of dictionaries
                - A list of model instances

            Returns
            -------
            int
                The number of rows successfully inserted into the database.
                Returns 0 if no valid data is provided.

            Notes
            -----
            - Converts model instances to dictionaries before insertion.
            - Uses engine-specific insert conflict handling:
                - SQLite: adds "OR IGNORE" prefix to skip duplicate entries
                - MySQL/MariaDB: adds "IGNORE" prefix to skip duplicate entries
                - PostgreSQL: uses "ON CONFLICT DO NOTHING" based on the primary key to ignore duplicates
                - Other engines: performs standard insert without conflict resolution

            - Uses a transaction context to execute the operation safely, ensuring commit or rollback as required.

            Examples
            --------
            >>> db.insert(User, {"id": 1, "name": "Alice"})
            1

            >>> db.insert(User, [User(id=2, name="Bob"), User(id=3, name="Carol")])
            2

            >>> db.insert(User, [])
            0

            """
        def to_dict(_data):
            if isinstance(_data, dict):
                return _data
            if isinstance(_data, model_class):
                _dict = _data.__dict__.copy()
                _dict.pop('_sa_instance_state', None)
                return _dict
            return None

        
        
        data_list=[]
        if isinstance(data,list):
            for d in data:
                _d=to_dict(d)
                if _d:
                    data_list.append(_d)
        else:
            _d=to_dict(data)
            if _d:
                data_list.append(_d)
            


        if not data_list:
            return 0
        
        
        def operation(session:Session):
            stmt = insert(model_class).values(data_list)
            if self.engine.name =='sqlite':
                stmt = stmt.prefix_with("OR IGNORE")
            elif self.engine.name in ['mysql', 'mariadb']:
                stmt = stmt.prefix_with("IGNORE")
            elif self.engine.name == 'postgresql':

                primary_keys_list = list(model_class.__table__.primary_key.columns)
                if primary_keys_list:
                    primary_key = primary_keys_list[0].name
                    stmt =stmt.on_conflict_do_nothing(index_elements=[primary_key]) 
            
            elif self.engine.name in ['mssql', 'oracle', 'ibm_db', 'firebird']:
                pass
            
            result = session.execute(stmt)
            return result.rowcount

        return self.execute_transaction(operation)

    def update(self, model_class, conditions: List | None, update_fields: Dict) -> int:
        """
        Bulk update existing records in a table using SQLAlchemy ORM.

        Args:
            model_class: SQLAlchemy ORM model class representing the table.
            update_fields: Dictionary of column names and their new values.
            conditions: Optional list of SQLAlchemy filter conditions (e.g., [User.active == True]).
                        If None, all rows will be updated.

        Returns:
            int: Number of records updated.

        Notes:
            - Works across all major databases supported by SQLAlchemy (SQLite, MySQL, PostgreSQL, MSSQL, Oracle, etc.).
            - Only updates existing rows; no new rows are inserted.

        Example:
            # Update only active users
            updated_count = db.update(
                User,
                conditions=[User.active == True],
                update_fields={'status': 'inactive'}
                
            )

            # Update all users
            updated_count = db.update(
                User,
                conditions=None,
                update_fields={'status': 'inactive'}
                
            )
        """
        def operation(session: Session):
            stmt = update(model_class).values(**update_fields)

            # Apply conditions if provided
            if conditions:
                stmt = stmt.where(and_(*conditions))

            result = session.execute(stmt)
            return result.rowcount or 0

        return self.execute_transaction(operation)


    def get(self, model_class,limit=None,conditions:list=None, order_by=None,descending=False )-> Data:
        

        """
        Retrieve data based on SQLAlchemy filter conditions.

        Args:
            model_class (type): The SQLAlchemy model class to retrieve from.
            conditions (List, optional): A list of SQLAlchemy filter conditions. Defaults to None.
            limit (int, optional): The number of records per page. Defaults to None.
            order_by (str, optional): The column name for ordering results. Defaults to None.
            descending (bool, optional): If True, sorts in descending order. Defaults to False.

        Returns:
            List: A list of records retrieved from the database.

        ### Example usage of different conditions:

            conditions=[]
            conditions.append(model_class.column_name == 'value')
            conditions.append(model_class.column_name != 'value')
            conditions.append(model_class.column_name.in_(['value', 'value2']))
            conditions.append(model_class.column_name.like('%value%'))
            conditions.append(model_class.column_name.ilike('%value%'))
            conditions.append(model_class.column_name.is_(None))
            conditions.append(model_class.column_name.isnot(None))
            conditions.append(model_class.column_name.between(1, 10))
            conditions.append(model_class.column_name.notbetween(1, 10))
        """
        
        def operation(session:Session):
            query = session.query(model_class)
            
            # Apply filters
            if conditions :
                query = query.filter(and_(*conditions))

            
            
            # Apply ordering
            if order_by:
                order_column = getattr(model_class, order_by)
                query = query.order_by(order_column.desc() if descending else order_column)
            
            # Apply limit
            if limit:
                query = query.limit(limit)

            return query.all()

        result = self.execute_transaction(operation)
        return Data(result) # type: ignore
    
   
        
        
    
    
    def bulk_update(self, model_class, updates: list[dict]) -> int:
        """
        Perform a bulk update on multiple rows of a table efficiently.

        This method uses SQLAlchemy's `bulk_update_mappings` to update multiple
        records in a single operation without loading them into memory as full objects.

        Args:
            model_class: The SQLAlchemy model class representing the table.
            updates (list[dict]): A list of dictionaries, each containing:
                - The primary key of the record to update.
                - The columns and their new values to update.
                Example:
                    updates = [
                        {'id': 1, 'status': 'inactive'},
                        {'id': 2, 'status': 'inactive'}
                    ]

        Returns:
            int: The number of records intended for update (length of `updates`).

        Raises:
            SQLAlchemyError: Any database error occurring during the transaction.
        
        Example:
            updates = [
                {'id': 1, 'status': 'inactive'},
                {'id': 2, 'status': 'inactive'}
            ]
            updated_count = db.update_bulk(UserModel, updates)
            print(f"{updated_count} records updated.")
        """
        def operation(session:'Session'):
            session.bulk_update_mappings(model_class, updates)
            return len(updates)

        return self.execute_transaction(operation)


    def paginate(self, model_class, conditions: List=None, page: int = 1, per_page: int = 10,order_by=None,descending=False)-> Data:
       
        """Retrieve paginated records from the database.
        Args:
            model_class (type): The SQLAlchemy model class to retrieve from.
            conditions (List, optional): A list of SQLAlchemy filter conditions. Defaults to None.
            page (int, optional): The page number to retrieve. Defaults to 1.
            per_page (int, optional): The number of records per page. Defaults to 10.

        Returns:
            List: A list of records retrieved from the database.
        
        ### Example usage of different conditions:
            conditions=[]
            conditions.append(model_class.column_name == 'value')
            conditions.append(model_class.column_name != 'value')
            conditions.append(model_class.column_name.in_(['value', 'value2']))
            conditions.append(model_class.column_name.like('%value%'))
            conditions.append(model_class.column_name.ilike('%value%'))
            conditions.append(model_class.column_name.is_(None))
            conditions.append(model_class.column_name.isnot(None))
            conditions.append(model_class.column_name.between(1, 10))
            conditions.append(model_class.column_name.notbetween(1, 10))
        """
        def operation(session:Session):
            query = session.query(model_class)
            if conditions:
                query = query.filter(and_(*conditions))
            # Apply ordering
            if order_by:
                order_column = getattr(model_class, order_by)
                query = query.order_by(order_column.desc() if descending else order_column)
                
            offset = (page - 1) * per_page
            records = query.offset(offset).limit(per_page).all()
            
            return records

        result= self.execute_transaction(operation)
        return Data(result)
    
    def delete(self, model_class, conditions: List|str=None,primary_keys:List[Any]=[]) -> int:
        """Delete records from the database based on the given conditions.

        Args:
            model_class (type): The SQLAlchemy model class to delete from.
            conditions (List|str): A list of SQLAlchemy filter conditions or a string 'ALL' to delete all records of the model_class.
            primary_keys (List[Any]): A list of primary key values to delete. If not provided, the primary key of the model_class is determined automatically.

        Returns:
            int: Number of rows deleted.

        ### Example usage of different conditions:
            conditions=[]
            conditions.append(model_class.column_name == 'value')
            conditions.append(model_class.column_name != 'value')
            conditions.append(model_class.column_name.in_(['value', 'value2']))
            conditions.append(model_class.column_name.like('%value%'))
            conditions.append(model_class.column_name.ilike('%value%'))
            conditions.append(model_class.column_name.is_(None))
            conditions.append(model_class.column_name.isnot(None))
            conditions.append(model_class.column_name.between(1, 10))
            conditions.append(model_class.column_name.notbetween(1, 10))

        """
        
       
        conditions = conditions or []
        
        if isinstance(conditions, list) and primary_keys:
            primary_keys_list = list(model_class.__table__.primary_key.columns)
            if not primary_keys_list:
                raise ValueError(f"Model {model_class.__name__} has no primary key!")
            primary_key = primary_keys_list[0].name
            condition = getattr(model_class, primary_key).in_(primary_keys)
            conditions.append(condition)

        
        

        def operation(session:Session):
            if isinstance(conditions, str) and conditions == 'ALL':
                deleted_count = session.query(model_class).delete(synchronize_session=False)
            elif isinstance(conditions, list):
                deleted_count = session.query(model_class).filter(and_(*conditions)).delete(synchronize_session=False)
            else:   
                deleted_count=0
                
            return deleted_count


        result=self.execute_transaction(operation) 
        return result if result is not None else 0

    def get_record_count(self,model_class,conditions:List=None):
        """
        Returns the count of records in the specified model's table, optionally filtered by conditions.

        Args:
            model_class: The ORM model class representing the database table.
            conditions (List, optional): A list of SQLAlchemy filter conditions to apply. 
                If None, all records are counted.

        Returns:
            int: The number of records matching the given conditions. Returns 0 if no result is found.
        """


        
        
        def operation(session:Session):
            
            query = session.query(func.count()).select_from(model_class)
            
            # Apply filters
            if conditions :
                query = query.filter(and_(*conditions))
            return query.scalar()

        result=self.execute_transaction(operation) 
        return result if result is not None else 0

