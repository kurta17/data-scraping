import requests
from bs4 import BeautifulSoup
import csv

# Set headers to mimic browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Send request to the website
url = "https://old.reddit.com/new/"
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

# Find all post containers
posts = soup.find_all('div', class_='thing')

# Create list to store post data
post_data = []

# Extract information for each post
for post in posts:
    # Title
    title = post.find('a', class_='title')
    title_text = title.text.strip() if title else "No title found"
    
    # Score
    score = post.find('div', class_='score')
    score_text = score.text.strip() if score else "0"
    
    # Number of comments
    comments = post.find('a', class_='comments')
    comments_text = comments.text.strip() if comments else "0 comments"
    
    # Add to list
    post_data.append({
        'title': title_text,
        'score': score_text,
        'comments': comments_text
    })

# Save to CSV
with open('reddit_new_posts.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['title', 'score', 'comments'])
    writer.writeheader()
    writer.writerows(post_data)

print("Data has been scraped and saved to reddit_new_posts.csv")