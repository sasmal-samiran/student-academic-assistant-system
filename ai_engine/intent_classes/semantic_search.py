import os, faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

from services import groq_api
from config import SENTENCE_TRANSFORMER_MODEL, VECTOR_DB_DIR
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Load everything
try:
    model = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
    index = faiss.read_index(os.path.join(VECTOR_DB_DIR, "faiss_index.index"))

    with open(os.path.join(VECTOR_DB_DIR, "meta.pkl"), "rb") as f:
        documents = pickle.load(f)
except Exception as e:
    logger.error(str(e))

def _search(query, k=10, threshold=0.75):
    try:
        query_vec = model.encode([query])
        query_vec = np.array(query_vec)

        faiss.normalize_L2(query_vec)
        D, I = index.search(query_vec, k)

        results = []
        for score, idx in zip(D[0], I[0]):
            if score <= threshold:
                results.append(documents[idx])
        
        return results
    except Exception as e:
        logger.error(str(e))

def semantic_search(user_query):
    # Combine retrieved chunks
    results = _search(user_query)
    context = "\n".join([r["text"] for r in results])

    prompt = f"""
        You are ASPAS (Academic Assistant).

        Answer the user's question using ONLY the context below.
        If context is not present, say "Information not available".
         
        OUTPUT FORMAT:
            - Return ONLY valid HTML inside <section>...</section>
            - answer sentences should be in proper format, do not merge words.

        CONTEXT:
        {context}

        QUESTION:
        {user_query}

        ANSWER (concise and clear):
        """

    return groq_api.call_groq(prompt)