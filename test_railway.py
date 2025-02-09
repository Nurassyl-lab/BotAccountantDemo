import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv
load_dotenv()

RAILWAY_DB_HOST = os.getenv("RAILWAY_DB_HOST")
RAILWAY_DB_PORT = os.getenv("RAILWAY_DB_PORT")
RAILWAY_DB_USER = os.getenv("RAILWAY_DB_USER")
RAILWAY_DB_PASSWORD = os.getenv("RAILWAY_DB_PASSWORD")

# Connect to PostgreSQL via Railway (this is for creating the new database)
def create_connection(db_name=None):
    conn = psycopg2.connect(
        host=RAILWAY_DB_HOST,
        port=RAILWAY_DB_PORT,
        user=RAILWAY_DB_USER,
        password=RAILWAY_DB_PASSWORD,
        dbname=db_name or "postgres"  # Connect to 'postgres' for initial DB creation
    )
    return conn

# Create a new database
def create_database():
    try:
        conn = create_connection()
        conn.autocommit = True  # Enable autocommit to allow DB creation
        cursor = conn.cursor()

        # Create a new database
        cursor.execute(sql.SQL("CREATE DATABASE {};").format(sql.Identifier("test_db")))
        print("Database 'test_db' created successfully.")
        
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error creating database: {e}")

# Connect to the new database
def connect_to_new_db():
    return create_connection(db_name="test_db")

# Create a table and insert data
def create_table_and_insert_data():
    try:
        conn = connect_to_new_db()
        cursor = conn.cursor()

        # Create a simple table
        cursor.execute("""
            CREATE TABLE test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100)
            );
        """)
        print("Table 'test_table' created successfully.")

        # Insert some data into the table
        cursor.execute("""
            INSERT INTO test_table (name) VALUES
            ('Alice'),
            ('Bob'),
            ('Charlie');
        """)
        print("Data inserted successfully.")

        # Commit the changes
        conn.commit()

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error creating table or inserting data: {e}")

# Retrieve data from the table
def retrieve_data():
    try:
        conn = connect_to_new_db()
        cursor = conn.cursor()

        # Query data from the table
        cursor.execute("SELECT * FROM test_table;")
        rows = cursor.fetchall()

        # Print the results
        print("Retrieved data:")
        for row in rows:
            print(row)

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error retrieving data: {e}")

# Running the test
def run_test():
    create_database()  # Step 1: Create database
    create_table_and_insert_data()  # Step 2: Create table and insert data
    retrieve_data()  # Step 3: Retrieve data

if __name__ == "__main__":
    run_test()

