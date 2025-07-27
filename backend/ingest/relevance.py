import os
os.environ["USE_TF"] = "0"  # ✅ Prevents TensorFlow from being loaded


from sentence_transformers import SentenceTransformer, util

# Load model once and reuse
_model = SentenceTransformer("all-MiniLM-L6-v2")

def is_semantically_similar(title: str, query: str, threshold: float = 0.1) -> bool:
    """
    Compare eBay title with search query using sentence-transformer embeddings.

    Args:
        title (str): The eBay listing title.
        query (str): The search term used.
        threshold (float): Cosine similarity threshold [0.0 - 1.0].

    Returns:
        bool: True if title is semantically similar to query.
    """
    embeddings = _model.encode([query, title], convert_to_tensor=True)
    similarity = util.cos_sim(embeddings[0], embeddings[1])
    return similarity.item() >= threshold