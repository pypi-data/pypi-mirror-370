#!/usr/bin/env python3
"""
Test script for comparing different retrieval methods using ranx-k evaluation.

This script demonstrates how to integrate ranx-k evaluation toolkit 
with various retrieval methods including semantic search, keyword search,
and hybrid approaches.
"""

import pandas as pd
from typing import List, Dict, Any, Optional, Union
from ranx_k.evaluation.utils import comprehensive_evaluation_comparison
from ranx_k.evaluation.kiwi_rouge import simple_kiwi_rouge_evaluation
from ranx_k.evaluation.enhanced_rouge import rouge_kiwi_enhanced_evaluation
from ranx_k.evaluation.similarity_ranx import evaluate_with_ranx_similarity
from ranx_k.tokenizers.kiwi_tokenizer import setup_korean_tokenizer


def create_hybrid_retriever(vector_store, bm25_retriever, weights: List[float]):
    """
    Create a hybrid retriever combining semantic and keyword search.
    
    Args:
        vector_store: Vector store for semantic search
        bm25_retriever: BM25 retriever for keyword search
        weights: [semantic_weight, keyword_weight] - should sum to 1.0
        
    Returns:
        Hybrid retriever function
    """
    class HybridRetriever:
        def __init__(self, vector_retriever, bm25_retriever, weights):
            self.vector_retriever = vector_retriever
            self.bm25_retriever = bm25_retriever
            self.semantic_weight = weights[0]
            self.keyword_weight = weights[1]
            
        def invoke(self, query: str, k: int = 5):
            """Invoke hybrid retrieval."""
            # Get results from both retrievers
            semantic_docs = self.vector_retriever.invoke(query)[:k]
            keyword_docs = self.bm25_retriever.invoke(query)[:k]
            
            # Simple fusion: combine and deduplicate based on content
            combined_docs = []
            seen_content = set()
            
            # Add semantic results with weight
            for doc in semantic_docs:
                content_hash = hash(doc.page_content[:100])  # Use first 100 chars as identifier
                if content_hash not in seen_content:
                    doc.metadata['retrieval_score'] = self.semantic_weight
                    doc.metadata['retrieval_method'] = 'semantic'
                    combined_docs.append(doc)
                    seen_content.add(content_hash)
            
            # Add keyword results with weight
            for doc in keyword_docs:
                content_hash = hash(doc.page_content[:100])
                if content_hash not in seen_content:
                    doc.metadata['retrieval_score'] = self.keyword_weight
                    doc.metadata['retrieval_method'] = 'keyword'
                    combined_docs.append(doc)
                    seen_content.add(content_hash)
                elif content_hash in seen_content:
                    # If already exists, boost the score
                    for existing_doc in combined_docs:
                        if hash(existing_doc.page_content[:100]) == content_hash:
                            existing_doc.metadata['retrieval_score'] += self.keyword_weight
                            existing_doc.metadata['retrieval_method'] = 'hybrid'
                            break
            
            # Sort by combined score and return top k
            combined_docs.sort(key=lambda x: x.metadata.get('retrieval_score', 0), reverse=True)
            return combined_docs[:k]
    
    vector_retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    return HybridRetriever(vector_retriever, bm25_retriever, weights)


