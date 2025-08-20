#!/usr/bin/env python3
"""
Practical example: Comparing retrieval methods with ranx-k evaluation.

This example shows how to use ranx-k to evaluate and compare different
retrieval approaches in a real RAG system.
"""

import pandas as pd
from typing import List, Dict, Any
from ranx_k.evaluation.utils import comprehensive_evaluation_comparison
from ranx_k.evaluation.kiwi_rouge import simple_kiwi_rouge_evaluation
from ranx_k.evaluation.similarity_ranx import evaluate_with_ranx_similarity


def create_hybrid_retriever(vector_store, bm25_retriever, weights: List[float]):
    """
    Create hybrid retriever combining semantic and keyword search.
    
    Args:
        vector_store: Vector store (e.g., Chroma, Pinecone, FAISS)
        bm25_retriever: BM25 retriever (e.g., from langchain)
        weights: [semantic_weight, keyword_weight] - should sum to 1.0
        
    Returns:
        Hybrid retriever object
    """
    class HybridRetriever:
        def __init__(self, vector_retriever, bm25_retriever, weights):
            self.vector_retriever = vector_retriever
            self.bm25_retriever = bm25_retriever
            self.semantic_weight = weights[0]
            self.keyword_weight = weights[1]
            
        def invoke(self, query: str, k: int = 5):
            """Invoke hybrid retrieval with score fusion."""
            # Get semantic results
            semantic_docs = self.vector_retriever.invoke(query)[:k*2]  # Get more for fusion
            keyword_docs = self.bm25_retriever.invoke(query)[:k*2]
            
            # Score-based fusion
            doc_scores = {}
            
            # Add semantic scores
            for i, doc in enumerate(semantic_docs):
                content_key = doc.page_content[:100]  # Use first 100 chars as key
                semantic_score = (len(semantic_docs) - i) / len(semantic_docs)  # Rank-based score
                doc_scores[content_key] = {
                    'doc': doc,
                    'score': semantic_score * self.semantic_weight,
                    'methods': ['semantic']
                }
            
            # Add keyword scores  
            for i, doc in enumerate(keyword_docs):
                content_key = doc.page_content[:100]
                keyword_score = (len(keyword_docs) - i) / len(keyword_docs)
                
                if content_key in doc_scores:
                    # Combine scores
                    doc_scores[content_key]['score'] += keyword_score * self.keyword_weight
                    doc_scores[content_key]['methods'].append('keyword')
                else:
                    doc_scores[content_key] = {
                        'doc': doc,
                        'score': keyword_score * self.keyword_weight,
                        'methods': ['keyword']
                    }
            
            # Sort by combined score and return top k
            sorted_docs = sorted(doc_scores.values(), key=lambda x: x['score'], reverse=True)
            return [item['doc'] for item in sorted_docs[:k]]
    
    vector_retriever = vector_store.as_retriever(search_kwargs={"k": k})
    return HybridRetriever(vector_retriever, bm25_retriever, weights)


