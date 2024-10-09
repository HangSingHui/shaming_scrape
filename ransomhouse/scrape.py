from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
import json

# Set up Selenium options
options = Options()
options.headless = True  # Run in headless mode (without opening a GUI)

# Specify the path to the GeckoDriver executable (update this path if needed)
gecko_driver_path = "/usr/local/bin/geckodriver"  # Ensure this path is correct

# Specify the path to the Firefox binary (Tor Browser path)
firefox_binary_path = "/Applications/Tor Browser.app/Contents/MacOS/firefox"  # Path to Tor Browser executable
options.binary_location = firefox_binary_path

# Create a new instance of the Firefox driver
service = FirefoxService(executable_path=gecko_driver_path)
browser = webdriver.Firefox(service=service, options=options)

# The onion URL you want to scrape
url = "http://zohlm7ahjwegcedoz7lrdrti7bvpofymcayotp744qhx6gjmxbuo2yid.onion/"

# Open the page
browser.get(url)

# Wait for the page to load
time.sleep(5)  # Adjust this time if necessary

# Get the page source and pass it to BeautifulSoup for parsing
html = browser.page_source
soup = BeautifulSoup(html, 'html.parser')

# List to hold the extracted records
records_list = []

# Function to check if the date is valid (within Jan to Sep 2024)
def is_valid_date(action_date_str):
    try:
        day, month, year = action_date_str.split('/')
        month = int(month)
        year = int(year)
        
        # Check the year and month
        if year < 2024 or month > 8:
            return False
        return True
    except:
        return False

# Find all the records
records = soup.find_all(class_='cls_record')

# Iterate through each record and extract the necessary information
for record in records:
    # Extract the element with class 'cls_recordTop' (company name)
    record_top = record.find(class_='cls_recordTop')
    if record_top:
        company_name = record_top.text.strip()
    
    # Extract the action date
    action_date_tag = record.find(text="Action date:").find_next('div')
    if action_date_tag:
        action_date_str = action_date_tag.text.strip()

        # Check if the action date is valid based on the string check
        if is_valid_date(action_date_str):
            # Append to records list as a dictionary
            records_list.append({
                "company": company_name,
                "date": action_date_str
            })

# Save the records list to a JSON file
with open("records.json", "w", encoding="utf-8") as json_file:
    json.dump(records_list, json_file, indent=4)

# Close the browser when done
browser.quit()

print("Data saved to 'records.json'")
