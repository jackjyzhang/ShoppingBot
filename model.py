import encoder

from sentence_transformers import util
import faiss
import os
import numpy as np
import pandas as pd

def recover_array(emb_str):
    '''Reconstructs the embedding array from csv entry string.'''
    arr = emb_str.strip('[]').split()
    arr = [float(x) for x in arr]
    return arr

class Retriever():
    def __init__(self, src_file='items.csv', vendor=None):
        emb_size_text = 768
        emb_size_img = 512
        self.df = pd.read_csv(src_file, index_col=0)
        if vendor is not None:
            self.df = self.df[self.df['brand'] == vendor]
        text_embs = self.df['text_repr'].tolist()
        img_embs = self.df['img_repr'].tolist()
        self.text_embs = np.float32([recover_array(emb_str) for emb_str in text_embs])
        self.img_embs = np.float32([recover_array(emb_str) for emb_str in img_embs])

        self.text_index = self.__create_faiss_index(self.text_embs, emb_size_text)
        self.img_index = self.__create_faiss_index(self.img_embs, emb_size_img)

    def __create_faiss_index(self, embeddings, embed_size, n_clusters=16):
        #We use Inner Product (dot-product) as Index. We will normalize our vectors to unit length, then is Inner Product equal to cosine similarity
        quantizer = faiss.IndexFlatIP(embed_size)
        index = faiss.IndexIVFFlat(quantizer, embed_size, n_clusters, faiss.METRIC_INNER_PRODUCT)
        #Number of clusters to explorer at search time. We will search for nearest neighbors in 3 clusters.
        index.nprobe = 3

        ### Create the FAISS index
        print("Start creating FAISS index")
        # First, we need to normalize vectors to unit length
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1)[:, None]
        # Then we train the index to find a suitable clustering
        index.train(embeddings)
        # Finally we add all embeddings to the index
        index.add(embeddings)

        print("Data loaded with {} embeddings".format(len(embeddings)))
        return index

    def search(self, embds, index, q_embedding, top_k_hits=5):
        '''
        index: the faiss index used for the search
        q_embedding: embedding of the query
        top_k_hits: number of hits to output
        '''
        #FAISS works with inner product (dot product). When we normalize vectors to unit length, inner product is equal to cosine similarity
        q_embedding = q_embedding / np.linalg.norm(q_embedding)
        q_embedding = np.expand_dims(q_embedding, axis=0)
        # Search in FAISS. It returns a matrix with distances and corpus ids.
        distances, corpus_ids = index.search(q_embedding, top_k_hits)

        hits = [{'corpus_id': id, 'score': score} for id, score in zip(corpus_ids[0], distances[0])]
        hits = sorted(hits, key=lambda x: x['score'], reverse=True)

        top_urls = []
        rank = 1
        for hit in hits[0:top_k_hits]:
            id_num = self.df.index[hit['corpus_id']]
            print("{}\t{:.3f}\t{}".format(rank, hit['score'], id_num))
            item = self.df.iloc[hit['corpus_id']]
            print(f"{item['descrption']}\t{item['brand']}\t{item['price']}\n{item['url']}")
            top_urls.append(item['url'])
            rank += 1
            print()

        correct_hits = util.semantic_search(q_embedding, embds, top_k=top_k_hits)[0]
        correct_hits_ids = set([hit['corpus_id'] for hit in correct_hits])
        ann_corpus_ids = set([hit['corpus_id'] for hit in hits])
        if len(ann_corpus_ids) != len(correct_hits_ids):
            print("Approximate Nearest Neighbor returned a different number of results than expected")

        recall = len(ann_corpus_ids.intersection(correct_hits_ids)) / len(correct_hits_ids)
        print("\nApproximate Nearest Neighbor Recall@{}: {:.2f}".format(top_k_hits, recall * 100))

        return top_urls


    def retrieve(self, input, mode, top_k):
        ''' Retrieve items and return their urls using a vector model.
        '''
        if mode == 'img':
            if os.path.exists(input):
                emb = encoder.encode_local_img(input)
            else:
                emb = encoder.encode_img(input)
            top_items = self.search(self.img_embs, self.img_index, emb, top_k)
        else: 
            emb = encoder.encode_text(input)
            top_items = self.search(self.text_embs, self.text_index, emb, top_k)

        return top_items

