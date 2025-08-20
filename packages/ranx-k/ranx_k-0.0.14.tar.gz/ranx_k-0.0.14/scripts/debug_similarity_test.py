#!/usr/bin/env python3

"""
Debug script to test similarity calculation step by step.
"""

import numpy as np
from ranx_k.evaluation.similarity_ranx import KiwiRougeSimilarityCalculator, EmbeddingSimilarityCalculator

def debug_similarity_detailed():
    """Debug similarity calculation with sample data."""
    
    print("🔍 Detailed Similarity Debug | 상세 유사도 디버그")
    print("="*70)
    
    # Sample Korean texts for testing
    print("📝 Sample Data | 샘플 데이터:")
    ref_texts = [
        "RAG는 검색 증강 생성 모델로, 외부 지식을 활용하여 더 정확한 답변을 생성합니다.",
        "자연어처리에서 토큰화는 텍스트를 의미 있는 단위로 분할하는 과정입니다."
    ]
    
    ret_texts = [
        "RAG 시스템은 검색과 생성을 결합한 AI 모델입니다.",
        "토큰화는 문장을 단어나 형태소로 나누는 전처리 단계입니다.", 
        "완전히 다른 주제에 대한 내용입니다.",
        "머신러닝은 인공지능의 한 분야입니다.",
        "데이터 전처리는 모델 성능에 중요한 영향을 미칩니다."
    ]
    
    print(f"Reference texts ({len(ref_texts)}):")
    for i, text in enumerate(ref_texts):
        print(f"  ref_{i}: {text}")
    
    print(f"\nRetrieved texts ({len(ret_texts)}):")
    for i, text in enumerate(ret_texts):
        print(f"  ret_{i}: {text}")
    
    # Test 1: Kiwi ROUGE similarity
    print(f"\n🔍 Test 1: Kiwi ROUGE Similarity | Kiwi ROUGE 유사도 테스트")
    print("-" * 50)
    
    kiwi_calc = KiwiRougeSimilarityCalculator()
    
    # Test tokenization first
    print("Tokenization test:")
    for i, text in enumerate(ref_texts[:2]):
        tokens = kiwi_calc.tokenize_with_kiwi(text)
        print(f"  ref_{i} tokens: {tokens}")
    
    for i, text in enumerate(ret_texts[:2]):
        tokens = kiwi_calc.tokenize_with_kiwi(text)
        print(f"  ret_{i} tokens: {tokens}")
    
    # Calculate similarity matrix
    kiwi_matrix = kiwi_calc.calculate_similarity_matrix(ref_texts, ret_texts)
    print(f"\nKiwi ROUGE similarity matrix shape: {kiwi_matrix.shape}")
    print("Kiwi ROUGE similarity matrix:")
    print(kiwi_matrix)
    print(f"Max similarity: {np.max(kiwi_matrix):.4f}")
    print(f"Min similarity: {np.min(kiwi_matrix):.4f}")
    print(f"Mean similarity: {np.mean(kiwi_matrix):.4f}")
    
    # Test 2: Embedding similarity
    print(f"\n🔍 Test 2: Embedding Similarity | 임베딩 유사도 테스트")
    print("-" * 50)
    
    try:
        embedding_calc = EmbeddingSimilarityCalculator()
        embedding_matrix = embedding_calc.calculate_similarity_matrix(ref_texts, ret_texts)
        print(f"Embedding similarity matrix shape: {embedding_matrix.shape}")
        print("Embedding similarity matrix:")
        print(embedding_matrix)
        print(f"Max similarity: {np.max(embedding_matrix):.4f}")
        print(f"Min similarity: {np.min(embedding_matrix):.4f}")
        print(f"Mean similarity: {np.mean(embedding_matrix):.4f}")
    except Exception as e:
        print(f"Embedding calculation failed: {e}")
    
    # Test 3: Threshold analysis
    print(f"\n🎯 Test 3: Threshold Analysis | 임계값 분석")
    print("-" * 50)
    
    thresholds = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    
    print("Kiwi ROUGE threshold analysis:")
    for threshold in thresholds:
        above_threshold = (kiwi_matrix >= threshold).sum()
        total_pairs = kiwi_matrix.shape[0] * kiwi_matrix.shape[1]
        percentage = (above_threshold / total_pairs) * 100
        print(f"  Threshold {threshold:.1f}: {above_threshold:2d}/{total_pairs} ({percentage:5.1f}%) pairs above")
    
    if 'embedding_matrix' in locals():
        print("\nEmbedding threshold analysis:")
        for threshold in thresholds:
            above_threshold = (embedding_matrix >= threshold).sum()
            total_pairs = embedding_matrix.shape[0] * embedding_matrix.shape[1]
            percentage = (above_threshold / total_pairs) * 100
            print(f"  Threshold {threshold:.1f}: {above_threshold:2d}/{total_pairs} ({percentage:5.1f}%) pairs above")
    
    # Test 4: Simulate ranx evaluation logic
    print(f"\n📊 Test 4: Simulate ranx Logic | ranx 로직 시뮬레이션")
    print("-" * 50)
    
    similarity_threshold = 0.3
    
    print(f"Using threshold: {similarity_threshold}")
    print("Simulating qrels and run creation...")
    
    qrels_dict = {}
    run_dict = {}
    query_id = "test_query"
    
    qrels_dict[query_id] = {}
    run_dict[query_id] = {}
    
    for j, ret_text in enumerate(ret_texts):
        doc_id = f"doc_{j}"
        
        # Find maximum similarity with any reference document
        max_similarity = np.max(kiwi_matrix[:, j]) if kiwi_matrix.shape[0] > 0 else 0
        
        # Add to run (all retrieved documents with their similarity scores)
        run_dict[query_id][doc_id] = float(max_similarity)
        
        # Add to qrels only if above threshold (relevant documents)
        if max_similarity >= similarity_threshold:
            qrels_dict[query_id][doc_id] = 1.0
    
    print(f"qrels: {qrels_dict}")
    print(f"run: {run_dict}")
    print(f"Relevant documents (qrels): {len(qrels_dict[query_id])}")
    print(f"Retrieved documents (run): {len(run_dict[query_id])}")
        
    # Test ranx evaluation
    try:
        from ranx import Qrels, Run, evaluate
        
        qrels = Qrels(qrels_dict)
        run = Run(run_dict)
        
        metrics = ["hit_rate@5", "ndcg@5", "map@5", "mrr"]
        results = evaluate(qrels, run, metrics)
        
        print(f"\n🏆 Ranx evaluation results:")
        for metric, score in results.items():
            print(f"  {metric}: {score:.3f}")
            
    except Exception as e:
        print(f"Ranx evaluation failed: {e}")

if __name__ == "__main__":
    debug_similarity_detailed()