import requests
from bs4 import BeautifulSoup
import csv

# Send request to the website
url = "https://books.toscrape.com/catalogue/page-1.html"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find all book containers
books = soup.find_all('article', class_='product_pod')

# Create list to store book data
book_data = []

# Extract information for each book
for book in books:
    # Title
    title = book.h3.a['title']
    
    # Price
    price = book.find('p', class_='price_color').text.strip()
    
    # Rating
    rating = book.p['class'][1]
    
    # Add to list
    book_data.append({
        'title': title,
        'price': price,
        'rating': rating
    })

# Save to CSV
with open('books.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['title', 'price', 'rating'])
    writer.writeheader()
    writer.writerows(book_data)

print("Data has been scraped and saved to books.csv")