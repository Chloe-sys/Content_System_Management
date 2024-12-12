import requests
import pandas as pd
import random
from faker import Faker

def fetch_and_merge_data():
    post_api_url = "http://127.0.0.1:8002/posts/"
    post_engagement_api_url_template = "http://127.0.0.1:800/posts/{post_id}/engagement"
    fake = Faker()

    try:
        # Fetch posts (pagination in case of many posts)
        post_data = []
        page = 1
        while True:
            post_response = requests.get(post_api_url, params={"page": page})
            post_response.raise_for_status()
            posts = post_response.json()
            if not posts:
                break
            post_data.extend(posts)
            page += 1

        # Fetch engagement data for each post
        engagement_data = []
        for post in post_data:
            post_id = post.get("id")
            if post_id is not None:
                engagement_url = post_engagement_api_url_template.format(post_id=post_id)
                engagement_response = requests.get(engagement_url)
                engagement_response.raise_for_status()
                engagement_data.append(engagement_response.json())

        # Convert to DataFrames
        posts_df = pd.DataFrame(post_data)
        engagement_df = pd.DataFrame(engagement_data)

        if posts_df.empty or engagement_df.empty:
            print("One or both datasets are empty.")
            return

        # Merge on `post_id` (make sure this matches the key name in both DataFrames)
        merged_df = pd.merge(posts_df, engagement_df, left_on="id", right_on="post_id", how="inner")

        # Generate additional synthetic data to meet the 500,000 rows
        additional_data_needed = 500000 - len(merged_df)
        if additional_data_needed > 0:
            synthetic_data = [
                {
                    "title": fake.sentence(nb_words=6),
                    "overview": fake.text(max_nb_chars=200),
                    "content": fake.text(),
                    "engagement_count": random.randint(1, 1000),  # Example: generate fake engagement count
                    "post_id": random.randint(1, len(post_data))  # Simulate engagement with random post
                }
                for _ in range(additional_data_needed)
            ]
            synthetic_df = pd.DataFrame(synthetic_data)
            merged_df = pd.concat([merged_df, synthetic_df], ignore_index=True)

        print(merged_df.shape)
        print(merged_df.isnull().sum())
        merged_df.ffill(inplace=True)

        # Save merged data to CSV (adjust file path as needed)
        output_file = "merged_dataset.csv"
        merged_df.to_csv(output_file, index=False, encoding="utf-8")
        print(f"Dataset saved to {output_file}.")

    except requests.exceptions.RequestException as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    fetch_and_merge_data()