def compare_retrieval_methods_with_ranx(vector_store, bm25_retriever, questions: List[str], 
                                       reference_contexts: List[List[Any]], k: int = 5) -> pd.DataFrame:
    """
    Compare different retrieval methods using comprehensive ranx-k evaluation.
    
    This function evaluates multiple retrieval approaches using all available
    ranx-k evaluation methods: Kiwi ROUGE, Enhanced ROUGE, and Similarity-based ranx.
    
    Args:
        vector_store: Vector store for semantic search
        bm25_retriever: BM25 retriever for keyword search  
        questions: List of evaluation questions
        reference_contexts: List of reference document lists for each question
        k: Number of top documents to retrieve and evaluate
        
    Returns:
        pandas.DataFrame: Comprehensive comparison results
        
    Example:
        >>> results_df = compare_retrieval_methods_with_ranx(
        ...     vector_store=my_vector_store,
        ...     bm25_retriever=my_bm25_retriever,
        ...     questions=test_questions,
        ...     reference_contexts=test_references,
        ...     k=5
        ... )
        >>> print(results_df)
    """
    print("🚀 Retrieval Methods Comparison with ranx-k | 검색 방법 비교 (ranx-k 평가)")
    print("=" * 80)
    
    # Define retrieval methods to compare
    retrievers = {
        "semantic_search": {
            "name": "Semantic Search | 의미론적 검색",
            "retriever": vector_store.as_retriever(search_kwargs={"k": k}),
            "description": "Dense embedding-based semantic similarity"
        },
        "keyword_search": {
            "name": "Keyword Search | 키워드 검색", 
            "retriever": bm25_retriever,
            "description": "BM25 sparse keyword matching"
        },
        "hybrid_balanced": {
            "name": "Hybrid (5:5) | 하이브리드 (5:5)",
            "retriever": create_hybrid_retriever(vector_store, bm25_retriever, [0.5, 0.5]),
            "description": "Balanced semantic + keyword fusion"
        },
        "hybrid_semantic_heavy": {
            "name": "Hybrid (7:3) | 하이브리드 (7:3)",
            "retriever": create_hybrid_retriever(vector_store, bm25_retriever, [0.7, 0.3]),
            "description": "Semantic-heavy hybrid approach"
        },
        "hybrid_keyword_heavy": {
            "name": "Hybrid (3:7) | 하이브리드 (3:7)",
            "retriever": create_hybrid_retriever(vector_store, bm25_retriever, [0.3, 0.7]),
            "description": "Keyword-heavy hybrid approach"
        }
    }
    
    all_results = []
    
    for method_id, method_config in retrievers.items():
        method_name = method_config["name"]
        retriever = method_config["retriever"]
        description = method_config["description"]
        
        print(f"\n{'='*60}")
        print(f"🔄 Evaluating: {method_name}")
        print(f"📝 Description: {description}")
        print(f"{'='*60}")
        
        try:
            # Run comprehensive evaluation using ranx-k
            evaluation_results = comprehensive_evaluation_comparison(
                retriever=retriever,
                questions=questions,
                reference_contexts=reference_contexts,
                k=k
            )
            
            # Extract key metrics from each evaluation method
            method_results = {"method": method_name, "method_id": method_id}
            
            # Extract Kiwi ROUGE metrics
            if "Kiwi ROUGE" in evaluation_results and evaluation_results["Kiwi ROUGE"]:
                kiwi_results = evaluation_results["Kiwi ROUGE"]
                for metric, value in kiwi_results.items():
                    if not metric.endswith('_std'):
                        method_results[f"kiwi_{metric}"] = value
            
            # Extract Enhanced ROUGE metrics  
            if "Enhanced ROUGE" in evaluation_results and evaluation_results["Enhanced ROUGE"]:
                enhanced_results = evaluation_results["Enhanced ROUGE"]
                for metric, value in enhanced_results.items():
                    if not metric.endswith('_std'):
                        method_results[f"enhanced_{metric}"] = value
            
            # Extract Similarity ranx metrics
            if "Similarity ranx" in evaluation_results and evaluation_results["Similarity ranx"]:
                ranx_results = evaluation_results["Similarity ranx"]
                for metric, value in ranx_results.items():
                    method_results[f"ranx_{metric}"] = value
            
            all_results.append(method_results)
            
        except Exception as e:
            print(f"❌ Error evaluating {method_name} | 평가 중 오류: {e}")
            # Add error entry
            all_results.append({
                "method": method_name,
                "method_id": method_id,
                "error": str(e)
            })
    
    # Convert results to DataFrame
    if all_results:
        results_df = pd.DataFrame(all_results)
        
        # Reorder columns for better readability
        base_cols = ["method", "method_id"]
        metric_cols = [col for col in results_df.columns if col not in base_cols + ["error"]]
        ordered_cols = base_cols + sorted(metric_cols)
        
        if "error" in results_df.columns:
            ordered_cols.append("error")
            
        results_df = results_df[ordered_cols]
        
        # Sort by a primary metric (try hit_rate, then ndcg, then rouge1)
        sort_candidates = [
            col for col in results_df.columns 
            if any(key in col.lower() for key in ["hit_rate", "ndcg", "rouge1"])
        ]
        
        if sort_candidates:
            sort_col = sort_candidates[0]
            results_df = results_df.sort_values(by=sort_col, ascending=False, na_position='last')
        
        print("\n🏆 Final Comparison Results | 최종 비교 결과")
        print("=" * 80)
        print(results_df.to_string(index=False, float_format='%.3f'))
        
        # Print summary recommendations
        print(f"\n💡 Performance Summary | 성능 요약:")
        if len(results_df) > 0 and not results_df.empty:
            best_method = results_df.iloc[0]['method']
            print(f"🥇 Best performing method | 최고 성능: {best_method}")
            
            # Find method-specific strengths
            for col in results_df.columns:
                if col.startswith(('kiwi_', 'enhanced_', 'ranx_')) and col not in ['method', 'method_id']:
                    try:
                        best_idx = results_df[col].idxmax()
                        best_method_for_metric = results_df.loc[best_idx, 'method']
                        best_score = results_df.loc[best_idx, col]
                        if pd.notna(best_score):
                            print(f"📊 Best {col} | 최고 {col}: {best_method_for_metric} ({best_score:.3f})")
                    except (KeyError, ValueError):
                        continue
        
        return results_df
    
    else:
        print("❌ No evaluation results obtained | 평가 결과를 얻지 못했습니다.")
        return pd.DataFrame()


