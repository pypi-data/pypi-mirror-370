"""
Evaluation module for ranx-k library.

This module provides various evaluation methods for Korean RAG systems:
- Kiwi ROUGE evaluation
- Enhanced ROUGE with Kiwi tokenizer
- Similarity-based ranx evaluation
- OpenAI embeddings evaluation (optional)
- Comprehensive comparison utilities

All evaluation functions are designed to work with LangChain retriever objects
that implement the invoke() method and return Document objects with page_content attribute.

LangChain compatibility:
- LangChain is licensed under MIT License
- ranx-k follows LangChain's retriever interface standards
"""

from .kiwi_rouge import simple_kiwi_rouge_evaluation
from .enhanced_rouge import rouge_kiwi_enhanced_evaluation
from .similarity_ranx import evaluate_with_ranx_similarity
from .utils import comprehensive_evaluation_comparison

# OpenAI embeddings is optional import (requires openai package)
try:
    from .openai_similarity import evaluate_with_openai_similarity, estimate_openai_cost
    __all__ = [
        "simple_kiwi_rouge_evaluation",
        "rouge_kiwi_enhanced_evaluation", 
        "evaluate_with_ranx_similarity",
        "comprehensive_evaluation_comparison",
        "evaluate_with_openai_similarity",
        "estimate_openai_cost",
    ]
except ImportError:
    __all__ = [
        "simple_kiwi_rouge_evaluation",
        "rouge_kiwi_enhanced_evaluation", 
        "evaluate_with_ranx_similarity",
        "comprehensive_evaluation_comparison",
    ]
