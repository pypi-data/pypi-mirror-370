#!/usr/bin/env python3

"""
Example: Comparing Different Embedding Models for RAG Evaluation

This example demonstrates how to use different embedding models 
for similarity-based ranx evaluation in Korean RAG systems.
"""

import warnings
warnings.filterwarnings("ignore", message=".*encoder_attention_mask.*")

from ranx_k.evaluation.similarity_ranx import evaluate_with_ranx_similarity

def compare_embedding_models(retriever, questions, reference_contexts, k=5):
    """
    Compare different embedding models for RAG evaluation.
    
    Args:
        retriever: RAG retriever object
        questions: List of evaluation questions
        reference_contexts: List of reference document lists
        k: Number of top documents to evaluate
    
    Returns:
        dict: Comparison results for different models
    """
    
    print("🔍 Embedding Models Comparison for RAG Evaluation | 임베딩 모델 비교 평가")
    print("="*80)
    
    # Define embedding models to compare
    embedding_models = {
        "MiniLM-L12-v2": {
            "model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            "threshold": 0.6,
            "description": "Fast and lightweight multilingual model | 빠르고 가벼운 다국어 모델"
        },
        "OpenAI-3-Small": {
            "model": "text-embedding-3-small",
            "method": "openai",
            "threshold": 0.7,
            "description": "OpenAI embedding model (requires API key) | OpenAI 임베딩 모델 (API 키 필요)"
        },
        "BGE-M3": {
            "model": "BAAI/bge-m3",
            "threshold": 0.6,
            "description": "Latest multilingual embedding model | 최신 다국어 임베딩 모델"
        },
        "All-MPNet-Base-v2": {
            "model": "sentence-transformers/all-mpnet-base-v2",
            "threshold": 0.7,
            "description": "High-quality English model | 고품질 영어 모델"
        }
    }
    
    all_results = {}
    
    for model_name, config in embedding_models.items():
        print(f"\n🚀 Testing {model_name} | {model_name} 테스트 중...")
        print(f"📝 {config['description']}")
        print(f"🎯 Model: {config['model']}")
        print(f"🎯 Threshold: {config['threshold']}")
        print("-" * 60)
        
        try:
            method = config.get('method', 'embedding')
            results = evaluate_with_ranx_similarity(
                retriever=retriever,
                questions=questions,
                reference_contexts=reference_contexts,
                k=k,
                method=method,
                similarity_threshold=config['threshold'],
                embedding_model=config['model']
            )
            
            if results:
                all_results[model_name] = results
                print(f"✅ {model_name} evaluation completed | {model_name} 평가 완료")
            else:
                print(f"❌ {model_name} evaluation failed | {model_name} 평가 실패")
                
        except Exception as e:
            print(f"❌ Error with {model_name}: {e}")
            print(f"💡 Try installing model: pip install sentence-transformers")
    
    # Results comparison
    if all_results:
        print("\n🏆 Embedding Models Performance Comparison | 임베딩 모델 성능 비교")
        print("="*80)
        
        # Create comparison table
        metrics = ['hit_rate@5', 'ndcg@5', 'map@5', 'mrr']
        
        # Header
        print(f"{'Model':<20} {'Hit@5':<10} {'NDCG@5':<10} {'MAP@5':<10} {'MRR':<10}")
        print("-" * 70)
        
        # Results for each model
        for model_name, results in all_results.items():
            row = f"{model_name:<20}"
            for metric in metrics:
                if metric in results:
                    row += f"{results[metric]:<10.3f}"
                else:
                    row += f"{'N/A':<10}"
            print(row)
        
        # Find best model
        best_model = None
        best_score = 0
        
        for model_name, results in all_results.items():
            if 'hit_rate@5' in results and results['hit_rate@5'] > best_score:
                best_score = results['hit_rate@5']
                best_model = model_name
        
        if best_model:
            print(f"\n🥇 Best Model | 최고 모델: {best_model} (Hit@5: {best_score:.3f})")
    
    return all_results

def example_with_korean_text():
    """
    Example with Korean text data for demonstration.
    """
    print("\n🔍 Korean Text Example | 한국어 텍스트 예제")
    print("="*50)
    
    # Sample Korean RAG data
    questions = [
        "Tesla는 어떤 회사인가요?",
        "전기차의 주요 장점은 무엇인가요?",
        "자율주행 기술의 현재 수준은?",
    ]
    
    # Sample reference contexts (what should be retrieved)
    reference_contexts = [
        ["Tesla는 미국의 전기자동차 및 청정에너지 회사입니다."],
        ["전기차는 환경친화적이고 연료비가 절약되는 장점이 있습니다."],
        ["자율주행 기술은 레벨 2-3 수준에서 상용화되고 있습니다."],
    ]
    
    # Mock retriever for demonstration (replace with your actual retriever)
    class MockRetriever:
        def invoke(self, question):
            # Mock retrieved documents
            from types import SimpleNamespace
            docs = [
                SimpleNamespace(page_content="Tesla는 전기자동차를 만드는 미국 회사입니다."),
                SimpleNamespace(page_content="전기차는 배터리로 구동되는 친환경 차량입니다."),
                SimpleNamespace(page_content="자율주행은 AI 기술을 활용한 운전 보조 시스템입니다."),
                SimpleNamespace(page_content="전혀 관련없는 내용입니다."),
                SimpleNamespace(page_content="다른 주제에 대한 문서입니다."),
            ]
            return docs
    
    mock_retriever = MockRetriever()
    
    # Convert reference contexts to Document objects
    from types import SimpleNamespace
    formatted_references = []
    for ref_list in reference_contexts:
        docs = [SimpleNamespace(page_content=ref) for ref in ref_list]
        formatted_references.append(docs)
    
    # Test with different embedding models
    print("Testing different embedding models with Korean text...")
    
    results = evaluate_with_ranx_similarity(
        retriever=mock_retriever,
        questions=questions,
        reference_contexts=formatted_references,
        k=5,
        method='embedding',
        similarity_threshold=0.5,
        embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    
    print(f"📊 Results | 결과:")
    for metric, score in results.items():
        print(f"  {metric}: {score:.3f}")

if __name__ == "__main__":
    print("🚀 Embedding Models Comparison Example | 임베딩 모델 비교 예제")
    print("="*80)
    
    # Run Korean text example
    example_with_korean_text()
    
    print(f"\n💡 Usage Tips | 사용 팁:")
    print(f"  - Use higher thresholds (0.6-0.8) for more accurate models")
    print(f"  - BGE-M3 works well for Korean and multilingual content")
    print(f"  - MPNet models provide good balance of accuracy and speed")
    print(f"  - 더 정확한 모델에는 높은 임계값(0.6-0.8)을 사용하세요")
    print(f"  - BGE-M3는 한국어와 다국어 콘텐츠에 적합합니다")
    print(f"  - MPNet 모델은 정확도와 속도의 좋은 균형을 제공합니다")