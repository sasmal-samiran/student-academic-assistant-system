from sentence_transformers import SentenceTransformer
import faiss, numpy as np
import os, pickle, json

from config import SENTENCE_TRANSFORMER_MODEL, DATASETS_DIR, VECTOR_DB_DIR

model = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)

with open(os.path.join(DATASETS_DIR, "unstructured.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

texts = [d["text"] for d in data]
embeddings = model.encode(texts)

faiss.normalize_L2(embeddings)

index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(np.array(embeddings))

faiss.write_index(index, os.path.join(VECTOR_DB_DIR, "faiss_index.index"))

# Save chunks separately
with open(os.path.join(VECTOR_DB_DIR, "meta.pkl"), "wb") as f:
    pickle.dump(data, f)