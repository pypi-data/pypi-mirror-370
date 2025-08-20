#!/usr/bin/env python3
"""
Korean RAG Evaluation Example Using OpenAI Embeddings

This example demonstrates how to evaluate Korean RAG systems using 
OpenAI's text-embedding-3-small/large models.

Note: Requires OpenAI API key and costs are incurred based on usage.
"""

import os
from ranx_k.evaluation.openai_similarity import (
    evaluate_with_openai_similarity, 
    estimate_openai_cost
)


class SimpleRetriever:
    """Simple test retriever"""
    
    def __init__(self, documents):
        self.documents = documents
    
    def invoke(self, query):
        # In practice, more complex search logic would be implemented here
        return self.documents


def main():
    print("🤖 Korean RAG Evaluation Example Using OpenAI Embeddings | OpenAI Embeddings를 사용한 한국어 RAG 평가 예제")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set | OPENAI_API_KEY 환경변수가 설정되지 않았습니다!")
        print("💡 Setup Instructions | 설정 방법:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print("   or add to .env file | 또는 .env 파일에 추가하세요.")
        return
    
    # 1. Prepare test data
    questions = [
        "자연어처리 기술의 최신 동향은?",
        "OpenAI의 임베딩 모델 특징은?",
        "한국어 AI 모델 개발의 어려움은?"
    ]
    
    documents = [
        "자연어처리는 빠르게 발전하고 있으며, 대규모 언어모델이 주요 트렌드입니다.",
        "OpenAI의 임베딩 모델은 다국어를 지원하고 높은 정확도를 자랑합니다.",
        "한국어 AI 개발은 언어의 복잡성과 데이터 부족이 주요 도전과제입니다.",
        "RAG 시스템은 검색과 생성을 결합하여 더 정확한 답변을 제공합니다.",
        "임베딩 기술은 의미적 유사성을 벡터 공간에서 측정할 수 있게 합니다."
    ]
    
    reference_contexts = [
        [documents[0]],
        [documents[1]],
        [documents[2]]
    ]
    
    # 2. Cost estimation
    print("\n💰 OpenAI API Cost Estimation | OpenAI API 비용 추정:")
    print("-" * 30)
    
    total_texts = len(questions) + len(documents) + sum(len(refs) for refs in reference_contexts)
    
    for model in ["text-embedding-3-small", "text-embedding-3-large"]:
        cost_info = estimate_openai_cost(total_texts, model_name=model)
        print(f"{model}:")
        print(f"  - Estimated Cost | 예상 비용: ${cost_info['estimated_cost_usd']} ({cost_info['estimated_cost_krw']}원)")
        print(f"  - Total Tokens | 총 토큰: {cost_info['total_tokens']:,}")
    
    # 3. User confirmation
    print(f"\nProcessing {total_texts} texts total | 총 {total_texts}개 텍스트를 처리합니다.")
    user_input = input("Continue? | 계속 진행하시겠습니까? (y/N): ").strip().lower()
    if user_input != 'y':
        print("Evaluation cancelled | 평가를 취소했습니다.")
        return
    
    # 4. Initialize retriever
    retriever = SimpleRetriever(documents)
    
    # 5. OpenAI text-embedding-3-small evaluation
    print("\n🔍 Evaluating with OpenAI text-embedding-3-small | OpenAI text-embedding-3-small로 평가 중...")
    
    try:
        results_small = evaluate_with_openai_similarity(
            retriever=retriever,
            questions=questions,
            reference_contexts=reference_contexts,
            k=3,
            model_name="text-embedding-3-small",
            similarity_threshold=0.7
        )
        
        print("\n📊 text-embedding-3-small Results | text-embedding-3-small 결과:")
        print("-" * 35)
        for metric, score in results_small.items():
            print(f"{metric:12s}: {score:.4f}")
            
    except Exception as e:
        print(f"❌ text-embedding-3-small evaluation failed | text-embedding-3-small 평가 실패: {e}")
        return
    
    # 6. OpenAI text-embedding-3-large evaluation (optional)
    print("\n🔍 Evaluate with OpenAI text-embedding-3-large? | OpenAI text-embedding-3-large로 평가할까요?")
    user_input = input("Higher performance but more expensive | 더 높은 성능이지만 비용이 더 듭니다. (y/N): ").strip().lower()
    
    if user_input == 'y':
        try:
            results_large = evaluate_with_openai_similarity(
                retriever=retriever,
                questions=questions,
                reference_contexts=reference_contexts,
                k=3,
                model_name="text-embedding-3-large",
                similarity_threshold=0.7
            )
            
            print("\n📊 text-embedding-3-large Results | text-embedding-3-large 결과:")
            print("-" * 35)
            for metric, score in results_large.items():
                print(f"{metric:12s}: {score:.4f}")
            
            # 7. Performance comparison
            print("\n📈 Model Performance Comparison | 모델 성능 비교:")
            print("-" * 35)
            print(f"{'Metric':<12} {'Small':<8} {'Large':<8} {'Improvement | 개선':<8}")
            print("-" * 35)
            
            for metric in results_small.keys():
                small_score = results_small[metric]
                large_score = results_large[metric]
                improvement = ((large_score - small_score) / small_score * 100) if small_score > 0 else 0
                print(f"{metric:<12} {small_score:<8.4f} {large_score:<8.4f} {improvement:+6.1f}%")
                
        except Exception as e:
            print(f"❌ text-embedding-3-large evaluation failed | text-embedding-3-large 평가 실패: {e}")
    
    print("\n" + "=" * 60)
    print("✅ OpenAI Embeddings Evaluation Completed | OpenAI Embeddings 평가 완료!")
    print("\n💡 Tips | 팁:")
    print("- Store API key securely in .env file | API 키를 .env 파일에 저장하여 안전하게 관리하세요")
    print("- Optimize API calls by adjusting batch size | 배치 크기를 조정하여 API 호출 횟수를 최적화할 수 있습니다")
    print("- text-embedding-3-small generally offers best cost-performance ratio | text-embedding-3-small이 일반적으로 비용 대비 성능이 좋습니다")
    print("- Consider caching for production environments | 프로덕션 환경에서는 캐싱을 고려하세요")


def show_openai_embedding_models():
    """Display OpenAI Embedding model information"""
    print("\n🤖 OpenAI Embedding Model Comparison | OpenAI Embedding 모델 비교:")
    print("=" * 50)
    
    models = [
        {
            "name": "text-embedding-3-small",
            "dimensions": 1536,
            "cost_per_1M": "$0.02",
            "performance": "High | 높음",
            "recommended": "✅ Recommended | 권장"
        },
        {
            "name": "text-embedding-3-large", 
            "dimensions": 3072,
            "cost_per_1M": "$0.13",
            "performance": "Highest | 최고",
            "recommended": "For high performance | 고성능 필요시"
        },
        {
            "name": "text-embedding-ada-002",
            "dimensions": 1536, 
            "cost_per_1M": "$0.10",
            "performance": "Average | 보통",
            "recommended": "Legacy model | 구 모델"
        }
    ]
    
    print(f"{'Model Name | 모델명':<25} {'Dimensions | 차원':<6} {'Cost | 비용':<8} {'Performance | 성능':<6} {'Recommendation | 추천'}")
    print("-" * 65)
    
    for model in models:
        print(f"{model['name']:<25} {model['dimensions']:<6} {model['cost_per_1M']:<8} "
              f"{model['performance']:<6} {model['recommended']}")
    
    print("\n🔗 More Information | 더 자세한 정보:")
    print("   - OpenAI Embeddings: https://platform.openai.com/docs/guides/embeddings")
    print("   - Pricing | 가격 정보: https://openai.com/pricing")


if __name__ == "__main__":
    show_openai_embedding_models()
    main()