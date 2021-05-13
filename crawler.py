# Crawl information from clothing websites and store in csv file
# columns: id, title (& description), image url, original website link, brand, price, 
# text representation, image representation

import csv
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import urllib
import os
import time
import requests

import encoder


def get_soup(url):
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, 'html.parser')
    # req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    # html = urlopen(req).read()
    # soup = BeautifulSoup(html, 'html.parser')
    #print(soup.prettify())
    return soup


class Site():
    def __init__(self):
        self.link_female = ''
        self.link_male = ''

    def crawl_female(self, csv_file):
        self.crawl(self.link_female, csv_file)
    def crawl_male(self, csv_file):
        self.crawl(self.link_male, csv_file)

    def parse_item(self, url):
        raise NotImplementedError

    def crawl(self, site, csv_file):
        raise NotImplementedError

class HM(Site):
    def __init__(self):
        self.link_female = 'https://www2.hm.com/en_us/women/products/view-all.html'
        self.link_male = 'https://www2.hm.com/en_us/men/products/view-all.html'

    def parse_item(self, site, tile):
        # time.sleep(1)
        link = tile.find("article").find("div", class_="image-container").find("a")
        url = urllib.parse.urljoin(site, link.get("href"))
        print(url)
        img_url = 'http:' + link.find("img").get("src")
        item_details = tile.find("article").find("div", class_="item-details")
        desc = item_details.find("h3").find("a").text.strip()
        price = item_details.find("strong").find("span").text.strip()
        price = "".join(price.split()) # '$ 75' -> '$75'
        color = item_details.find("ul").find("li").find("a").text.strip()
        return {
            'descrption': desc,
            'img_url': img_url,
            'url': url,
            'brand': "H&M",
            'price': price,
            'color': color,
            'text_repr': encoder.encode_text(desc),
            'img_repr': encoder.encode_img(img_url)
        }

    def crawl(self, site, csv_file):
        id = 6871
        # 1751 - 6871 : H&M female, 6872 - X: H&M male
        with open(csv_file, 'a') as f:
            wr = csv.writer(f)
            soup = get_soup(site)
            #num_pages = int(soup.find("div", class_="pagination__list flex flex-align-center flex-justify-center").find_all("button")[-2].text.strip())
            num_items = int(soup.find("div", class_="filter-pagination").text.strip().split()[0])
            print("Number of items in total:", num_items)
            
            i = 0
            PAGE_SIZE = 4

            while (i+1)*PAGE_SIZE-1 < num_items:
                print(f"Currently on items {i*PAGE_SIZE} to {(i+1)*PAGE_SIZE-1}")
                page_i = site + f"?offset={i*PAGE_SIZE}&page-size={PAGE_SIZE}"
                print(f"Page link: {page_i}")
                soup = get_soup(page_i)
                for tile in soup.find_all("li", class_="product-item"):
                    href = urllib.parse.urljoin(site, tile.get("href"))
                    try:
                        row = self.parse_item(site, tile)
                        id += 1
                        row['id'] = id
                        wr.writerow([row[col] for col in column_names])
                    except urllib.error.HTTPError:
                        print("HTTP Error")
                    except KeyboardInterrupt:
                        return
                    except Exception as e:
                        print(f"Some other error {e}")
                i += 1

