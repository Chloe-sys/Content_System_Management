import csv
import pymysql
import mysql.connector

def insert_data_into_db(csv_file):
    try:
        # Establish MySQL connection
        conn = pymysql.connect(
            host="localhost",          # Your MySQL server host
            user="root",               # Your MySQL username
            password="12345",          # Your MySQL password
            database="content_system_management",  # Your database name
            port=3306                  # MySQL default port
        )

        cursor = conn.cursor()

        # Open the CSV file
        with open('generated_data.csv', "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)  # Read CSV data
            for row in reader:
                cursor.execute(
                    """
                    INSERT INTO content_system_post (title, overview, content, created_at, updated_at)
                    VALUES (%s, %s, %s, NOW(), NOW())
                    """, (
                        row['title'],       # Map to the 'title' column in the CSV
                        row['overview'],    # Map to the 'overview' column in the CSV
                        row['content'],     # Map to the 'content' column in the CSV
                    )
                )

        # Commit changes and close the connection
        conn.commit()
        cursor.close()
        conn.close()

        print("Data insertion complete.")

    except mysql.connector.Error as err:
        print(f"MySQL error: {err}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    csv_file = "generated_data.csv"  # Path to your CSV file
    insert_data_into_db(csv_file)  # Insert data into the database

