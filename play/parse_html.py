import os
import re
from bs4 import BeautifulSoup
from datetime import datetime

# Directory containing your saved HTML files
html_dir = './outputs'  # Change this to the directory where your HTML files are located
output_file = 'extracted_ids.txt'  # File to save the extracted IDs

# Date range to filter the 'added' field
start_date = datetime.strptime('2024-01-01', '%Y-%m-%d')
end_date = datetime.strptime('2024-08-31', '%Y-%m-%d')

# Function to extract IDs from local HTML files
def extract_ids_from_html_files(directory):
    extracted_ids = []

    # Iterate over each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')

                # Find all <th> tags with the onclick attribute matching "viewtopic('ID')"
                th_elements = soup.find_all('th', attrs={"onclick": re.compile(r"viewtopic\('([a-zA-Z0-9]+)'\)")})

                for th in th_elements:
                    # Extract the ID from the onclick attribute
                    match = re.search(r"viewtopic\('([a-zA-Z0-9]+)'\)", th['onclick'])
                    if match:
                        topic_id = match.group(1)

                        # Now find the corresponding 'added' date inside the same <th> tag
                        added_match = re.search(r"added:\s*(\d{4}-\d{2}-\d{2})", th.text)
                        if added_match:
                            added_date_str = added_match.group(1)
                            added_date = datetime.strptime(added_date_str, '%Y-%m-%d')

                            # Check if the added date falls within the desired range
                            if start_date <= added_date <= end_date:
                                #print(added_date)
                                #print(filename)
                                extracted_ids.append(topic_id)

    return extracted_ids

# Main execution flow
if __name__ == "__main__":
    # Step 1: Extract IDs from local HTML files
    ids = extract_ids_from_html_files(html_dir)
    
    # Step 2: Write the extracted IDs to a text file
    if ids:
        with open(output_file, 'w') as f:
            for topic_id in ids:
                f.write(f"{topic_id}\n")
        print(f"Extracted {len(ids)} IDs. Saved to {output_file}.")
    else:
        print("No IDs found within the date range.")
