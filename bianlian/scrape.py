import requests
from bs4 import BeautifulSoup
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# The onion URL you want to scrape
url = "http://bianlianlbc5an4kgnay3opdemgcryg2kpfcbgczopmm3dnbz3uaunad.onion/companies/"

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

    # Extract the header information
    header = {}
    header['main'] = soup.find('div', class_='main').a.get_text(strip=True)
    header['nav_links'] = [a.get_text(strip=True) for a in soup.find('nav').find_all('a')]

    # Extract the site description
    site_description = {}
    description_section = soup.find('div', class_='site-description')
    site_description['work_with_us'] = description_section.find_all('p')[0].get_text(strip=True)
    site_description['tox'] = description_section.find_all('p')[1].get_text(strip=True)
    site_description['email'] = description_section.find_all('p')[2].get_text(strip=True)

    # Extract the list of companies and their metadata
    companies = []
    posts = soup.find('ul', class_='posts').find_all('li', class_='post')
    
    for post in posts:
        company_info = {}
        company_info['name'] = post.find('a').get_text(strip=True)
        company_info['url'] = post.find('a')['href']
        company_info['date'] = post.find('span', class_='meta').get_text(strip=True)
        companies.append(company_info)

    # Compile all data into a final dictionary
    result = {
        'header': header,
        'site_description': site_description,
        'companies': companies
    }

    # Save the data to a JSON file
    with open("bianlian_companies.json", "w") as f:
        json.dump(result, f, indent=4)

else:
    print(f"Failed to reach the site. Status code: {response.status_code}")
