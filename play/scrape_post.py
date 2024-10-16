import requests
import json
import re  # Import the regular expression module
from bs4 import BeautifulSoup

def load_ids(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def scrape_data(extracted_ids):
    json_data = []

    for extracted_id in extracted_ids:
        url = f"http://k7kg3jqxang3wh7hnmaiokchk7qoebupfgoik6rha6mjpzwupwtj25yd.onion/topic.php?id={extracted_id}"
        
        # Use socks proxy if needed
        proxies = {
            'http': 'socks5h://127.0.0.1:9050',  # Adjust this if your SOCKS proxy is on a different port
            'https': 'socks5h://127.0.0.1:9050'
        }

        try:
            response = requests.get(url, proxies=proxies, timeout=20)
            response.raise_for_status()  # Raises an HTTPError if the response was unsuccessful

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extracting the company name from the <title> tag
            company = soup.title.text.strip()

            # Extracting industry info using "information:"
            text = soup.get_text()  # Get all text from the HTML
            industry_info_match = re.search(r'information:\s*', text)
            industry_info = industry_info_match.group(1).strip('<br>') if industry_info_match else "Not available"  # Get the extracted info or set default value

            # Extracting country
            country = soup.find("i", class_="location").next.strip()

            # Extracting website
            website = soup.find("i", class_="link").next.strip()

            # Extracting date_added 
            date_added_match = re.search(r'added:\s*([\d-]+)', text)
            date_added = date_added_match.group(1).strip() if date_added_match else "Not available"  # Get the extracted info or set default value

            # Extracting data_size 
            #data_size_match = re.search(r'amount of data:\s*([^<]+)', text)  
            data_size_match = re.search(r'\d+\s+[A-Za-z]{2}', text)

            data_size = data_size_match.group(1).strip() if data_size_match else "Not available"  # Get the extracted info or set default value

         
            # Extracting description using "comment:"
            description_match = re.search(r'comment:\s*([^<]+)', text)  
            description = description_match.group(1).strip('<br>') if description_match else "Not available"  # Get the extracted info or set default value

            # Extracting download_links
            download_links_match = re.search(r'DOWNLOAD LINKS:\s*(.*?)\s*Rar password:', text, re.DOTALL)
            download_links = [link.strip() for link in download_links_match.group(1).split('<br>')] if download_links_match else "Not available"  # Get the extracted info or set default value

            # Extracting password
            password_match = re.search(r'Rar password:\s*([^<]+)', text)  
            password = password_match.group(1).strip() if password_match else "Not available"  # Get the extracted info or set default value

            # Create a dictionary for the current entry
            entry = {
                "company": company,
                "industry information": industry_info,
                "country": country,
                "date": date_added,
                "website": website,
                "data size": data_size,
                "description": description,
                "download links": download_links,
                "password": password
            }

            json_data.append(entry)
            print(extracted_id)

        except Exception as e:
            print(f"Failed to scrape {url}: {e}")

    return json_data

def save_to_json(data, output_file):
    with open(output_file, 'w') as json_file:
        json.dump(data, json_file, indent=4)

if __name__ == "__main__":
    extracted_ids = load_ids('extracted_ids.txt')
    json_data = scrape_data(extracted_ids)
    save_to_json(json_data, 'output_data_2.json')
    print("Scraping and JSON generation completed!")
