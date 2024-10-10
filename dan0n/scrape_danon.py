import requests
from bs4 import BeautifulSoup
import json

print('starting')

proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}
print('configured')

main_url = 'http://2c7nd54guzi6xhjyqrj5kdkrq2ngm2u3e6oy4nfhn3wm3r54ul2utiqd.onion/search?search=com'

try:
    response = requests.get(main_url, proxies=proxies, timeout=120)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a', class_='btn btn-dark btn-sm')

    all_page_contents = []

    for link in links:
        relative_url = link.get('href')
        if relative_url:
            full_url = f'http://2c7nd54guzi6xhjyqrj5kdkrq2ngm2u3e6oy4nfhn3wm3r54ul2utiqd.onion{relative_url}'
            print(f'Fetching content from: {full_url}')
            
            page_response = requests.get(full_url, proxies=proxies, timeout=120)
            page_response.raise_for_status()
            
            page_soup = BeautifulSoup(page_response.content, 'html.parser')

            # Extracting the required information
            company_info = {}

            # Extracting time from the h4 tag with class 'timer'
            company_info['time'] = page_soup.find('h4', class_='timer')['data-deadline']

            # Extracting attributes like Country, Website, Revenue, Industry
            attrs = page_soup.find_all('p', class_='attrs')
            for attr in attrs:
                if 'Country' in attr.text:
                    company_info['country'] = attr.find('span', class_='old').text.strip()
                elif 'Website' in attr.text:
                    company_info['website'] = attr.find('span', class_='old').text.strip()
                elif 'Revenue' in attr.text:
                    company_info['revenue'] = attr.find('span', class_='old').text.strip()
                elif 'Industry' in attr.text:
                    company_info['industry'] = attr.find('span', class_='old').text.strip()

            # Extracting description text
            description = page_soup.find('p', class_='card-text justify')
            company_info['description'] = description.text.strip() if description else "No description available"

            all_page_contents.append(company_info)

    # Save all scraped content to a JSON file
    with open('output.json', 'w', encoding='utf-8') as json_file:
        json.dump(all_page_contents, json_file, ensure_ascii=False, indent=4)

    print("All scraped content saved to 'output.json'")

except requests.exceptions.RequestException as e:
    print(f"Error fetching the page: {e}")
