import requests
from bs4 import BeautifulSoup
import json

print('starting')

proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}
print('configured')

main_url = 'http://arcuufpr5xxbbkin4mlidt7itmr6znlppk63jbtkeguuhszmc5g7qdyd.onion/'

try:
    response = requests.get(main_url, proxies=proxies, timeout=120)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a', class_='link')

    all_page_contents = []

    for link in links:
        post_url = link.get('href')
        if post_url:
            print(f'Fetching content from: {post_url}')
             
            page_response = requests.get(post_url, proxies=proxies, timeout=120)
            page_response.raise_for_status()
            
            page_soup = BeautifulSoup(page_response.content, 'html.parser')

            # Extracting the required information
            company_info = {}

            # Extract the company name (e.g., BRAZIL GOV)
            company_name = page_soup.find('h1').text.strip()
            company_info['company'] = company_name

            # Extract the time (e.g., datetime="2024-05-08T00:01:57+00:00")
            time_element = page_soup.find('time', class_='published')
            if time_element:
                company_info['time'] = time_element['datetime']

            # Extract the description (the paragraph text)
            description_element = page_soup.find('div', class_='yuki-article-content').find('p')
            if description_element:
                company_info['description'] = description_element.get_text(separator=" ").strip()

            all_page_contents.append(company_info)

    # Save all scraped content to a JSON file
    with open('output.json', 'w', encoding='utf-8') as json_file:
        json.dump(all_page_contents, json_file, ensure_ascii=False, indent=4)

    print("All scraped content saved to 'output.json'") 

except requests.exceptions.RequestException as e:
    print(f"Error fetching the page: {e}")
