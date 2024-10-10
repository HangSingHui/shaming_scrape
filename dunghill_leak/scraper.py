import requests
from bs4 import BeautifulSoup
import json

def get_tor_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5h://127.0.0.1:9150',
                       'https': 'socks5h://127.0.0.1:9150'}
    return session

def fetch_and_parse(url, session):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_company_data(entity):
    info_dict = {}
    
    # Extract company name
    company_name_elem = entity.find('div', class_='ibody_title')
    info_dict['Company Name'] = company_name_elem.text.strip() if company_name_elem else "N/A"
    
    # Extract logo URL
    logo_img = entity.find('img')
    info_dict['Logo URL'] = logo_img['src'] if logo_img else "N/A"
    
    # Extract website and ZoomInfo URLs
    links = entity.find_all('a')
    info_dict['Website'] = "N/A"
    info_dict['ZoomInfo URL'] = "N/A"
    for link in links:
        if link.text.startswith('https://'):
            if 'zoominfo.com' in link.text:
                info_dict['ZoomInfo URL'] = link.text
            else:
                info_dict['Website'] = link.text
    
    # Extract description
    description_elem = entity.find('div', class_='ibody_body')
    info_dict['Description'] = description_elem.text.strip() if description_elem else "N/A"
    
    # Extract date and status
    footer = entity.find('div', class_='ibody_footer')
    if footer:
        date_elem = footer.find('p', string=lambda t: t and 'Date:' in t)
        status_elem = footer.find('p', string=lambda t: t and 'Status:' in t)
        info_dict['Date'] = date_elem.text.split(':')[1].strip() if date_elem else "N/A"
        info_dict['Status'] = status_elem.text.split(':')[1].strip() if status_elem else "N/A"
    else:
        info_dict['Date'] = "N/A"
        info_dict['Status'] = "N/A"
    
    # Extract views
    views_elem = entity.find('div', class_='counter_include')
    info_dict['Views'] = views_elem.text.strip() if views_elem else "N/A"
    
    return info_dict

def main():
    url = "http://nsalewdnfclsowcal6kn5csm4ryqmfpijznxwictukhrgvz2vbmjjjyd.onion/index.html"
    session = get_tor_session()
    
    soup = fetch_and_parse(url, session)
    if not soup:
        print("Failed to fetch and parse the webpage.")
        return
    
    data_objects = []
    entities = soup.find_all('div', class_='custom-container')
    
    for entity in entities:
        info_dict = extract_company_data(entity)
        
        # Get only records from 2024 onwards
        if info_dict['Date'] != "N/A" and info_dict['Date'][6:10] == "2024":
            # Fetch additional data from the company's specific page
            company_link = entity.find('a', class_='ibody_header')
            if company_link and 'href' in company_link.attrs:
                company_url = url.rsplit('/', 1)[0] + '/' + company_link['href']
                company_soup = fetch_and_parse(company_url, session)
                
                if company_soup:
                    additional_info = company_soup.find_all('div', class_='filling')
                    if len(additional_info) > 1:
                        content = additional_info[1].get_text(separator="\n", strip=True).split("\n")
                        info_dict["Additional Info"] = content
            
            data_objects.append(info_dict)
    
    # Save the data to a JSON file
    with open("extracted_data.json", "w") as f:
        json.dump(data_objects, f, indent=4)
    
    print(f"Extracted data for {len(data_objects)} companies from 2024 onwards.")

if __name__ == "__main__":
    main()
