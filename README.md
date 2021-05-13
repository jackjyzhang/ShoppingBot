# FashionShoppingBot

This project is a fashion shopping bot that helps you retrieve clothes you want across different clothing websites.

To run this project, first create a virtual environment with python==3.7, and run `pip install -r requirements.txt`.
(Notably, you would need faiss-cpu, sentence-transformer, and torchvision packages.)

To start the interactive retrieval shell, run
`python retrieve.py` \
and you will be prompted to enter a search text or an image for search.

We also made an attempt to develop an application interface for this project, using PostgreSQL instead of CSV for data storage. The flask app is hosted at https://github.com/ChenyuHeidiZhang/FashionShoppingApp, although deployment has been a difficult issue.
