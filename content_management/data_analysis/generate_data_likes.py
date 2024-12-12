import csv
from faker import Faker
import random

# Dummy data for users and posts - in a real case, you would fetch these from the database
user_ids = [i for i in range(1, 1001)]  # Example: 1000 users
post_ids = [i for i in range(1, 5001)]  # Example: 5000 posts

def generate_like_dislike_data(num_records):
    fake = Faker()
    data = []
    
    for _ in range(num_records):
        user_id = random.choice(user_ids)  # Random user ID from existing users
        post_id = random.choice(post_ids)  # Random post ID from existing posts
        liked = random.choice([True, False])  # Randomly choose if the user liked or disliked the post

        data.append({
            "user_id": user_id,
            "post_id": post_id,
            "liked": liked,
        })
        
    return data

def save_to_csv(data, output_file="like_dislike_data.csv"):
    # Save the generated data to a CSV file
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["user_id", "post_id", "liked"])
        writer.writeheader()
        writer.writerows(data)

    print(f"Successfully generated and saved {len(data)} rows to {output_file}.")

if __name__ == "__main__":
    num_records = 500  # Number of rows to generate
    data = generate_like_dislike_data(num_records)  # Generate the fake data
    save_to_csv(data)  # Save the data to a CSV file