class AF(Site):
    def __init__(self):
        self.link_female = 'https://www.abercrombie.com/shop/us/womens-new-arrivals'
        self.link_male = 'https://www.abercrombie.com/shop/us/mens-new-arrivals'

    def parse_item(self, site, tile):
        #time.sleep(8)
        link = tile.find("a", class_="product-card__image-link")
        url = urllib.parse.urljoin(site, link.get("href"))
        print(url)
        img_url = link.find("noscript").find("img").get("src")
        desc = tile.find("a", class_="product-card__name").text.strip()
        price = tile.find("span", class_="product-price-text ds-override").text.strip()
        color = "N/A"
        return {
            'descrption': desc,
            'img_url': img_url,
            'url': url,
            'brand': "A&F",
            'price': price,
            'color': color,
            'text_repr': encoder.encode_text(desc),
            'img_repr': encoder.encode_img(img_url)
        }

    def crawl(self, site, csv_file):
        id = 1501
        # 1060-1501: AF female; 1502-1750
        with open(csv_file, 'a') as f:
            wr = csv.writer(f)
            soup = get_soup(site)
            #num_pages = int(soup.find("div", class_="pagination__list flex flex-align-center flex-justify-center").find_all("button")[-2].text.strip())
            num_pages = 2
            print("Number of pages in total:", num_pages)

            for page in range(num_pages):
                print("Currently on page", page+1)
                page_i = site + f"?start={page*240}&start={page*240}"
                soup = get_soup(page_i)
                for tile in soup.find_all("div", class_="product-template ds-override"):
                    #href = urllib.parse.urljoin(site, tile.get("href"))
                    try:
                        row = self.parse_item(site, tile)
                        id += 1
                        row['id'] = id
                        wr.writerow([row[col] for col in column_names])
                    except urllib.error.HTTPError:
                        print("HTTP Error")
                    except KeyboardInterrupt:
                        return
                    except:
                        print("Some other error")


class UO(Site):
    def __init__(self):
        link = "https://www.urbanoutfitters.com/"
        self.link_female = link + "womens-clothing"
        self.link_male = link + "mens-clothing"

    def parse_item(self, url):
        print(url)
        time.sleep(8)
        soup = get_soup(url)
        img = soup.find("div", class_="c-pwa-image-viewer__img-outer")
        img_url = img.find("picture").find("img").get("src")
        desc = soup.find("h1", class_="c-pwa-product-meta-heading").text.strip()
        price = soup.find("p", class_="c-pwa-product-price").find("span").text.strip()
        color = soup.find("span", class_="c-pwa-sku-selection__color-value").text.strip()
        return {
            'descrption': desc,
            'img_url': img_url,
            'url': url,
            'brand': "urban outfitter",
            'price': price,
            'color': color,
            'text_repr': encoder.encode_text(desc),
            'img_repr': encoder.encode_img(img_url)
        }

    def crawl(self, site, csv_file):
        id = 1059  # 691 is the last female item
        with open(csv_file, 'a') as f:
            wr = csv.writer(f)

            soup = get_soup(site)
            num_pages = int(soup.find("ul", class_="o-pwa-pagination").find_all("li")[1] \
                .find("a").get("aria-label").split()[-1])
            print("Number of pages in total:", num_pages)

            for page in range(10, num_pages+1):
                print("Currently on page", page)
                page_i = site + "?page={}".format(str(page))
                soup = get_soup(page_i)
                #for tile in soup.find_all("div", class_="c-pwa-product-tile"):
                for tile in soup.find_all("div", class_="o-pwa-product-tile"):
                    link = tile.find("a", recursive=False)
                    href = urllib.parse.urljoin(site, link.get("href"))
                    try:
                        row = self.parse_item(href)
                        id += 1
                        row['id'] = id
                        wr.writerow([row[col] for col in column_names])
                    except urllib.error.HTTPError:
                        print("HTTP Error")
                    except KeyboardInterrupt:
                        return
                    except:
                        print("Some other error")


def initialize_csv(csv_file, column_names):
    if not os.path.exists(csv_file):
        with open(csv_file, 'w') as f:
            wr = csv.writer(f)
            wr.writerow(column_names)


if __name__ == "__main__":
    csv_file = "items_hm.csv"
    column_names = ['id', 'descrption', 'img_url', 'url', 'brand', 'price', 'color', 'text_repr', 'img_repr']
    initialize_csv(csv_file, column_names)

    # site = UO()
    # site = Shein()
    # site = Gap()
    # site = Forever21()
    site = HM()
    site.crawl_male(csv_file)

    df = pd.read_csv(csv_file, index_col=0)
    print(df.head())
    print(df.tail())

