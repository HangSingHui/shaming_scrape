import os
import json
import re  # Import the regular expression module
from bs4 import BeautifulSoup

def scrape_data_from_folder(html_folder):
    json_data = []

    # Loop through all files in the folder
    for file_name in os.listdir(html_folder):
        # Process only .html files
        if file_name.endswith(".html"):
            file_path = os.path.join(html_folder, file_name)

            try:
                # Read the HTML file
                with open(file_path, 'r', encoding='utf-8') as file:
                    html_content = file.read()

                soup = BeautifulSoup(html_content, 'html.parser')

                # Extracting the company name 
                company = soup.title.text.strip() if soup.title else "Not available"

                # Extracting industry info u"
                text = soup.get_text()  
                industry_info_match = re.search(r'information:\s*(.*?)\s*comment:', text, re.IGNORECASE | re.DOTALL)
                industry_info = industry_info_match.group(1).strip() if industry_info_match else "Not available"

                # Extracting country
                country = soup.find("i", class_="location").next.strip() if soup.find("i", class_="location") else "Not available"

                # Extracting website
                website = soup.find("i", class_="link").next.strip() if soup.find("i", class_="link") else "Not available"

                # Extracting date_added
                date_added_match = re.search(r'added:\s*([\d-]+)', text)
                date_added = date_added_match.group(1).strip() if date_added_match else "Not available"

                # Extracting data_size  
                before_added = text.split("added")[0]  # Take the part before "added"
                data_size_match = re.search(r'amount of data:\s*(\d+\s+[a-z]{2})', before_added, re.IGNORECASE)
                data_size = data_size_match.group(1).strip() if data_size_match else "Not available"

                # Extracting description using "comment:"
                data_description_match = re.search(r'comment:\s*(.*?)\s*and etc', text, re.IGNORECASE | re.DOTALL)

                #data_description = data_description_match.group(1).strip() if data_description_match else "Not available"
                data_description = [type.strip() for type in data_description_match.group(1).split(',')] if data_description_match else "Not available"

                # Extracting download_links
                download_links_match = re.search(r'DOWNLOAD LINKS:\s*(.*?)\s*Rar password:', text, re.DOTALL)
                download_links = [link.strip() for link in download_links_match.group(1).split('<br>')] if download_links_match else "Not available"

                # Extracting password
                password_match = re.search(r'Rar password:\s*(.*?)\s*PUBLISHED', text, re.DOTALL)
                password = password_match.group(1).strip() if password_match else "Not available"

                # Create a dictionary for entry
                entry = {
                    "company": company,
                    "industry information": industry_info,
                    "industry":None,
                    "country": country,
                    "date": date_added,
                    "website": website,
                    "data size": data_size,
                    "data_description": data_description,
                    "download links": download_links,
                    "password": password
                }

                json_data.append(entry)
                print(f"Processed {file_name}")

            except Exception as e:
                print(f"Failed to process {file_path}: {e}")

    return json_data

def save_to_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)

if __name__ == "__main__":
    html_folder = 'scraped_posts'  
    json_data = scrape_data_from_folder(html_folder)
    save_to_json(json_data, 'output_data.json')
    print("Processing and JSON generation completed!")
