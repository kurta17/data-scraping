import requests
import json

# Endpoint URL
url = "https://harbour.space/api/v1/schedule?include=course&first_year=2024&campus=bangkok"

# Send GET request
response = requests.get(url)

# Check if request was successful
if response.status_code == 200:
    data = response.json()  # Parse response JSON
    with open("courses_data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print("Data saved successfully to courses_data.json")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
