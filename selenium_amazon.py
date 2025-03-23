import csv
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Base Amazon search URL with "monitors" keyword and page placeholder
base_url = "https://www.amazon.com/s?k=monitors&page={}"

# Configure Firefox options
firefox_options = Options()
HEADLESS = False  # Set to True for headless mode (no browser window)

if HEADLESS:
    firefox_options.add_argument("--headless")

firefox_options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"
)
firefox_options.add_argument("--disable-blink-features=AutomationControlled")
firefox_options.set_preference("dom.webdriver.enabled", False)
firefox_options.set_preference("useAutomationExtension", False)

# Initialize Firefox WebDriver
print("Starting Firefox WebDriver...")
try:
    driver = webdriver.Firefox(options=firefox_options)
except Exception as e:
    print(f"Failed to initialize WebDriver: {e}")
    exit()

try:
    # Open a single CSV file for all data
    csv_filename = "amazon_monitors_products.csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Name", "Price", "Rating", "Image"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Iterate over the first three pages
        for page in range(1, 4):  # Pages 1, 2, 3
            url = base_url.format(page)
            print(f"\nProcessing page {page}...")

            # Navigate to the search page
            driver.get(url)
            print(f"Navigating to {url}")

            # Wait for search results to appear
            print("Waiting for search results...")
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-component-type='s-search-result']"))
            )
            print("Search results detected.")

            # Small delay for dynamic content (optional)
            time.sleep(2)

            # Locate all product containers on the page
            products = driver.find_elements(By.CSS_SELECTOR, "[data-component-type='s-search-result']")
            print(f"Total products found on page {page}: {len(products)}")

            # Process each product on the page
            for i, product in enumerate(products, 1):
                print(f"Processing product {i} on page {page}...")

                # --- Extract Product Name ---
                try:
                    name_elem = product.find_element(By.CSS_SELECTOR, "h2 span.a-size-medium")
                    name = name_elem.text.strip()
                except:
                    try:
                        name_elem = product.find_element(By.CSS_SELECTOR, "h2")
                        name = name_elem.text.strip()
                    except:
                        name = "No name"

                # --- Extract Product Price ---
                price = None  # Default to None (null in output)
                try:
                    no_offers_elem = product.find_element(By.CSS_SELECTOR, "span.a-size-base.a-color-secondary")
                    if "No featured offers available" in no_offers_elem.text:
                        print(f"No featured offers for product {i} on page {page}")
                    else:
                        price_elem = WebDriverWait(product, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "span.a-price span.a-offscreen"))
                        )
                        price = price_elem.text.strip()
                        if price:
                            print(f"Featured price found: {price}")
                except:
                    print(f"Featured price not found for product {i} on page {page}")
                    try:
                        symbol = product.find_element(By.CSS_SELECTOR, "span.a-price-symbol").text
                    except:
                        symbol = "$"
                    try:
                        whole = product.find_element(By.CSS_SELECTOR, "span.a-price-whole").text
                    except:
                        whole = ""
                    try:
                        fraction = product.find_element(By.CSS_SELECTOR, "span.a-price-fraction").text
                    except:
                        fraction = "00"
                    if whole:
                        whole = whole.replace(".", "")
                        price = f"{symbol}{whole}.{fraction}"
                        print(f"Fractured featured price constructed: {price}")
                    else:
                        print(f"No valid featured price for product {i} on page {page}")

                # --- Extract Product Rating ---
                try:
                    rating_elem = product.find_element(By.CSS_SELECTOR, "[aria-label*='out of 5 stars']")
                    rating = rating_elem.get_attribute("aria-label").split()[0]
                except:
                    rating = "No rating"

                # --- Extract Product Image ---
                try:
                    image_elem = product.find_element(By.CSS_SELECTOR, "img.s-image")
                    image = image_elem.get_attribute("src")
                except:
                    image = "No image"

                # --- Validate Extracted Data ---
                if name == "No name" or not name:
                    print(f"Skipping product {i} on page {page} due to missing name")
                    continue
                if rating == "No rating" or not rating:
                    print(f"Skipping product {i} on page {page} due to missing rating")
                    continue
                if image == "No image" or not image:
                    print(f"Skipping product {i} on page {page} due to missing image")
                    continue

                # --- Save to CSV ---
                writer.writerow({"Name": name, "Price": price, "Rating": rating, "Image": image})

                # --- Display Product Details ---
                print(f"Name: {name}")
                print(f"Price: {price if price is not None else 'null'}")
                print(f"Rating: {rating}")
                print(f"Image: {image}")
                print("-" * 50)

    print(f"All data has been saved to '{csv_filename}'")

except Exception as e:
    # Handle any unexpected errors
    print(f"An error occurred: {str(e)}")
    print("Dumping page source for debugging...")
    with open("debug_page_source.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)

finally:
    # Ensure WebDriver is closed
    print("Closing WebDriver...")
    driver.quit()