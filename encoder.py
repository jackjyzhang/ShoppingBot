# Encode the text and image of each item and store the encodings for retrieval
# Use SBERT embeddings for text, and Resnet18 representations for image

from sentence_transformers import SentenceTransformer, util
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from torch.autograd import Variable
from PIL import Image

from download_img import download_img, delete_file

sbert_model_name = 'bert-base-nli-stsb-mean-tokens'
sbert_model = SentenceTransformer(sbert_model_name)

def encode_text(text):
    embedding = sbert_model.encode([text], show_progress_bar=False, convert_to_numpy=True)
    return embedding[0]  # embedding size: 768


# TODO: fine-tune the resnet model
img_model = models.resnet18(pretrained=True)
layer = img_model._modules.get('avgpool')  # output size 512
img_model.eval()
scaler = transforms.Resize((224, 224))
normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
to_tensor = transforms.ToTensor()

def encode_img(image_url):
    image_name = download_img(image_url)
    embedding = encode_local_img(image_name)
    delete_file(image_name)
    return embedding

def encode_local_img(image_name):
    img = Image.open(image_name)  # Load the image with Pillow library
    t_img = Variable(normalize(to_tensor(scaler(img))).unsqueeze(0))
    out = img_model(t_img)

    embedding = torch.zeros(512)

    def copy_data(m, i, o):
        embedding.copy_(o.data.squeeze())  # shape [1,512,1,1] -> [512]

    h = layer.register_forward_hook(copy_data)
    img_model(t_img)
    h.remove()
    return embedding.numpy()


if __name__ == "__main__":
    print(encode_text("Hello").shape)

    image_url = "https://s7d5.scene7.com/is/image/UrbanOutfitters/60751856_000_b?$xlarge$&fit=constrain&fmt=webp&qlt=80&wid=960"
    print(encode_img(image_url).shape)
