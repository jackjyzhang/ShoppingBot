## Importing Necessary Modules
import requests # to get image from the web
import shutil # to save it locally
import os

def download_img(image_url):
    filename = "downloaded_img.jpg"
    # Open the url image, set stream to True, this will return the stream content.
    r = requests.get(image_url, stream = True, headers={'User-Agent': 'Mozilla/5.0'})
    # Check if the image was retrieved successfully
    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True

        # Open a local file with wb ( write binary ) permission.
        with open(filename,'wb') as f:
            shutil.copyfileobj(r.raw, f)

        #print('Image sucessfully Downloaded: ',filename)
        return filename
    else:
        print('Image Couldn\'t be retreived')

def delete_file(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)
    else:
        print("{} does not exist".format(file_name))


if __name__ == "__main__":
    #image_url = "https://s7d5.scene7.com/is/image/UrbanOutfitters/56775687_011_b?$xlarge$&fit=constrain&qlt=80&wid=640"
    #image_url = "https://s7d5.scene7.com/is/image/UrbanOutfitters/52290020_093_b?$xlarge$&fit=constrain&qlt=80&wid=640"
    image_url = "https://s7d5.scene7.com/is/image/UrbanOutfitters/60751856_000_b?$xlarge$&fit=constrain&fmt=webp&qlt=80&wid=960"
    download_img(image_url)
