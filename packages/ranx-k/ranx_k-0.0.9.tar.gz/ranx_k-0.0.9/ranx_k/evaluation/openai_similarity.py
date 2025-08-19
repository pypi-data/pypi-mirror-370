"""
OpenAI Embeddings similarity calculation module

Adapter classes to use OpenAI embedding models like text-embedding-3-small 
and text-embedding-3-large within the ranx-k framework.
"""

import numpy as np
from typing import List, Dict, Any, Optional
import os

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAISimilarityCalculator:
    """Similarity calculator using OpenAI Embeddings API"""
    
    def __init__(self, 
                 model_name: str = "text-embedding-3-small",
                 api_key: Optional[str] = None,
                 batch_size: int = 100):
        """
        Initialize OpenAI embedding similarity calculator
        
        Args:
            model_name: OpenAI embedding model name
                - text-embedding-3-small (recommended, cost-effective)
                - text-embedding-3-large (high performance)
                - text-embedding-ada-002 (legacy model)
            api_key: OpenAI API key (loads from environment if None)
            batch_size: Batch size for API calls
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI library required. Install with: pip install openai"
            )
        
        self.model_name = model_name
        self.batch_size = batch_size
        
        # Setup API key
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
        else:
            # Load from environment variable
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError(
                    "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                    "or pass api_key parameter."
                )
            self.client = openai.OpenAI(api_key=api_key)
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Convert text list to embeddings
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Embedding array (shape: [len(texts), embedding_dim])
        """
        embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]
            
            try:
                response = self.client.embeddings.create(
                    model=self.model_name,
                    input=batch_texts,
                    encoding_format="float"
                )
                
                batch_embeddings = [data.embedding for data in response.data]
                embeddings.extend(batch_embeddings)
                
            except Exception as e:
                raise RuntimeError(f"OpenAI API call failed: {e}")
        
        return np.array(embeddings)
    
    def calculate_similarity_matrix(self, 
                                  ref_texts: List[str], 
                                  ret_texts: List[str]) -> np.ndarray:
        """
        Calculate cosine similarity matrix between reference and retrieved texts
        
        Args:
            ref_texts: Reference text list
            ret_texts: Retrieved text list
            
        Returns:
            Similarity matrix (shape: [len(ref_texts), len(ret_texts)])
        """
        # Generate embeddings
        ref_embeddings = self.get_embeddings(ref_texts)
        ret_embeddings = self.get_embeddings(ret_texts)
        
        # Calculate cosine similarity
        # Normalize embeddings
        ref_embeddings = ref_embeddings / np.linalg.norm(ref_embeddings, axis=1, keepdims=True)
        ret_embeddings = ret_embeddings / np.linalg.norm(ret_embeddings, axis=1, keepdims=True)
        
        # Compute similarity matrix
        similarity_matrix = np.dot(ref_embeddings, ret_embeddings.T)
        
        return similarity_matrix


def evaluate_with_openai_similarity(retriever,
                                   questions: List[str],
                                   reference_contexts: List[List[str]],
                                   k: int = 5,
                                   model_name: str = "text-embedding-3-small",
                                   similarity_threshold: float = 0.7,
                                   api_key: Optional[str] = None) -> Dict[str, float]:
    """
    Evaluate retriever using OpenAI embeddings with ranx compatibility.
    
    Args:
        retriever: Document retriever object
        questions: List of questions
        reference_contexts: List of lists of reference documents
        k: Number of top documents to evaluate
        model_name: OpenAI embedding model name
        similarity_threshold: Similarity threshold for relevance judgment
        api_key: OpenAI API key
        
    Returns:
        Dictionary containing ranx evaluation results
    """
    try:
        from ranx import Qrels, Run, evaluate as ranx_evaluate
    except ImportError:
        raise ImportError("ranx library required. Install with: pip install ranx")
    
    # Initialize OpenAI similarity calculator
    similarity_calculator = OpenAISimilarityCalculator(
        model_name=model_name,
        api_key=api_key
    )
    
    qrels_dict = {}
    run_dict = {}
    
    for i, (question, ref_contexts) in enumerate(zip(questions, reference_contexts)):
        query_id = f"q{i}"
        
        # Perform retrieval
        retrieved_docs = retriever.invoke(question)[:k]
        
        # Calculate similarity
        similarity_matrix = similarity_calculator.calculate_similarity_matrix(
            ref_contexts, retrieved_docs
        )
        
        # Generate qrels (based on reference documents)
        qrels_dict[query_id] = {}
        for ref_idx, ref_doc in enumerate(ref_contexts):
            qrels_dict[query_id][f"ref_{ref_idx}"] = 1
        
        # Generate run (similarity-based relevance judgment)
        run_dict[query_id] = {}
        for ret_idx, ret_doc in enumerate(retrieved_docs):
            # Maximum similarity for each retrieved document
            max_similarity = np.max(similarity_matrix[:, ret_idx])
            
            if max_similarity >= similarity_threshold:
                # Find and map the most similar reference document
                best_ref_idx = np.argmax(similarity_matrix[:, ret_idx])
                run_dict[query_id][f"ref_{best_ref_idx}"] = float(max_similarity)
    
    # Perform ranx evaluation
    qrels = Qrels(qrels_dict)
    run = Run(run_dict)
    
    results = ranx_evaluate(qrels, run, [f"hit_rate@{k}", f"ndcg@{k}", f"map@{k}", "mrr"])
    
    return results


# Cost estimation function
def estimate_openai_cost(num_texts: int, 
                        avg_tokens_per_text: int = 100,
                        model_name: str = "text-embedding-3-small") -> Dict[str, Any]:
    """
    OpenAI Embeddings API Cost estimation
    
    Args:
        num_texts: Number of texts to process
        avg_tokens_per_text: Average tokens per text
        model_name: OpenAI model name
        
    Returns:
        Cost information dictionary
    """
    # 2024 pricing (USD per 1M tokens)
    pricing = {
        "text-embedding-3-small": 0.02,
        "text-embedding-3-large": 0.13,
        "text-embedding-ada-002": 0.10
    }
    
    if model_name not in pricing:
        return {"error": f"Unknown model: {model_name}"}
    
    total_tokens = num_texts * avg_tokens_per_text
    cost_per_million = pricing[model_name]
    estimated_cost = (total_tokens / 1_000_000) * cost_per_million
    
    return {
        "model": model_name,
        "total_texts": num_texts,
        "total_tokens": total_tokens,
        "cost_per_1M_tokens": cost_per_million,
        "estimated_cost_usd": round(estimated_cost, 4),
        "estimated_cost_krw": round(estimated_cost * 1300, 0)  # Approximate exchange rate
    }