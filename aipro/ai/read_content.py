import pickle
import torch
import numpy as np
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def recommend_product(user_vector, product_vectors, product_ids, top_n=12):
    """
    Recommend products based on cosine similarity between user and product vectors
    """
    try:
        # Convert user_vector to tensor if it's not already
        if isinstance(user_vector, list):
            user_vector = torch.tensor(user_vector, dtype=torch.float32)
        elif isinstance(user_vector, np.ndarray):
            user_vector = torch.tensor(user_vector, dtype=torch.float32)
        
        # Ensure product_vectors is the right type
        if not isinstance(product_vectors, torch.Tensor):
            product_vectors = torch.tensor(product_vectors, dtype=torch.float32)
        
        # Normalize vectors for cosine similarity
        user_vector_norm = torch.nn.functional.normalize(user_vector.unsqueeze(0), p=2, dim=1)
        product_vectors_norm = torch.nn.functional.normalize(product_vectors, p=2, dim=1)
        
        # Calculate cosine similarity
        similarities = torch.mm(user_vector_norm, product_vectors_norm.t()).squeeze()
        
        # Get top N recommendations
        top_indices = torch.topk(similarities, min(top_n, len(similarities))).indices
        
        # Return list of (product_id, similarity_score) tuples
        recommendations = []
        for idx in top_indices:
            product_id = product_ids[idx.item()]
            similarity_score = similarities[idx].item()
            recommendations.append((product_id, similarity_score))
        
        return recommendations
        
    except Exception as e:
        print(f"Error in recommend_product: {e}")
        return []
