# Cleaning will need to take the same amount of time as crawling. So technically, we could 
# just crawl a new dataset when items get outdated.

import csv
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import urllib
import os
import time

def get_soup(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(req).read()
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def parse_item(url):
    print(url)
    time.sleep(8)
    soup = get_soup(url)
    img = soup.find("div", class_="c-pwa-image-viewer__img-outer")
    img_url = img.find("picture").find("img").get("src")

def main():
    column_names = ['descrption', 'img_url', 'url', 'brand', 'price', 'color', 'text_repr', 'img_repr']

    inp = open('items.csv', 'r')
    otp = open('clean_items.csv', 'w')
    reader = csv.reader(inp)
    next(reader)
    writer = csv.writer(otp)
    writer.writerow(column_names)
    for row in reader:
        url = row[3]
        try:
            parse_item(url)
            writer.writerow(row)
        except:
            print(f'skipping item {url}')
            continue


if __name__ == "__main__":
    main()
