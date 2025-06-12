import pandas as pd
# import pickle
from sentence_transformers import SentenceTransformer

# Initialize Sentence-BERT model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to process and vectorize reviews for a course
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

# Initialize Sentence-BERT model
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Error loading SentenceTransformer model: {e}")
    model = None

def process_reviews(reviews):
    """Vectorize each review and return the average vector."""
    if not model:
        return None
        
    if reviews and reviews.strip():  # Check for non-empty reviews
        try:
            review_list = [review.strip() for review in reviews.split(',') if review.strip()]
            if review_list:
                review_vectors = model.encode(review_list)
                review_vector = review_vectors.mean(axis=0)
                return review_vector.tolist()  # Convert to list for JSON serialization
        except Exception as e:
            print(f"Error processing reviews: {e}")
    return None

def process_search(search):
    """Process search terms and return average vector."""
    if not model:
        return None
        
    if search and search.strip():
        try:
            search_list = [term.strip() for term in search.split(',') if term.strip()]
            if search_list:
                search_vectors = model.encode(search_list)
                search_vector = search_vectors.mean(axis=0)
                return search_vector.tolist()  # Convert to list for JSON serialization
        except Exception as e:
            print(f"Error processing search terms: {e}")
    return None

def combine_product_with_reviews(product_data):
    """Combine product metadata and reviews to create a vector."""
    if not model:
        return None
        
    try:
        # Create combined text with better formatting
        combined_text = (
            f"Product Name: {product_data.get('title', '')}, "
            f"Rating: {product_data.get('rating', '')}, "
            f"Category: {product_data.get('categorys', '')}, "
            f"Description: {product_data.get('description', '')}"
        )
        
        product_vector = model.encode(combined_text)
        review_vector = process_reviews(product_data.get('reviews', ''))
        
        if review_vector is not None:
            # Ensure both vectors have the same dimension
            review_vector = np.array(review_vector)
            if len(product_vector) == len(review_vector):
                combined_vector = product_vector + review_vector
            else:
                print("Vector dimension mismatch, using only product vector")
                combined_vector = product_vector
        else:
            combined_vector = product_vector
        
        return combined_vector.tolist()  # Convert to list for JSON serialization
        
    except Exception as e:
        print(f"Error combining product with reviews: {e}")
        return None

def vectorize_product_with_reviews(df):
    """Vectorize all products in the dataframe."""
    product_vectors = []
    for _, product in df.iterrows():
        product_vector = combine_product_with_reviews(product)
        if product_vector is not None:
            product_vectors.append(product_vector)
        else:
            print(f"Failed to vectorize product: {product.get('title', 'Unknown')}")
    return product_vectors

def combine_user_with_search(user_data):
    """Combine user data with search history to create a vector."""
    if not model:
        return None
        
    try:
        combined_text = (
            f"User ID: {user_data.get('user_id', '')}, "
            f"Product: {user_data.get('product', '')}"
        )
        
        user_vector = model.encode(combined_text)
        search_vector = process_search(user_data.get('search', ''))
        
        if search_vector is not None:
            search_vector = np.array(search_vector)
            if len(user_vector) == len(search_vector):
                combined_vector = user_vector + search_vector
            else:
                print("Vector dimension mismatch, using only user vector")
                combined_vector = user_vector
        else:
            combined_vector = user_vector
            
        return combined_vector.tolist()  # Convert to list for JSON serialization
        
    except Exception as e:
        print(f"Error combining user with search: {e}")
        return None

def vectorize_user_with_search(df):
    """Vectorize all users in the dataframe."""
    user_vectors = []
    for _, user in df.iterrows():
        user_vector = combine_user_with_search(user)
        if user_vector is not None:
            user_vectors.append(user_vector)
        else:
            print(f"Failed to vectorize user: {user.get('user_id', 'Unknown')}")
    return user_vectors
