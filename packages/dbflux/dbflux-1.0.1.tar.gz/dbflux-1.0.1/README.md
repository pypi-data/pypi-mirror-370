<h1 align="center">🚀 DBFlux: Lightweight Database Management Library</h1>

<p align="center">
<a href="https://pypi.org/project/dbflux/"><img src="https://img.shields.io/pypi/v/dbflux?style=plastic" alt="PyPI - Version"></a>
<a href="https://github.com/abbas-bachari/dbflux"><img src="https://img.shields.io/badge/Python%20-3.8+-green?style=plastic&logo=Python" alt="Python"></a>
  <a href="https://pypi.org/project/dbflux/"><img src="https://img.shields.io/pypi/l/dbflux?style=plastic" alt="License"></a>
  <a href="https://pepy.tech/project/dbflux"><img src="https://pepy.tech/badge/dbflux?style=flat-plastic" alt="Downloads"></a>
</p

## 🛠️ Version 1.0.1

## 🌟 **Introduction**

#### **DBFlux** is a lightweight, easy-to-use library built on top of **SQLAlchemy** to simplify database operations in Python.  

#### It provides a streamlined interface for **connecting to databases**, **managing sessions**, and **performing CRUD operations** with minimal effort.

---

## ✨ **Features**

* 🔁 Automatic Transaction Management
* 🛠️ Session Handling
* 🔗 Flexibility – Supports multiple database engines via SQLAlchemy
* ⚡ Lightweight & Efficient
* 🔍 Advanced Filtering
* 📥 Data Insertion
* ✏️ Data Modification
* 📄 Easy Pagination
* 🛡️ Safe Deletion
* 📦 Consistent Output Handling

---

## 📚 **Requirements**

* **Python 3.8+**
* **SQLAlchemy >= 2.0**

---

## 🔧 **Installation**

Install **dbflux** via **pip**:

```bash
pip install dbflux
```

Or install from source:

```bash
git clone https://github.com/abbas-bachari/dbflux.git
cd dbflux
pip install .
```

---


## 💡 **Quick Start**

```python

from dbflux  import Sqlite,DBModel
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base
from time import time

Base=declarative_base()
db = Sqlite(db_name="example.db")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100))

class Order(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True)
    product = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    time = Column(Integer, nullable=False)

db.create_tables(Base)


users=DBModel(User,db)
orders=DBModel(Order,db)


users_data=[
    {"id": 1, "name": "Alice", "email": "alice@test.com"},
    {"id": 2, "name": "Bob", "email": "bob@test.com"},
    {"id": 3, "name": "Carol", "email": "carol@test.com"}
]

orders_data=[
    {"order_id": 1, "product": "Product A", "price": 100, "time": time()},
    {"order_id": 2, "product": "Product B", "price": 200, "time": time()},
    {"order_id": 3, "product": "Product C", "price": 300, "time": time()}
]

users.insert(users_data)
orders.insert(orders_data)

```

---

## 💡 **Examples Usage DBFactory**

```python
from dbflux import DBFactory,DBModel
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base
from time import time

Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True)
    product = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    time = Column(Integer, nullable=False)



factory = DBFactory(db_name="data.db")
db = factory.create("sqlite")
db.create_tables(Base)
orders_db = DBModel(Order ,db)


order = Order(order_id=1, product="Product A", price=100, time=time())
orders_db.insert( order)

orders = orders_db.get(limit=1).to_json()

print(orders)
```

---

### Result:

```python
[
    {
        "price": 100.0,
        "time": 1755565113.9635222,
        "order_id": 1,
        "product": "Product A"
    }
]
```

---

## 🔹 Supported Database Types

| Type       | Aliases              |
| ---------- | -------------------- |
| SQLite     | sqlite               |
| MySQL      | mysql                |
| PostgreSQL | postgres, postgresql |
| MariaDB    | mariadb              |
| Oracle     | oracle               |
| DB2        | db2, ibmdb2          |
| Firebird   | firebird             |
| MSSQL      | mssql, sqlserver     |

---

## 🔹 Examples for Different Databases

```python
from dbflux.databases import Sqlite, MySQL, PostgreSQL

# Example 1: SQLite
sqlite_db = Sqlite(db_name="data.db")
sqlite_db.create_tables(Base)
sqlite_db.insert(model_class= Order ,data=Order(order_id=10, product="SQLite Product", price=50, time=time()))

# Example 2: MySQL
mysql_db = MySQL(db_name="test_db",username="root", password="password", host="localhost", )
mysql_db.create_tables(Base)
mysql_db.insert(model_class= Order ,data=Order(order_id=11, product="MySQL Product", price=60, time=time()))

# Example 3: PostgreSQL
postgres_db = PostgreSQL(db_name="test_db",username="postgres", password="secret", host="localhost")
postgres_db.create_tables(Base)
postgres_db.insert(model_class= Order ,data=Order(order_id=12, product="PostgreSQL Product", price=70, time=time()))
```

---

### 🎯 Summary of Features

#### ✅ CRUD Operations  

#### ✅ Bulk Insert & Bulk Update  

#### ✅ Advanced Filtering (OR/AND/Range)  

#### ✅ Pagination  

#### ✅ JSON Output  

#### ✅ Transaction Safety  

#### ✅ Direct SQLAlchemy Access via BaseDB  

---

## 📖 **Documentation**

For more details, visit the [official SQLAlchemy documentation](https://docs.sqlalchemy.org/).

---

## 📜 **License**

This project is licensed under the **[MIT License](LICENSE)**.

---

## 👤 **Publisher / ناشر**

**[Abbas Bachari / عباس بچاری](https://github.com/abbas-bachari)**

---

## 💖 **Sponsor**

Support development by sponsoring on **[Github Sponsors](https://github.com/sponsors/abbas-bachari)**.
