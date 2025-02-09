import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_PUBLIC_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # If the connection is successful, you can execute a simple query
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"PostgreSQL version: {version}")

    print("Connection to Railway PostgreSQL successful!")

except psycopg2.Error as e:
    print(f"Error connecting to PostgreSQL: {e}")

finally:
    if conn:
        cur.close()
        conn.close()
        print("Connection closed.")
