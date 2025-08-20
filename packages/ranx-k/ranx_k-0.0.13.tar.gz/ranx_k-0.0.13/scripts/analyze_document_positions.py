"""Analyze document positions and relevance for debugging MAP calculation."""

from ranx_k.evaluation.similarity_ranx import KiwiRougeSimilarityCalculator
import numpy as np

# You'll need to set up your retriever and data here
# This is a template showing the analysis structure

def analyze_retrieval_positions(questions, reference_contexts, hybrid_retriever, 
                               start_idx=30, end_idx=35, threshold=0.5):
    """
    Analyze retrieval positions to understand why MAP values might be identical.
    
    Args:
        questions: List of query questions
        reference_contexts: List of reference document lists
        hybrid_retriever: The retriever to evaluate
        start_idx: Starting index for analysis
        end_idx: Ending index for analysis
        threshold: Similarity threshold for relevance
    """
    calculator = KiwiRougeSimilarityCalculator()
    
    all_positions = []
    all_ap_scores = []
    
    for i, (question, ref_docs) in enumerate(zip(questions[start_idx:end_idx], 
                                                  reference_contexts[start_idx:end_idx])):
        print(f"\n=== 질문 {i+1} ===")
        print(f"질문: {question[:50]}...")
        
        retrieved_docs = hybrid_retriever.invoke(question)[:5]
        retrieved_texts = [doc.page_content for doc in retrieved_docs]
        ref_texts = [ref.page_content for ref in ref_docs]
        
        similarity_matrix = calculator.calculate_similarity_matrix(ref_texts, retrieved_texts)
        
        # Track relevant documents and their positions
        relevant_positions = []
        relevant_scores = []
        
        # Analyze each document
        print("\n문서별 분석:")
        for j in range(len(retrieved_texts)):
            max_sim = np.max(similarity_matrix[:, j])
            is_relevant = max_sim >= threshold
            
            if is_relevant:
                relevant_positions.append(j+1)  # 1-based position
                relevant_scores.append(max_sim)
            
            print(f"  doc_{j}: 유사도={max_sim:.3f}, 관련성={'YES' if is_relevant else 'NO'}")
        
        print(f"\n  관련 문서 수: {len(relevant_positions)}")
        print(f"  관련 문서 위치: {relevant_positions}")
        
        # Calculate Average Precision for this query
        if relevant_positions:
            precisions = []
            for idx, pos in enumerate(relevant_positions):
                precision_at_k = (idx + 1) / pos
                precisions.append(precision_at_k)
                print(f"  Precision at position {pos}: {precision_at_k:.3f}")
            
            ap = sum(precisions) / len(ref_texts)  # Should be total relevant docs
            print(f"  Average Precision: {ap:.3f}")
            all_ap_scores.append(ap)
        else:
            print("  Average Precision: 0.000 (no relevant documents)")
            all_ap_scores.append(0.0)
        
        all_positions.append(relevant_positions)
    
    # Summary statistics
    print("\n=== 요약 통계 ===")
    print(f"평균 Average Precision: {np.mean(all_ap_scores):.3f}")
    print(f"AP 표준편차: {np.std(all_ap_scores):.3f}")
    print(f"개별 AP 값들: {[f'{ap:.3f}' for ap in all_ap_scores]}")
    
    # Check if all queries have same pattern
    position_patterns = [tuple(pos) for pos in all_positions]
    unique_patterns = set(position_patterns)
    print(f"\n고유한 위치 패턴 수: {len(unique_patterns)}")
    for pattern in unique_patterns:
        count = position_patterns.count(pattern)
        print(f"  패턴 {pattern}: {count}개 질문")
    
    return all_positions, all_ap_scores

# Example usage (you'll need to provide your actual data)
if __name__ == "__main__":
    print("이 스크립트를 실행하려면 실제 데이터와 retriever가 필요합니다.")
    print("\n사용 예시:")
    print("from your_module import questions, reference_contexts, hybrid_retriever")
    print("analyze_retrieval_positions(questions, reference_contexts, hybrid_retriever)")