def evaluate_retrieval_methods(vector_store, bm25_retriever, questions: List[str], 
                             reference_contexts: List[List[Any]], k: int = 5,
                             evaluation_methods: List[str] = None) -> Dict[str, pd.DataFrame]:
    """
    Comprehensive evaluation of multiple retrieval methods using ranx-k.
    
    Args:
        vector_store: Vector store for semantic search
        bm25_retriever: BM25 retriever for keyword search
        questions: Evaluation questions
        reference_contexts: Reference documents for each question
        k: Number of documents to retrieve
        evaluation_methods: List of ranx-k methods to use ['kiwi_rouge', 'enhanced_rouge', 'ranx_similarity']
        
    Returns:
        Dictionary containing evaluation results and comparison DataFrames
        
    Example:
        >>> # Setup your retrievers
        >>> vector_store = ... # Your vector store
        >>> bm25_retriever = ... # Your BM25 retriever
        >>> 
        >>> # Prepare evaluation data
        >>> questions = ["질문 1", "질문 2", ...]
        >>> references = [[doc1, doc2], [doc3], ...]
        >>> 
        >>> # Run comprehensive evaluation
        >>> results = evaluate_retrieval_methods(
        ...     vector_store, bm25_retriever, questions, references, k=5
        ... )
        >>> 
        >>> # View results
        >>> print(results['summary_table'])
        >>> print(results['detailed_results'])
    """
    if evaluation_methods is None:
        evaluation_methods = ['kiwi_rouge', 'enhanced_rouge', 'ranx_similarity']
    
    print("🚀 Comprehensive Retrieval Methods Evaluation | 포괄적 검색 방법 평가")
    print("=" * 80)
    
    # Define retrieval methods to compare
    retrievers = {
        "semantic": {
            "name": "Semantic Search | 의미론적 검색",
            "retriever": vector_store.as_retriever(search_kwargs={"k": k}),
            "description": "Dense embedding similarity"
        },
        "keyword": {
            "name": "Keyword Search | 키워드 검색",
            "retriever": bm25_retriever,
            "description": "BM25 sparse matching"
        },
        "hybrid_balanced": {
            "name": "Hybrid Balanced | 균형 하이브리드",
            "retriever": create_hybrid_retriever(vector_store, bm25_retriever, [0.5, 0.5]),
            "description": "50% semantic + 50% keyword"
        },
        "hybrid_semantic": {
            "name": "Hybrid Semantic-Heavy | 의미 중심 하이브리드",
            "retriever": create_hybrid_retriever(vector_store, bm25_retriever, [0.7, 0.3]),
            "description": "70% semantic + 30% keyword"
        },
        "hybrid_keyword": {
            "name": "Hybrid Keyword-Heavy | 키워드 중심 하이브리드", 
            "retriever": create_hybrid_retriever(vector_store, bm25_retriever, [0.3, 0.7]),
            "description": "30% semantic + 70% keyword"
        }
    }
    
    all_results = {}
    summary_data = []
    
    for method_id, config in retrievers.items():
        method_name = config["name"]
        retriever = config["retriever"]
        
        print(f"\n🔄 Evaluating: {method_name}")
        print(f"📝 {config['description']}")
        print("-" * 50)
        
        method_results = {"method": method_name, "method_id": method_id}
        
        try:
            # Run each requested evaluation method
            if 'kiwi_rouge' in evaluation_methods:
                print("📊 Running Kiwi ROUGE evaluation | Kiwi ROUGE 평가 실행...")
                kiwi_results = simple_kiwi_rouge_evaluation(
                    retriever, questions, reference_contexts, k
                )
                method_results['kiwi_rouge'] = kiwi_results
                
                # Extract key metrics for summary
                if kiwi_results:
                    method_results['kiwi_rouge1'] = kiwi_results.get(f'kiwi_rouge1@{k}', 0)
                    method_results['kiwi_rouge2'] = kiwi_results.get(f'kiwi_rouge2@{k}', 0)
            
            if 'enhanced_rouge' in evaluation_methods:
                print("📊 Running Enhanced ROUGE evaluation | 향상된 ROUGE 평가 실행...")
                enhanced_results = rouge_kiwi_enhanced_evaluation(
                    retriever, questions, reference_contexts, k
                )
                method_results['enhanced_rouge'] = enhanced_results
                
                if enhanced_results:
                    method_results['enhanced_rouge1'] = enhanced_results.get(f'enhanced_rouge1@{k}', 0)
                    method_results['enhanced_rouge2'] = enhanced_results.get(f'enhanced_rouge2@{k}', 0)
            
            if 'ranx_similarity' in evaluation_methods:
                print("📊 Running ranx Similarity evaluation | ranx 유사도 평가 실행...")
                ranx_results = evaluate_with_ranx_similarity(
                    retriever, questions, reference_contexts, k,
                    method='kiwi_rouge', similarity_threshold=0.6
                )
                method_results['ranx_similarity'] = ranx_results
                
                if ranx_results:
                    method_results['hit_rate'] = ranx_results.get(f'hit_rate@{k}', 0)
                    method_results['ndcg'] = ranx_results.get(f'ndcg@{k}', 0)
                    method_results['mrr'] = ranx_results.get('mrr', 0)
            
            print(f"✅ {method_name} evaluation completed | 평가 완료")
            
        except Exception as e:
            print(f"❌ Error evaluating {method_name}: {e}")
            method_results['error'] = str(e)
        
        all_results[method_id] = method_results
        summary_data.append(method_results)
    
    # Create summary DataFrame
    summary_df = pd.DataFrame(summary_data)
    
    # Clean up summary DataFrame for display
    display_columns = ['method']
    metric_columns = []
    
    for col in summary_df.columns:
        if col in ['kiwi_rouge1', 'kiwi_rouge2', 'enhanced_rouge1', 'enhanced_rouge2', 
                  'hit_rate', 'ndcg', 'mrr']:
            metric_columns.append(col)
    
    display_columns.extend(sorted(metric_columns))
    if 'error' in summary_df.columns:
        display_columns.append('error')
    
    summary_df = summary_df[display_columns]
    
    # Sort by primary metric
    if metric_columns:
        primary_metric = metric_columns[0]
        summary_df = summary_df.sort_values(primary_metric, ascending=False, na_last=True)
    
    print(f"\n🏆 Evaluation Summary | 평가 요약")
    print("=" * 80)
    print(summary_df.to_string(index=False, float_format='%.3f'))
    
    # Find best performing methods
    print(f"\n🥇 Best Performing Methods | 최고 성능 방법:")
    for col in metric_columns:
        if col in summary_df.columns and not summary_df[col].isna().all():
            best_idx = summary_df[col].idxmax()
            best_method = summary_df.loc[best_idx, 'method']
            best_score = summary_df.loc[best_idx, col]
            print(f"  {col}: {best_method} ({best_score:.3f})")
    
    return {
        'summary_table': summary_df,
        'detailed_results': all_results,
        'retrievers_config': retrievers
    }


