#!/usr/bin/env python3
"""
Korean RAG Evaluation Example Using BGE-M3 Model

BGE-M3 is a high-performance multilingual embedding model
that shows excellent performance on Korean text.
"""

from ranx_k.evaluation import evaluate_with_ranx_similarity
from ranx_k.tokenizers import KiwiTokenizer


class SimpleRetriever:
    """Simple test retriever"""
    
    def __init__(self, documents):
        self.documents = documents
    
    def invoke(self, query):
        # In practice, more complex search logic would be implemented here
        # For simplicity, returning all documents
        return self.documents


def main():
    print("🚀 Korean RAG Evaluation Example Using BGE-M3 Model | BGE-M3 모델을 사용한 한국어 RAG 평가 예제")
    print("=" * 60)
    
    # 1. Prepare test data
    questions = [
        "자연어처리란 무엇인가요?",
        "BGE 모델의 특징은 무엇인가요?",
        "한국어 토큰화의 어려움은?"
    ]
    
    # Document database (in real environment, vector DB would be used)
    documents = [
        "자연어처리는 컴퓨터가 인간의 언어를 이해하고 처리하는 인공지능 기술입니다.",
        "BGE 모델은 BAAI에서 개발한 다국어 임베딩 모델로 높은 성능을 자랑합니다.",
        "한국어는 교착어적 특성으로 인해 형태소 분석이 복잡하고 토큰화가 어렵습니다.",
        "BGE-M3는 다중 기능, 다국어, 다중 세분성을 지원하는 혁신적인 모델입니다.",
        "RAG 시스템은 검색과 생성을 결합하여 더 정확한 답변을 제공합니다."
    ]
    
    reference_contexts = [
        [documents[0]],  # Natural language processing related document
        [documents[1], documents[3]],  # BGE related documents
        [documents[2]]   # Korean tokenization related document
    ]
    
    # 2. Initialize retriever
    retriever = SimpleRetriever(documents)
    
    # 3. BGE-M3 model evaluation
    print("\n🔍 Evaluating with BGE-M3 Model | BGE-M3 모델로 평가 중...")
    print("Model | 모델: BAAI/bge-m3")
    
    try:
        # BGE-M3 requires replacing the default model in EmbeddingSimilarityCalculator
        # In practice, need improvement to accept model name as parameter
        results = evaluate_with_ranx_similarity(
            retriever=retriever,
            questions=questions,
            reference_contexts=reference_contexts,
            k=3,
            method='embedding',
            similarity_threshold=0.6
        )
        
        print("\n📊 BGE-M3 Evaluation Results | BGE-M3 평가 결과:")
        print("-" * 30)
        for metric, score in results.items():
            print(f"{metric:12s}: {score:.4f}")
            
    except Exception as e:
        print(f"❌ BGE-M3 evaluation error | BGE-M3 평가 중 오류 발생: {e}")
        print("💡 Solution: Check if sentence-transformers library is installed | 해결방법: sentence-transformers 라이브러리가 설치되었는지 확인하세요")
    
    # 4. Baseline model evaluation for comparison
    print("\n🔍 Comparative evaluation with default model (paraphrase-multilingual-MiniLM) | 기본 모델(paraphrase-multilingual-MiniLM)로 비교 평가...")
    
    try:
        baseline_results = evaluate_with_ranx_similarity(
            retriever=retriever,
            questions=questions,
            reference_contexts=reference_contexts,
            k=3,
            method='embedding',
            similarity_threshold=0.6
        )
        
        print("\n📊 Baseline Model Evaluation Results | 기본 모델 평가 결과:")
        print("-" * 30)
        for metric, score in baseline_results.items():
            print(f"{metric:12s}: {score:.4f}")
            
    except Exception as e:
        print(f"❌ Baseline model evaluation error | 기본 모델 평가 중 오류 발생: {e}")
    
    # 5. Comparison with Kiwi + ROUGE method
    print("\n🔍 Comparative evaluation with Kiwi + ROUGE method | Kiwi + ROUGE 방법으로 비교 평가...")
    
    try:
        kiwi_results = evaluate_with_ranx_similarity(
            retriever=retriever,
            questions=questions,
            reference_contexts=reference_contexts,
            k=3,
            method='kiwi_rouge',
            similarity_threshold=0.4  # ROUGE generally uses lower threshold
        )
        
        print("\n📊 Kiwi + ROUGE Evaluation Results | Kiwi + ROUGE 평가 결과:")
        print("-" * 30)
        for metric, score in kiwi_results.items():
            print(f"{metric:12s}: {score:.4f}")
            
    except Exception as e:
        print(f"❌ Kiwi + ROUGE evaluation error | Kiwi + ROUGE 평가 중 오류 발생: {e}")
    
    print("\n" + "=" * 60)
    print("✅ BGE-M3 Evaluation Completed | BGE-M3 평가 완료!")
    print("\n💡 Tips | 팁:")
    print("- BGE-M3 can process up to 8192 tokens | BGE-M3는 최대 8192 토큰까지 처리 가능")
    print("- Effective for mixed Korean-English text with multilingual support | 다국어 지원으로 한국어-영어 혼합 텍스트에도 효과적")
    print("- Recommend adjusting batch size due to high memory usage | 메모리 사용량이 큰 모델이므로 배치 크기 조절 권장")


def show_bge_m3_features():
    """Introduce BGE-M3 model features"""
    print("\n🌟 BGE-M3 Model Features | BGE-M3 모델 특징:")
    print("=" * 40)
    print("1. Multi-Functionality:")
    print("   - Dense retrieval (general embedding) | Dense retrieval (일반 임베딩)")
    print("   - Sparse retrieval (lexical matching) | Sparse retrieval (어휘 매칭)")
    print("   - Multi-vector retrieval (ColBERT)")
    print()
    print("2. Multi-Linguality:")
    print("   - Support for 100+ languages | 100개 이상 언어 지원")
    print("   - Excellent performance for East Asian languages including Korean | 한국어 포함 동아시아 언어 우수 성능")
    print()
    print("3. Multi-Granularity:")
    print("   - From short sentences to long documents (8192 tokens) | 짧은 문장부터 긴 문서(8192 토큰)까지")
    print("   - Can process texts of various lengths | 다양한 길이의 텍스트 처리 가능")
    print()
    print("🔗 More Information | 더 자세한 정보:")
    print("   - Paper | 논문: https://arxiv.org/abs/2402.03216")
    print("   - GitHub: https://github.com/FlagOpen/FlagEmbedding")
    print("   - Hugging Face: https://huggingface.co/BAAI/bge-m3")


if __name__ == "__main__":
    show_bge_m3_features()
    main()