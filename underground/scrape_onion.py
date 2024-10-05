import requests
from bs4 import BeautifulSoup
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# The onion URL you want to scrape
url = "http://47glxkuxyayqrvugfumgsblrdagvrah7gttfscgzn56eyss5wg3uvmqd.onion/"

# Set up the proxies for Tor (SOCKS5)
proxies = {
    'http': 'socks5h://127.0.0.1:9150',
    'https': 'socks5h://127.0.0.1:9150'
}

# Send the request via Tor
response = requests.get(url, proxies=proxies, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the page content
    soup = BeautifulSoup(response.text, 'html.parser')

    data_objects = []
    # Get all divs with class "col-lg-6 col-12 mb-3"
    entities = soup.find_all('div', class_='col-lg-6 col-12 mb-3')

    # Iterate through each entity
    for entity in entities:
        info_dict = {}
        
        # Find both block__info elements within the entity
        blocks = entity.find_all('div', class_='block__info')
        
        for block in blocks:
            # Iterate through each key-value pair in the block
            details = block.find_all('div')
            for detail in details:
                key = detail.find('span').get_text(strip=True).rstrip(':')
                # Replace Cyrillic С with Latin C
                key = key.replace('\u0421', 'C')
                value = detail.find('p').get_text(strip=True)
                
                # Add the key-value pair to the dictionary
                info_dict[key] = value
        
        # Get only records from 2024 onwards
        if "Date" in info_dict and info_dict["Date"][6:10] != "2024":
            continue  # Skip records before 2024

        # Scrape the link to get the description and the type of data leaked
        link = entity.find('a', class_='stretched-link').get('href')
        full_url = url + link
        print(full_url)

        # new page response
        new_page_response = requests.get(full_url, proxies=proxies, headers=headers)
        if new_page_response.status_code == 200:  # Compare status code correctly
            new_soup = BeautifulSoup(new_page_response.text, 'html.parser')
            # Example: Extract description from the new page
            description = new_soup.find_all('div', class_='filling')
            print("Description")
            content = description[1].get_text(separator="\n", strip=True).split("\n")
            info_dict["Description"] = content

        # Append the dictionary to the list
        data_objects.append(info_dict)

    # Save the data to a JSON file
    with open("undergroundData.json", "w") as f:
        json.dump(data_objects, f, indent=4)

else:
    print(f"Failed to reach the site. Status code: {response.status_code}")
