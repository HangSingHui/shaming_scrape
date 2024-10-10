import requests
from bs4 import BeautifulSoup
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# The onion URL you want to scrape
url = "http://kill432ltnkqvaqntbalnsgojqqs2wz4lhnamrqjg66tq6fuvcztilyd.onion/index.php"

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

    # Extract the list of companies
    companies = []
    post_blocks = soup.find_all('a', class_='post-block unleaked')
    
    for post in post_blocks:
        company_info = {}
        company_info['name'] = post.find('div', class_='post-title').get_text(strip=True)
        company_info['url'] = post['href']
        company_info['description'] = post.find('p', class_='post-block-text').get_text(strip=True)
        
        # Append the company info to the list
        companies.append(company_info)

    # Save the data to a JSON file
    with open("killsecurity_companies.json", "w") as f:
        json.dump(companies, f, indent=4)

    print("Data saved to killsecurity_companies.json")

else:
    print(f"Failed to reach the site. Status code: {response.status_code}")
