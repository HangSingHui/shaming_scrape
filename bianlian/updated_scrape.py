import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time  # Optional: to avoid overloading the server with requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# BianLian Onion URL 
base_url = "http://bianlianlbc5an4kgnay3opdemgcryg2kpfcbgczopmm3dnbz3uaunad.onion"

# Set up SOCKS5 proxies for Tor
proxies = {
    'http': 'socks5h://127.0.0.1:9150',
    'https': 'socks5h://127.0.0.1:9150'
}

# Date range for filtering (Jan to Aug 2024)
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 8, 31)

# Send the initial request to the main page
response = requests.get(base_url + "/companies/", proxies=proxies, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the page content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract list of posts and metadata
    companies = []
    posts = soup.find('ul', class_='posts').find_all('li', class_='post')
    
    for post in posts:
        company_info = {}
        company_info['name'] = post.find('a').get_text(strip=True)
        company_info['url'] = post.find('a')['href']
        date_str = post.find('span', class_='meta').get_text(strip=True)
        
        # Parse the date string into a datetime object
        company_date = datetime.strptime(date_str, "%b %d, %Y")
        
        # Check if the post date is between Jan and Aug 2024
        if start_date <= company_date <= end_date:
            company_info['date'] = date_str
            
            # Go into each post to extract detailed information
            company_page_url = base_url + company_info['url']
            company_response = requests.get(company_page_url, proxies=proxies, headers=headers)
            
            if company_response.status_code == 200:
                company_soup = BeautifulSoup(company_response.text, 'html.parser')
                
                # Content extraction
                company_content = {}

                # Extract the title of the post (company name)
                title_section = company_soup.find('h1', class_='title')
                if title_section:
                    company_content['title'] = title_section.get_text(strip=True)
                
                # Extract links within the post
                post_links = [a['href'] for a in company_soup.find_all('a', href=True)]
                company_content['links'] = post_links

                # Extract description paragraphs
                paragraphs = [p.get_text(strip=True) for p in company_soup.find_all('p')]
                company_content['description'] = paragraphs

                # Extract preformatted code sections
                code_sections = [pre.get_text(strip=True) for pre in company_soup.find_all('pre')]
                company_content['code_sections'] = code_sections

                # Extract list items (data description bullet points)
                list_items = [li.get_text(strip=True) for li in company_soup.find_all('li')]
                company_content['list_items'] = list_items

                # Wait before making the next request to avoid overloading the server
                time.sleep(1)

                # Add the dynamically extracted content to the company_info
                company_info['details'] = company_content

            # Add the company info to the list of companies
            companies.append(company_info)

    # Compile all data
    result = {
        'companies': companies
    }

    # Save the data to a JSON file
    with open("bianlian_companies_updated.json", "w") as f:
        json.dump(result, f, indent=4)

else:
    # Error message
    print(f"Failed to reach the site. Status code: {response.status_code}")
