# An interactive script that retrieves an item based on the input.

from model import Retriever

import validators
import os

if __name__ == "__main__":
    src_file = 'items.csv'
    vendor = input('If search within a vendor, enter vendor name (choices: "urban outfitter", "A&F", "H&M"); otherwise, enter "none": ')
    if vendor == "none":
        vendor = None
    print("Construsting retriever...")
    retriever = Retriever(src_file, vendor)
    print("Done")

    while True:
        top_k = int(input('Please input number of search results to show: '))
        user_input = input('Please input search query (text, or url/path to image): ')
        if os.path.exists(user_input) or validators.url(user_input):
            mode = 'img'
        else:
            mode = 'text'
        top_items = retriever.retrieve(user_input, mode, top_k)
        #print(top_items)
        print()
