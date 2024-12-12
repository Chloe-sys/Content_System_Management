import requests
import pandas as pd

def fetch_and_merge_data():
    post_api_url = "http://127.0.0.1:8002/posts/"
    post_engagement_api_url_template = "http://127.0.0.1:8002/posts/{post_id}/engagement"

    try:
        # Fetch posts
        post_response = requests.get(post_api_url)
        post_response.raise_for_status()
        post_data = post_response.json()

        # Print raw response to check if 'id' exists
        print("Raw Post Data:", post_data)

        # Fetch engagement data for each post
        engagement_data = []
        for post in post_data:
            # Print post data to inspect its structure
            print(f"Post Data: {post}")

            # Access the post ID (make sure to use the correct key)
            post_id = post.get("id")  # Ensure the key here matches what your API returns

            if post_id is not None:
                engagement_url = post_engagement_api_url_template.format(post_id=post_id)
                engagement_response = requests.get(engagement_url)
                engagement_response.raise_for_status()
                engagement_data.append(engagement_response.json())
            else:
                print(f"Skipping post with missing ID: {post}")

        # Convert to DataFrames
        posts_df = pd.DataFrame(post_data)
        engagement_df = pd.DataFrame(engagement_data)

        if posts_df.empty or engagement_df.empty:
            print("One or both datasets are empty.")
            return

        # Merge on `post_id` (make sure this matches the key name in both DataFrames)
        merged_df = pd.merge(posts_df, engagement_df, left_on="id", right_on="post_id", how="inner")

        print(merged_df.shape)
        print(merged_df.isnull().sum())
        merged_df.ffill(inplace=True)
        print(merged_df.dtypes)

        # Save merged data to JSON (standard format)
        output_file = "merged_dataset.json"
        merged_df.to_json(output_file, orient="records", indent=4)  # Standard JSON format with array
        print(f"Dataset saved to {output_file}.")

    except requests.exceptions.RequestException as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    fetch_and_merge_data()
