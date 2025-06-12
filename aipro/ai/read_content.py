import pickle
import torch
import numpy as np
from . models import *
from sentence_transformers import SentenceTransformer, util
import logging


model = SentenceTransformer('all-MiniLM-L6-v2')

def recommend_product(user_vector, product_vectors, product_ids, top_n=12, last_clicked_product_id=None):
    """
    Recommend products based on cosine similarity between user and product vectors,
    with optional category-based weighting for last clicked product.
    """
    try:
        # Convert user_vector to tensor if it's not already
        if isinstance(user_vector, list):
            user_vector = torch.tensor(user_vector, dtype=torch.float32)
        elif isinstance(user_vector, np.ndarray):
            user_vector = torch.tensor(user_vector, dtype=torch.float32)
        
        # Ensure product_vectors is a tensor
        if not isinstance(product_vectors, torch.Tensor):
            product_vectors = torch.tensor(product_vectors, dtype=torch.float32)
        
        # Normalize vectors for cosine similarity
        user_vector_norm = torch.nn.functional.normalize(user_vector.unsqueeze(0), p=2, dim=1)
        product_vectors_norm = torch.nn.functional.normalize(product_vectors, p=2, dim=1)
        
        # Calculate cosine similarity
        similarities = torch.mm(user_vector_norm, product_vectors_norm.t()).squeeze()
        
        # Apply category-based weighting if last_clicked_product_id is provided
        if last_clicked_product_id:
            try:
                last_clicked_product = Product.objects.get(id=last_clicked_product_id)
                last_clicked_category = last_clicked_product.categorys
                if last_clicked_category:
                    # Boost similarity scores for products in the same category
                    for idx, product_id in enumerate(product_ids):
                        product = Product.objects.get(pk=product_id)
                        if product.categorys == last_clicked_category:
                            similarities[idx] += 0.2  # Boost score by 0.2 for same category
            except Product.DoesNotExist:
                logger.warning(f"Last clicked product {last_clicked_product_id} not found")
        
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
        logger.error(f"Error in recommend_product: {e}")
        return []