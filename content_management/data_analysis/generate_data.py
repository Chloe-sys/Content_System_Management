import csv
from faker import Faker

def generate_data(num_records):
    fake = Faker()
    data = [
        {
            "title": fake.sentence(nb_words=6),  # Generate fake post title
            "overview": fake.text(max_nb_chars=200),  # Generate fake overview
            "content": fake.text(),  # Generate fake post content
        }
        for _ in range(num_records)
    ]
    return data

def save_to_csv(data, output_file="generated_data.csv"):
    # Save the generated data to a CSV file
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["title", "overview", "content"])
        writer.writeheader()
        writer.writerows(data)

    print(f"Successfully generated and saved {len(data)} rows to {output_file}.")

if __name__ == "__main__":
    num_records = 500000  # Number of rows to generate
    data = generate_data(num_records)  # Generate the fake data
    save_to_csv(data)  # Save the data to a CSV file
