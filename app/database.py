from psycopg2 import pool
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

try: 
    postgreSql_pool = pool.SimpleConnectionPool(
        1, 20,
        dsn=DATABASE_URL
    )
    print("Connection pool created successfully")
except Exception as e:
    print("Error while connection pool: {e}")