import os
import csv
import base64
import re
import argparse


import requests
from bs4 import BeautifulSoup
from tbselenium.tbdriver import TorBrowserDriver, WebDriverWait
from tbselenium.utils import By, EC
from selenium.webdriver.firefox.options import Options


# Takes in a dirty str and cleans it
def clean(dirty: str):
    # Find all the blocks
    clean = dirty.replace("\n", "").replace("\r", "")
    clean = re.sub(r'\s+', ' ', clean)
    return clean


class Scraper():
    def __init__(self, mirror):
        import os
        work_dir = os.path.dirname(os.path.realpath(__file__))
        # work_dir = "/home/soonann/development/y4-t1/cs445/project/shaming_scrape/lockbit"
        torbrowser_path = os.path.join(work_dir, "lib/tor-browser")
        geckodriver_path = os.path.join(work_dir, "lib/geckodriver")
        self.output_path = os.path.join(work_dir, "outputs")
        self.mirror = mirror

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
        # input("Press enter to proceed")
        # self.xvfb_display = stop_xvfb()
        self.driver.quit()

    # Scrapes the main listing page
    def scrape_victim_listing(self, victim_listing_url, start=0, records=50):

        # Check if there was already a scraped copy
        if not os.path.exists(f'{self.output_path}/lockbit3.csv'):
            self.driver.load_url(victim_listing_url)

            # Wait for the page to show up
            WebDriverWait(self.driver, 360).until(
                EC.visibility_of_element_located(
                    (By.CLASS_NAME, 'post-big-list',))
            )
            # Wait for the loader to dissapear
            WebDriverWait(self.driver, 360).until(
                EC.invisibility_of_element_located(
                    (By.CLASS_NAME, 'preloader_global',))
            )

            # Get the posts
            listing = self.driver.find_element(By.CLASS_NAME, "post-big-list")
            Scraper.parse_victim_listing_page(
                listing.get_attribute("outerHTML"),
                f'{self.output_path}/lockbit3.csv'
            )

        # Read the scrape copy and run each scrap
        with open(f'{self.output_path}/lockbit3.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)

            # For each link, scrape it
            for row in reader:
                if not (int(row['no']) >= start and int(row['no']) < start + records):
                    continue
                link = f'{self.mirror}{row["link"]}'
                print(f'===== scraping {link} ...')
                self.scrape_victim_page(link, row['no'])

    def scrape_victim_page(self, victim_url, id):
        self.driver.get(victim_url)

        # Make a resource directory for the victim
        victim_resources_dir = os.path.join(self.output_path, str(id))
        try:
            os.mkdir(path=victim_resources_dir)
            print(f'made directory {victim_resources_dir}')
        except FileExistsError:
            print(f'skipping {id} as dir exists')
            return

        # Wait for the page to show up
        WebDriverWait(self.driver, 360).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'post-wrapper',))
        )
        # Wait for the loader to dissapear
        print('waiting preloader_global')
        WebDriverWait(self.driver, 360).until(
            EC.invisibility_of_element_located(
                (By.CLASS_NAME, 'preloader_global'))
        )
        print('done preloader_global')

        # handle -> possible not found error
        # span.folder-name with text unpack

        # Wait for either ts-container or reserve-links
        # TODO: handle exception
        print('waiting for ts-container or reserve-links')
        container = WebDriverWait(self.driver, 10).until(
            EC.any_of(
                EC.visibility_of_element_located(
                    (By.CLASS_NAME, 'ts-container')),
                EC.visibility_of_element_located(
                    (By.CLASS_NAME, 'reserve-links'))
            )
        )
        print('found for ts-container or reserve-links')

        # Case 1: images
        # /post/oeOilJIVrKr8BNXj66f42b53e3087
        # if its the .ts-container, download the images
        if container.get_attribute('class') == 'ts-container':
            print('found ts-container')
            Scraper.parse_victim_page_images(
                container.get_attribute('outerHTML'),
                victim_resources_dir
            )

        # Case 2: archived links
        # /post/YLbuWZrY2l6jigbo66b9ea69cf824
        # div.reserve-links -> container that hodls buttons
        # a.chat-open-btn -> buttons (href with full path)
        else:
            print('found reserve-links, parsing archive')
            archives = Scraper.parse_victim_archives(
                container.get_attribute('outerHTML'),
            )
            print(f'found {len(archives)}')

            # iterate through each archive and try it
            success = False
            for archive in archives:
                print(f'===== scraping {archive} ...')
                # Keep scraping the next link until we can get a result
                success = self.scrape_archive_page(
                    archive_url=archive,
                    outdir=os.path.join(victim_resources_dir)
                )
                if not success:
                    print(f"failed to scrape on from: {id}, {archive}")
                else:
                    break

            if success:
                print(f'===== successfully scraped {archive} ...')
            else:
                print(f'===== ERROR scraped {archive} ...')

    # Parses the victim listing page
    def parse_victim_listing_page(markup, outfile):
        print('parsing victim page')
        soup = BeautifulSoup(markup, 'html.parser')

        post_blocks = soup.find_all('a', class_='post-block')

        # CSV Writer
        file = open(outfile, "w")
        writer = csv.writer(file)

        # Header col
        writer.writerow(['no', 'link', 'post_title', 'post_text',
                         'updated_post_date'])

        no = 0
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
            writer.writerow(
                [no, link, post_title, post_text, updated_post_date])
            no += 1

    # Takes in the markup for victim page with images and outputs it to a file
    def parse_victim_page_images(markup, outdir):
        print('parsing victim imgs')
        soup = BeautifulSoup(markup, 'html.parser')
        imgs = soup.find_all('img', class_='ts-content')
        i = 0
        for img in imgs:
            src = img.get('src')
            if src.startswith('data:image'):
                base64_data = src.split(',')[1]
                image_data = base64.b64decode(base64_data)
                with open(os.path.join(outdir, f'{i}.png'), "wb") as f:
                    f.write(image_data)
            i += 1

    def parse_victim_archives(markup):
        # a.chat-open-btn -> buttons (href with full path)
        print('parsing victim archives')
        soup = BeautifulSoup(markup, 'html.parser')
        anchors = soup.find_all('a', class_='chat-open-btn')
        archives = []
        for a in anchors:
            archive = a.get('href')
            archives.append(archive)
        return archives

    def scrape_archive_page(self, archive_url, outdir):
        try:
            self.driver.get(archive_url)
        except:
            print('error page from get')
            return False

        # Check if the page loaded properly by finding body neterror onior error
        # Wait for the loader to dissapear
        page_load = WebDriverWait(self.driver, 360).until(
            EC.any_of(
                EC.invisibility_of_element_located(
                    (By.CLASS_NAME, 'preloader_global')),
                EC.visibility_of_element_located(
                    (By.CLASS_NAME, 'neterror onion-error'))
            )
        )

        # success
        try:
            print(page_load.get_attribute('class'))
            if page_load.get_attribute('class') == 'neterror onion-error':
                print('error page netonion')
                return False
            else:

                ft = WebDriverWait(self.driver, 360).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, "//a[contains(@href, 'file-tree.txt')]",)
                    )
                )
                ft_href = ft.get_attribute('href')
                print(f'===== downloading {ft_href}')
                Scraper.download_file(
                    ft_href,
                    os.path.join(outdir, 'filetree.txt')
                )
        except Exception as download_fail_ex:
            print(download_fail_ex)
            return False
        return True

    # The onion link of filtree
    def download_file(url, outfile):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        # Set up the proxies for Tor (SOCKS5)
        proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }

        # Send the request via Tor
        with requests.get(
            url,
            proxies=proxies,
            headers=headers,
            stream=True
        ) as r:
            with open(outfile, 'wb') as f:
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)


