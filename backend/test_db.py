from database import get_db_connection

try:
    connection = get_db_connection()
    print("Database connected successfully!")

    connection.close()
    print("Database connection closed.")

except Exception as e:
    print("Database connection failed:", e)