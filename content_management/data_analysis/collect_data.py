import requests
import pandas as pd
import time

# Function to fetch and merge data from two APIs
def fetch_and_process_data():
    # API URLs
    post_api_url = "http://127.0.0.1:8004/posts/"
    post_engagement_api_url_template = "http://127.0.0.1:8004/posts/engagements"

    try:
        # Fetch data from the first API (posts)
        post_response = requests.get(post_api_url, timeout=None)
        post_response.raise_for_status()
        post_data = post_response.json()
        print("post data done", len(post_data))

        eng_respo = requests.get(post_engagement_api_url_template, timeout=None)
        eng_respo.raise_for_status()
        engagement_data = eng_respo.json()
 

        # Fetch engagement data for each post
        # engagement_data = []
        # for post in post_data:
        #     post_id = post.get("id")
        #     print("getting data for ", post_id)
        #     if post_id:
        #         engagement_url = post_engagement_api_url_template.format(post_id=post_id)
        #         engagement_response = requests.get(engagement_url, timeout=None)
        #         engagement_response.raise_for_status()
        #         engagement_data.append(engagement_response.json())

        print("engage data", len(engagement_data))
        # Convert to DataFrames
        posts_df = pd.DataFrame(post_data)
        posts_df.to_csv("post_data.csv")
        engagement_df = pd.DataFrame(engagement_data)
        engagement_df.to_csv("eng_data.csv")

        # posts_df = pd.read_csv("post_data.csv")
        # engagement_df = pd.read_csv("eng_data.csv")
        # Merge the data
        merged_df = pd.merge(posts_df, engagement_df, left_on="id", right_on="post_id", how="inner")


        # Print the shape of the merged dataset
        print("Shape of the merged dataset (rows, columns):", merged_df.shape)


        print("Data fetched and merged:")
        print(merged_df.head())
        print(f"Total rows in merged dataset: {len(merged_df)}")

        # Save the merged dataset as JSON
        merged_df.to_json("merged_dataset.json", orient="records", indent=4)
        print("Merged dataset saved to 'merged_dataset.json'.")

        # Preprocess the data
        preprocess_data(merged_df)

    except requests.exceptions.RequestException as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Basic data preprocessing: Handling nulls, describing dataset, and feature creation
def preprocess_data(df):
    # 1. Describe the dataset
    print("\nDataset Description:")
    print(df.describe(include="all"))  # Summary statistics of the dataset

    # 2. Find and replace null values
    print("\nHandling Null Values:")
    # Example null handling for specific columns
    for column in df.columns:
        if df[column].dtype == 'object':  # For categorical columns
            df[column].fillna(df[column].mode()[0], inplace=True)
        else:  # For numerical columns
            df[column].fillna(df[column].mean(), inplace=True)
    print("Null values replaced.")

    # 3. Basic data preprocessing
    print("\nPreprocessing Data:")
    # Example: Normalize numerical columns
    if 'likes' in df.columns and 'dislikes' in df.columns:
        df['normalized_likes'] = df['likes'] / df['likes'].max()
        df['normalized_dislikes'] = df['dislikes'] / df['dislikes'].max()

    # 4. Create new features
    print("\nCreating New Features:")
    if 'created_at' in df.columns and 'updated_at' in df.columns:
        df['post_age_days'] = (pd.to_datetime(df['updated_at']) - pd.to_datetime(df['created_at'])).dt.days
    print("New features created.")

    # Print final dataset info
    print("\nProcessed Data:")
    print(df.head())
    print(f"Total rows in processed dataset: {len(df)}")

    # Save the processed dataset to CSV
    df.to_csv("processed_dataset.csv", index=False)
    print("Processed dataset saved to 'processed_dataset.csv'.")

# Main execution
if __name__ == "__main__":
    fetch_and_process_data()
