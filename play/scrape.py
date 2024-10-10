import requests
from bs4 import BeautifulSoup
import csv
import os

# TODO: this is not complete yet


def parse_post_block(markup, outfile):
    soup = BeautifulSoup(markup, 'html.parser')

    cells = soup.find_all('th', class_='News')

    # CSV Writer
    file = open(outfile, "w")
    writer = csv.writer(file)
    writer.writerow(["link", "post_title", "post_text", "post_date_utc"])

    for cell in cells:

        # Extract the href attribute
        link = cell.get('href')

        # Find all the blocks
        post_title = cell.find(
            'div',
            class_='post-title'
        ).get_text(strip=True)
        post_title = clean(post_title)

        post_text = cell.find(
            'div',
            class_='post-block-text'
        ).get_text(strip=True)
        post_text = clean(post_text)

        updated_post_date = cell.find(
            'div',
            class_='updated-post-date'
        ).get_text(strip=True)
        updated_post_date = clean(updated_post_date)

        # Write to csv
        writer.writerow([link, post_title, post_text, updated_post_date])


site = "http://k7kg3jqxang3wh7hnmaiokchk7qoebupfgoik6rha6mjpzwupwtj25yd.onion"
# 1 to 41
php_site = "http://k7kg3jqxang3wh7hnmaiokchk7qoebupfgoik6rha6mjpzwupwtj25yd.onion/index.php"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
}

proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050',
}

output_dir = 'outputs'

# Iterate all pages
for i in range(1, 42):
    filename = f'{output_dir}/play_{i}.html'
    url = f'{php_site}?page={i}'
    markup = ""

    if os.path.isfile(filename):
        markup = open(filename, "r").readall()
    else:
        response = requests.get(
            url,
            proxies=proxies,
            headers=headers
        )
        markup = response.text

        # Save the html file
        with open(filename, 'w') as f:
            f.write(markup)
            print(f'writing page {i}')