def quick_hit_rate_comparison(vector_store, bm25_retriever, questions: List[str], 
                            reference_contexts: List[List[Any]], k: int = 5) -> pd.DataFrame:
    """
    Quick hit rate comparison for fast evaluation.
    
    Args:
        vector_store: Vector store
        bm25_retriever: BM25 retriever
        questions: Test questions
        reference_contexts: Reference documents
        k: Number of documents to retrieve
        
    Returns:
        pandas.DataFrame: Hit rate comparison results
    """
    print("⚡ Quick Hit Rate Comparison | 빠른 적중률 비교")
    print("=" * 50)
    
    retrievers = {
        "Semantic | 의미론적": vector_store.as_retriever(search_kwargs={"k": k}),
        "Keyword | 키워드": bm25_retriever,
        "Hybrid (5:5) | 하이브리드": create_hybrid_retriever(vector_store, bm25_retriever, [0.5, 0.5]),
        "Hybrid (7:3) | 의미 중심": create_hybrid_retriever(vector_store, bm25_retriever, [0.7, 0.3]),
        "Hybrid (3:7) | 키워드 중심": create_hybrid_retriever(vector_store, bm25_retriever, [0.3, 0.7]),
    }
    
    results = []
    
    for method_name, retriever in retrievers.items():
        hits = 0
        total = len(questions)
        
        for question, ref_docs in zip(questions, reference_contexts):
            try:
                retrieved = retriever.invoke(question)
                retrieved_texts = [doc.page_content for doc in retrieved]
                ref_texts = [
                    doc.page_content if hasattr(doc, 'page_content') else str(doc)
                    for doc in ref_docs
                ]
                
                # Simple substring matching
                hit = any(
                    any(ref[:100] in ret for ret in retrieved_texts)
                    for ref in ref_texts
                )
                
                if hit:
                    hits += 1
                    
            except Exception as e:
                print(f"⚠️ Error in {method_name}: {e}")
        
        hit_rate = hits / total if total > 0 else 0
        results.append({
            "Method | 방법": method_name,
            "Hit Rate | 적중률": hit_rate,
            "Hits | 적중 수": f"{hits}/{total}"
        })
        
        print(f"  {method_name}: {hit_rate:.3f}")
    
    df = pd.DataFrame(results).sort_values("Hit Rate | 적중률", ascending=False)
    
    print(f"\n📊 Quick Comparison Results | 빠른 비교 결과:")
    print(df.to_string(index=False, float_format='%.3f'))
    
    return df


if __name__ == "__main__":
    print("📖 Retrieval Methods Comparison Example | 검색 방법 비교 예제")
    print("=" * 60)
    print()
    print("🔧 To use this example:")
    print("1. Replace mock objects with your actual vector store and BM25 retriever")
    print("2. Provide your evaluation questions and reference documents")
    print("3. Run the evaluation functions")
    print()
    print("💡 Example usage:")
    print("""
# Your setup
vector_store = ...  # Your Chroma/Pinecone/FAISS vector store
bm25_retriever = ...  # Your BM25 retriever
questions = ["질문 1", "질문 2", ...]
references = [[doc1, doc2], [doc3], ...]

# Quick evaluation
quick_results = quick_hit_rate_comparison(
    vector_store, bm25_retriever, questions, references, k=5
)

# Comprehensive evaluation  
full_results = evaluate_retrieval_methods(
    vector_store, bm25_retriever, questions, references, k=5,
    evaluation_methods=['kiwi_rouge', 'ranx_similarity']  
)

print(full_results['summary_table'])
    """)