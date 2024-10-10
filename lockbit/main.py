import os
import csv

from utils import clean

from bs4 import BeautifulSoup
from tbselenium.tbdriver import TorBrowserDriver, WebDriverWait
from tbselenium.utils import By, EC
from selenium.webdriver.firefox.options import Options


class Scraper():
    def __init__(self):
        work_dir = "/home/soonann/development/y4-t1/cs445/project/selenium-scraper"
        torbrowser_path = os.path.join(work_dir, "tor-browser")
        geckodriver_path = os.path.join(work_dir, "geckodriver")
        self.output_path = os.path.join(work_dir, "outputs")

        user_agent = "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0"
        options = Options()

        # Disable JavaScript
        # options.set_preference("javascript.enabled", False)

        # Disable Images
        # options.set_preference("permissions.default.image", 2)

        # Disable web fonts
        options.set_preference("browser.display.use_document_fonts", 0)

        # Block stylesheets
        # options.set_preference("permissions.default.stylesheet",
        # 2)

        # Set the user agent to a normal Firefox user agent string
        options.set_preference("general.useragent.override", user_agent)

        # self.xvfb_display = start_xvfb()
        self.driver = TorBrowserDriver(
            torbrowser_path,
            executable_path=geckodriver_path,
            options=options,
        )

    def __del__(self):
        input("Press enter to proceed")
        # self.xvfb_display = stop_xvfb()
        self.driver.quit()

    def handle_victim_listing(self, victim_listing_url):

        self.driver.load_url(victim_listing_url)

        # Wait for the page to show up
        WebDriverWait(self.driver, 360).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'post-big-list',))
        )
        # Wait for the loader to dissapear
        WebDriverWait(self.driver, 360).until(
            EC.invisibility_of_element_located(
                (By.CLASS_NAME, 'preloader_global',))
        )

        # Get the posts
        elements = self.driver.find_elements(By.CLASS_NAME, "post-block")

        victim_urls = []
        with open(f'{self.output_path}/urls.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for e in elements:
                link = e.get_attribute("href")
                victim_urls.append(link)
                writer.writerow([link])

        for url in victim_urls:
            self.handle_victim_page(url)

    def handle_victim_page(self,  victim_url):
        self.driver.get(victim_url)

        # Wait for the page to show up
        WebDriverWait(self.driver, 360).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'post-wrapper',))
        )
        # Wait for the loader to dissapear
        WebDriverWait(self.driver, 360).until(
            EC.invisibility_of_element_located(
                (By.CLASS_NAME, 'preloader_global',))
        )

        # Wait for the fields to appear
        title = WebDriverWait(self.driver, 360).until(
            EC.visibility_of_element_located(
                (By.CLASS_NAME, 'post-big-title',))
        )
        desc = self.driver.find_element(By.CLASS_NAME, "desc")
        date = self.driver.find_element(By.CLASS_NAME, "uploaded-date-utc")

        with open(f'{self.output_path}/scrape.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([title.text,  desc.text, date.text])

        print(title.text)
        print(desc.text)
        print(date.text)

    def parse_post_block(markup, outfile):
        soup = BeautifulSoup(markup, 'html.parser')

        post_blocks = soup.find_all('a', class_='post-block')

        # CSV Writer
        file = open(outfile, "w")
        writer = csv.writer(file)

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

    # listing = "http://lockbit3g3ohd3katajf6zaehxz4h4cnhmz5t735zpltywhwpc6oy3id.onion"
    post = "http://lockbit3g3ohd3katajf6zaehxz4h4cnhmz5t735zpltywhwpc6oy3id.onion/post/oeOilJIVrKr8BNXj66f42b53e3087"

    # Handle a single victim's data
    scr = Scraper()
    # scr.handle_victim_listing(listing)
    scr.handle_victim_page(post)


if __name__ == "__main__":
    main()
