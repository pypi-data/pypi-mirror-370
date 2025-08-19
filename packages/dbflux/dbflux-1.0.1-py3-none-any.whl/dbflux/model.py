
from typing import Union, Dict, Any, List
from .base import BaseDB





class DBModel:
    


    def __init__(self, model_class, db: BaseDB):
        """
        Initializes the DBModel wrapper.

        Args:
            model_class: The ORM model class.
            db (BaseDB): An instance of BaseDB to delegate operations.
        """
        self._model_class = model_class
        self._db: "BaseDB" = db  # اینجا تایپ‌هینت باعث می‌شه IDE مستندات رو بشناسه


    def create_tables(self, Base)-> bool:
        """Create tables if they don't exist"""
        self._db.create_tables(Base)
        
        
    def insert(self,  data: Union[Dict[str, Any], object, List[Dict[str, Any]], List[object]]):
        """
            Insert one or multiple records into the database table associated with the specified SQLAlchemy model class.

            Parameters
            ----------
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
            >>> db.insert({"id": 1, "name": "Alice"})
            1

            >>> db.insert([User(id=2, name="Bob"), User(id=3, name="Carol")])
            2

            >>> db.insert([])
            0

            """
        return self._db.insert(self._model_class, data)


    def get(self, limit=None,conditions:list=None, order_by=None,descending=False ) :
        """
            Retrieve records from the database using SQLAlchemy filter conditions.

            Args:
                limit (int, optional): Maximum number of records to retrieve. 
                    If set to 1, only a single record will be returned. Defaults to None.
                conditions (List, optional): A list of SQLAlchemy filter conditions. Defaults to None.
                order_by (str, optional): Column name to order the results by. Defaults to None.
                descending (bool, optional): Whether to sort results in descending order. Defaults to False.

            Returns:
                List: A list of records retrieved from the database.

            Examples:
                ### Retrieve one user by ID
                user = db.get(limit=1, conditions=[User.id == 1])

                ### Retrieve all active users
                users = db.get(conditions=[User.active == True])

                ### Retrieve the 5 newest users
                latest_users = db.get(limit=5, order_by="created_at", descending=True)

                ## Example of different filter conditions:

                ### Equal
                users = db.get(conditions=[User.id == 1])

                ### Not equal
                users = db.get(conditions=[User.id != 1])

                ### IN list
                users = db.get(conditions=[User.id.in_([1, 2])])

                ### LIKE
                users = db.get(conditions=[User.name.like('%value%')])

                ### ILIKE (case-insensitive LIKE)
                users = db.get(conditions=[User.name.ilike('%value%')])

                ### IS NULL
                users = db.get(conditions=[User.name.is_(None)])

                ### IS NOT NULL
                users = db.get(conditions=[User.name.isnot(None)])

                ### BETWEEN
                users = db.get(conditions=[User.id.between(1, 10)])
            """

        return self._db.get(self._model_class, limit, conditions, order_by, descending)
           
      
       
    
    def update(self,   conditions: List | None,update_fields: Dict):
        """
        Bulk update existing records in a table using SQLAlchemy ORM.

        Args:
           conditions: Optional list of SQLAlchemy filter conditions (e.g., [User.active == True]).
                        If None, all rows will be updated.
            update_fields: Dictionary of column names and their new values.
            

        Returns:
            int: Number of records updated.

        Notes:
            - Works across all major databases supported by SQLAlchemy (SQLite, MySQL, PostgreSQL, MSSQL, Oracle, etc.).
            - Only updates existing rows; no new rows are inserted.

        Example:
            # Update only active users
            updated_count = db.update(
                conditions=[User.active == True],
                update_fields={'status': 'inactive'}
                
            )

            # Update all users
            updated_count = db.update(
                conditions=None,
                update_fields={'status': 'inactive'}
                
            )
        """
        return self._db.update(self._model_class, conditions, update_fields)
        
    
    def bulk_update(self,  updates: List[Dict]) :
        """
        Perform a bulk update on multiple rows of a table efficiently.

        This method uses SQLAlchemy's `bulk_update_mappings` to update multiple
        records in a single operation without loading them into memory as full objects.

        Args:
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
            updated_count = db.bulk_update(updates)
            print(f"{updated_count} records updated.")
        """
        return self._db.bulk_update(self._model_class, updates)
       

    def paginate(self,  conditions: List=None, page: int = 1, per_page: int = 10,order_by=None,descending=False):
       """Retrieve paginated records from the database.
        Args:
            conditions (List, optional): A list of SQLAlchemy filter conditions. Defaults to None.
            page (int, optional): The page number to retrieve. Defaults to 1.
            per_page (int, optional): The number of records per page. Defaults to 10.

        Returns:
            List: A list of records retrieved from the database.
        
        ### Example usage of different conditions:
            conditions=[]
            conditions.append(User.id == 1)
            conditions.append(User.id != 1)
            conditions.append(User.id.in_([1, 2]))
            conditions.append(User.name.like('%value%'))
            conditions.append(User.name.ilike('%value%'))
            conditions.append(User.name.is_(None))
            conditions.append(User.name.isnot(None))
            conditions.append(User.id.between(1, 10))
            conditions.append(User.id.notbetween(1, 10))
        """
    
       return self._db.paginate(self._model_class, conditions, page, per_page,order_by,descending)
        
    def delete(self,  conditions: List|str=None,primary_keys:List[Any]=[]) -> int:
       """Delete records from the database based on the given conditions.

        Args:
            conditions (List|str): A list of SQLAlchemy filter conditions or a string 'ALL' to delete all records of the model_class.
            primary_keys (List[Any]): A list of primary key values to delete. If not provided, the primary key of the model_class is determined automatically.

        Returns:
            int: Number of rows deleted.

        ### Example usage of different conditions:
            conditions=[]
            conditions.append(User.id == 1)
            conditions.append(User.id != 1)
            conditions.append(User.id.in_([1, 2]))
            conditions.append(User.name.like('%value%'))
            conditions.append(User.name.ilike('%value%'))
            conditions.append(User.name.is_(None))
            conditions.append(User.name.isnot(None))
            conditions.append(User.id.between(1, 10))
            conditions.append(User.id.notbetween(1, 10))

        """
       return self._db.delete(self._model_class, conditions,primary_keys)

    def get_record_count(self,conditions:List=None):
        """
        Returns the count of records in the specified model's table, optionally filtered by conditions.

        Args:
            conditions (List, optional): A list of SQLAlchemy filter conditions to apply. 
                If None, all records are counted.

        Returns:
            int: The number of records matching the given conditions. Returns 0 if no result is found.
        """
        return self._db.get_record_count(self._model_class,conditions)
        