def simple_hit_rate_comparison(vector_store, bm25_retriever, questions: List[str], 
                              reference_contexts: List[List[Any]], k: int = 5) -> pd.DataFrame:
    """
    Simple hit rate comparison for quick evaluation.
    
    This is a lightweight alternative when full ranx-k evaluation is not needed.
    
    Args:
        vector_store: Vector store for semantic search
        bm25_retriever: BM25 retriever for keyword search
        questions: List of evaluation questions  
        reference_contexts: List of reference document lists
        k: Number of documents to retrieve
        
    Returns:
        pandas.DataFrame: Simple hit rate comparison results
    """
    print("🚀 Simple Hit Rate Comparison | 간단한 적중률 비교")
    print("=" * 60)
    
    results = []
    
    # Define retrieval methods
    retrievers = {
        "Semantic Search | 의미론적 검색": vector_store.as_retriever(search_kwargs={"k": k}),
        "Keyword Search | 키워드 검색": bm25_retriever,
        "Hybrid (5:5) | 하이브리드 (5:5)": create_hybrid_retriever(vector_store, bm25_retriever, [0.5, 0.5]),
        "Hybrid (7:3) | 하이브리드 (7:3)": create_hybrid_retriever(vector_store, bm25_retriever, [0.7, 0.3]),
        "Hybrid (3:7) | 하이브리드 (3:7)": create_hybrid_retriever(vector_store, bm25_retriever, [0.3, 0.7]),
    }
    
    for method_name, retriever in retrievers.items():
        print(f"🔄 Evaluating {method_name} | {method_name} 평가 중...")
        
        # Calculate simple hit rate
        hits = 0
        total_docs = 0
        
        for question, ref_docs in zip(questions, reference_contexts):
            try:
                retrieved = retriever.invoke(question)
                retrieved_content = [doc.page_content for doc in retrieved]
                ref_content = [
                    doc.page_content if hasattr(doc, 'page_content') else str(doc) 
                    for doc in ref_docs
                ]
                
                # Check if any reference content appears in retrieved content
                hit = any(
                    any(ref_text[:100] in ret_text for ret_text in retrieved_content)
                    for ref_text in ref_content
                )
                
                if hit:
                    hits += 1
                total_docs += 1
                
            except Exception as e:
                print(f"   ⚠️ Error processing question: {e}")
                total_docs += 1  # Still count it for denominator
        
        hit_rate = hits / total_docs if total_docs > 0 else 0
        
        results.append({
            "Method | 방법": method_name,
            "Hit Rate | 적중률": hit_rate,
            "Hits | 적중": hits,
            "Total | 전체": total_docs
        })
        
        print(f"   ✅ Hit Rate | 적중률: {hit_rate:.3f} ({hits}/{total_docs})")
    
    # Convert to DataFrame and sort
    comparison_df = pd.DataFrame(results)
    comparison_df = comparison_df.sort_values("Hit Rate | 적중률", ascending=False)
    
    print(f"\n📊 Hit Rate Comparison Results | 적중률 비교 결과:")
    print(comparison_df.to_string(index=False, float_format='%.3f'))
    
    return comparison_df


def test_retrieval_comparison_example():
    """
    Example test function showing how to use the retrieval comparison functions.
    
    This function demonstrates the usage with mock data. 
    Replace with your actual vector store, BM25 retriever, and test data.
    """
    print("🧪 Testing Retrieval Methods Comparison | 검색 방법 비교 테스트")
    print("=" * 70)
    
    # Mock data for demonstration - replace with your actual data
    class MockDocument:
        def __init__(self, content):
            self.page_content = content
            self.metadata = {}
    
    class MockRetriever:
        def __init__(self, docs):
            self.docs = docs
            
        def invoke(self, query):
            # Simple mock: return first 5 docs
            return self.docs[:5]
        
        def as_retriever(self, search_kwargs=None):
            return self
    
    # Create mock data
    mock_docs = [MockDocument(f"This is document {i} about topic {i%3}") for i in range(20)]
    mock_vector_store = MockRetriever(mock_docs)
    mock_bm25_retriever = MockRetriever(mock_docs[::2])  # Different subset
    
    mock_questions = [
        "What is document 1 about?",
        "Tell me about topic 0",
        "Find information on topic 2"
    ]
    
    mock_references = [
        [MockDocument("This is document 1 about topic 1")],
        [MockDocument("This is document 0 about topic 0")], 
        [MockDocument("This is document 2 about topic 2")]
    ]
    
    print("📝 Note: Using mock data for demonstration | 데모용 모조 데이터 사용")
    print("🔄 To use with real data, replace mock objects with your actual retrievers")
    print()
    
    try:
        # Test simple hit rate comparison
        print("1️⃣ Simple Hit Rate Comparison | 간단한 적중률 비교:")
        simple_results = simple_hit_rate_comparison(
            mock_vector_store, mock_bm25_retriever, 
            mock_questions, mock_references, k=5
        )
        
        print(f"\n✅ Simple comparison completed | 간단한 비교 완료")
        
        # Uncomment to test full ranx-k evaluation (requires actual retrievers)
        # print("\n2️⃣ Full ranx-k Evaluation | 전체 ranx-k 평가:")
        # full_results = compare_retrieval_methods_with_ranx(
        #     mock_vector_store, mock_bm25_retriever,
        #     mock_questions, mock_references, k=5
        # )
        
    except Exception as e:
        print(f"❌ Test failed | 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_retrieval_comparison_example()