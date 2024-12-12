import csv
import mysql.connector
import pymysql

# Function to insert data into MySQL using mysql-connector
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
        with open(csv_file, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)  # Read CSV data
            data_to_insert = []

            # Loop through each row in the CSV and prepare the data for insertion
            for row in reader:
                data_to_insert.append((
                    row['user_id'],  # Assuming your CSV has 'user_id'
                    row['post_id'],  # Assuming your CSV has 'post_id'
                    row['liked'] == 'True'  # Convert 'liked' column (string) to boolean
                ))

        # Insert data in batches using executemany
        cursor.executemany(
            """
            INSERT INTO content_system_likedislike (user_id, post_id, liked)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE liked=VALUES(liked);
            """, data_to_insert
        )

        # Commit changes and close the connection
        conn.commit()
        cursor.close()
        conn.close()

        print(f"Data from {csv_file} inserted successfully.")

    except mysql.connector.Error as err:
        print(f"MySQL error: {err}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Run the function to insert data
if __name__ == "__main__":
    csv_file = "like_dislike_data.csv"  # Path to your CSV file
    insert_data_into_db(csv_file)  # Insert data into the database
