from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re


model = SentenceTransformer('all-MiniLM-L6-v2')

SIMILARITY_THRESHOLD = 0.85
stored_texts = []
stored_embeddings = []


def is_similar(new_emb, stored_embs, threshold=SIMILARITY_THRESHOLD):
    return bool(stored_embs and np.max(cosine_similarity([new_emb], stored_embs)) >= threshold)



def get_unique_text(text):
    pieces = [line.strip() for line in re.split(r'\n|(?<=[.!?])\s+', text) if line.strip()]
    unique_pieces = []
    for piece in pieces:
        emb = model.encode(piece)
        if not is_similar(emb, stored_embeddings):
            unique_pieces.append(piece)
            stored_texts.append(piece)
            stored_embeddings.append(emb)
    return " ".join(unique_pieces)



