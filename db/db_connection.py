# db/db_connection.py
import pymysql

def create_connection():
    try:
        conn = pymysql.connect(
            host='localhost',     # XAMPP default host
            user='root',          # Default MySQL user in XAMPP
            password='',          # Default empty password in XAMPP
            database='library_db' # Your database name
        )
        return conn
    except pymysql.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None