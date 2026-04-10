import threading
from sentence_transformers import SentenceTransformer

_model = None
_lock = threading.Lock()

def get_embedding_model():
    global _model
    with _lock:
        if _model is None:
            # all-mpnet-base-v2 naturally outputs 768-D vectors
            _model = SentenceTransformer('all-mpnet-base-v2')
    return _model
