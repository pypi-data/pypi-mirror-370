"""
Reference-based evaluation example for ranx-k.

This example demonstrates the difference between retrieval-based and 
reference-based evaluation modes, showing how reference-based mode
provides more accurate assessment of retrieval completeness.
"""

# Simulated example showing the evaluation modes
print("🚀 Reference-based Evaluation Example | 참조 기반 평가 예제")
print("=" * 60)

# Example retriever and data setup would go here
# from your_module import retriever, questions, reference_contexts

# Simulated evaluation results for demonstration
print("\n📊 Retrieval-based Evaluation (Original) | 검색 기반 평가 (기존):")
print("   - Evaluates only retrieved documents | 검색된 문서만 평가")
print("   - May show perfect scores even when missing references | 참조 문서를 놓쳐도 완벽한 점수 가능")
print("\n   Example results | 예시 결과:")
print("   hit_rate@5: 1.000")
print("   ndcg@5: 1.000")
print("   map@5: 1.000")
print("   mrr: 1.000")

print("\n📊 Reference-based Evaluation (New) | 참조 기반 평가 (신규):")
print("   - Evaluates against all reference documents | 모든 참조 문서 대상 평가")
print("   - Accurately reflects retrieval completeness | 검색 완전성을 정확히 반영")
print("\n   Example results | 예시 결과:")
print("   hit_rate@5: 0.900")
print("   ndcg@5: 0.876")
print("   map@5: 0.833")
print("   mrr: 0.900")
print("   recall@5: 0.833")

print("\n💡 Key Differences | 주요 차이점:")
print("1. Recall calculation | 재현율 계산:")
print("   - Retrieval-based | 검색 기반: recall = 1.0 (all retrieved docs are relevant)")
print("   - Reference-based | 참조 기반: recall = 0.833 (5/6 reference docs found)")

print("\n2. Use cases | 사용 사례:")
print("   - Retrieval-based | 검색 기반: Quick quality check of retrieved results")
print("   - Reference-based | 참조 기반: Comprehensive evaluation for production")

# Code example
print("\n📝 Code Example | 코드 예제:")
print("""
from ranx_k.evaluation import evaluate_with_ranx_similarity

# Reference-based evaluation (recommended)
results = evaluate_with_ranx_similarity(
    retriever=your_retriever,
    questions=questions,
    reference_contexts=reference_contexts,
    k=5,
    method='kiwi_rouge',
    similarity_threshold=0.5,
    evaluation_mode='reference_based',  # NEW: Proper recall calculation
    use_graded_relevance=False         # NEW: Optional graded relevance
)

print(f"Recall@5: {results['recall@5']:.3f}")  # Now available!
""")

print("\n✅ Recommendation | 권장사항:")
print("   Use 'reference_based' mode for accurate evaluation!")
print("   정확한 평가를 위해 'reference_based' 모드를 사용하세요!")