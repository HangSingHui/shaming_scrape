import os
import requests

# File with the extracted IDs
ids_file = 'extracted_ids.txt'
output_dir = 'scraped_pages/'  # Directory to save the scraped HTML files

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Function to scrape .onion pages using the extracted IDs with Tor SOCKS proxy
def scrape_onion_pages(ids):
    session = requests.Session()
    session.proxies = {
        'http': 'socks5h://127.0.0.1:9050',  # Make sure Tor is running on port 9050
        'https': 'socks5h://127.0.0.1:9050'
    }

    base_url = 'http://k7kg3jqxang3wh7hnmaiokchk7qoebupfgoik6rha6mjpzwupwtj25yd.onion/topic.php?id='

    for topic_id in ids:
        url = f"{base_url}{topic_id}"
        try:
            response = session.get(url)
            if response.status_code == 200:
                # Save the page content to a .html file
                output_path = os.path.join(output_dir, f"{topic_id}.html")
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)  # Save the HTML content of the page
                print(f"Successfully saved {url} to {output_path}")
            else:
                print(f"Failed to fetch {url}, status code: {response.status_code}")
        except Exception as e:
            print(f"Error fetching {url}: {e}")

# Main execution flow
if __name__ == "__main__":
    # Step 1: Read the IDs from the text file
    if not os.path.exists(ids_file):
        print(f"Error: {ids_file} does not exist.")
    else:
        with open(ids_file, 'r') as f:
            ids = [line.strip() for line in f.readlines()]
        
        # Step 2: Scrape the pages using the extracted IDs and save as HTML
        if ids:
            scrape_onion_pages(ids)
        else:
            print("No IDs found in the file.")