# # Define a worker function
# def worker(line):

#     # check if the episode already exists
#     ep_no = get_ep_num(line)
#     if os.path.isfile(f"./episodes/episode_{ep_no}.mp4"):
#         return ep_no
#     print(f"ep_no failed:{ep_no}")
#     driver = get_driver()
#     get_blob(line, ep_no, driver)
#     driver.close()
#     driver.quit()
#     return ep_no


# # Create a worker pool with a maximum of 5 workers
# with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
#     # Submit tasks to the worker pool
#     file_path = './links.txt'
#     # Read the scrape copy and run each scrape
#     with open(f'{self.output_path}/lockbit3.csv', 'r') as csvfile:
#         reader = csv.DictReader(csvfile)

#         # For each link, scrape it
#         # i = 0
#         # for row in reader:
#         #     link =
#         #     print(f'===== scraping {link} ...')
#         #     self.scrape_victim_page(link, i)
#         #     i += 1

#         futures = [executor.submit(worker, row) for row in reader]

#         # Retrieve the results as they become available
#         for future in concurrent.futures.as_completed(futures):
#             result = future.result()


def main():

    # Parse cli args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--start",
        help="record to start from",
        type=int,
        default=0
    )
    parser.add_argument(
        "--count",
        help="number of records to scrape",
        type=int,
        default=50
    )
    parser.add_argument(
        "--mirror",
        help="mirror to use when scraping/downloading",
        type=str,
        default="http://lockbit3g3ohd3katajf6zaehxz4h4cnhmz5t735zpltywhwpc6oy3id.onion"
    )
    args = parser.parse_args()

    # post_img = "http://lockbit3g3ohd3katajf6zaehxz4h4cnhmz5t735zpltywhwpc6oy3id.onion/post/oeOilJIVrKr8BNXj66f42b53e3087"
    # post_link = "http://lockbit3g3ohd3katajf6zaehxz4h4cnhmz5t735zpltywhwpc6oy3id.onion/post/L0SVBEqogQGtzkPh66b9e337dbb84"

    # Handle a single victim's data
    scr = Scraper(mirror=args.mirror)
    scr.scrape_victim_listing(args.mirror, args.start, args.count)
    # scr.scrape_victim_page(post_link, 4)


if __name__ == "__main__":
    main()
