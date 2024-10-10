import csv
import re
from bs4 import BeautifulSoup


# Takes in a dirty str and cleans it
def clean(dirty: str):
    # Find all the blocks
    clean = dirty.replace("\n", "").replace("\r", "")
    clean = re.sub(r'\s+', ' ', clean)
    return clean


def parse_post_block(markup, outfile):
    soup = BeautifulSoup(markup, 'html.parser')

    post_blocks = soup.find_all('a', class_='post-block')

    # CSV Writer
    file = open(outfile, "w")
    writer = csv.writer(file)
    writer.writerow(["link", "post_title", "post_text", "post_date_utc"])

    for post in post_blocks:

        # Extract the href attribute
        link = post.get('href')

        # Find all the blocks
        post_title = post.find(
            'div',
            class_='post-title'
        ).get_text(strip=True)
        post_title = clean(post_title)

        post_text = post.find(
            'div',
            class_='post-block-text'
        ).get_text(strip=True)
        post_text = clean(post_text)

        updated_post_date = post.find(
            'div',
            class_='updated-post-date'
        ).get_text(strip=True)
        updated_post_date = clean(updated_post_date)

        # Write to csv
        writer.writerow([link, post_title, post_text, updated_post_date])


def main():
    markup = open("./lockbit3.html", "r")
    parse_post_block(markup, "lockbit3.csv")


if __name__ == '__main__':
    main()
