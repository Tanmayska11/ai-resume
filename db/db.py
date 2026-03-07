import psycopg2
from contextlib import contextmanager
import os
from dotenv import load_dotenv
import psycopg2.extras  

load_dotenv()
psycopg2.extras.register_uuid()

@contextmanager
def get_db_conn():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
