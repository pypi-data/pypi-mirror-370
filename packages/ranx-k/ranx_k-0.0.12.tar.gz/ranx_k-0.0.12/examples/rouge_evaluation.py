#!/usr/bin/env python3
"""
ranx-k ROUGE Evaluation Example

이 예제는 다양한 ROUGE 평가 방법을 보여줍니다.
"""

from ranx_k.evaluation import simple_kiwi_rouge_evaluation, rouge_kiwi_enhanced_evaluation
import time

class MockRetriever:
    """Example virtual retriever"""
    
    def __init__(self):
        # Virtual document collection
        self.documents = [
            "자연어처리는 컴퓨터가 인간의 언어를 이해하고 처리하는 인공지능 기술입니다.",
            "RAG 시스템은 검색 증강 생성으로 문서 검색과 텍스트 생성을 결합합니다.",
            "한국어 토큰화는 교착어적 특성으로 인해 영어보다 복잡한 과정을 거칩니다.",
            "정보 검색 평가는 정확도와 재현율을 기반으로 시스템 성능을 측정합니다.",
            "Kiwi는 한국어 형태소 분석에 특화된 오픈소스 라이브러리입니다.",
            "머신러닝 모델의 성능 평가에는 다양한 메트릭이 사용됩니다.",
            "딥러닝 기반 언어 모델은 대량의 텍스트 데이터로 훈련됩니다.",
            "검색 시스템의 효율성은 응답 시간과 정확도로 판단됩니다.",
            "텍스트 마이닝 기술은 비구조화된 데이터에서 의미있는 정보를 추출합니다.",
            "인공지능 모델의 해석 가능성은 실제 응용에서 중요한 요소입니다."
        ]
    
    def invoke(self, query):
        """쿼리와 가장 유사한 문서들을 반환"""
        # 간단한 키워드 기반 검색 시뮬레이션
        class Document:
            def __init__(self, content):
                self.page_content = content
        
        # 쿼리의 키워드를 기반으로 관련 문서 찾기
        query_words = set(query.split())
        scored_docs = []
        
        for doc in self.documents:
            doc_words = set(doc.split())
            overlap = len(query_words & doc_words)
            if overlap > 0:
                scored_docs.append((overlap, Document(doc)))
        
        # Sort by score하고 Document 객체만 반환
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs]

def main():
    print("📊 ranx-k ROUGE Evaluation Example | ranx-k ROUGE 평가 예제")
    print("=" * 50)
    
    # 검색기 초기화
    retriever = MockRetriever()
    
    # 평가 데이터 준비
    questions = [
        "자연어처리란 무엇인가요?",
        "RAG 시스템의 작동 원리는?",
        "한국어 토큰화의 특징은?",
        "정보 검색 평가 방법은?",
        "Kiwi 라이브러리의 특징은?"
    ]
    
    # Correct documents for each question
    reference_contexts = [
        ["자연어처리는 컴퓨터가 인간의 언어를 이해하고 처리하는 인공지능 기술입니다."],
        ["RAG 시스템은 검색 증강 생성으로 문서 검색과 텍스트 생성을 결합합니다."],
        ["한국어 토큰화는 교착어적 특성으로 인해 영어보다 복잡한 과정을 거칩니다."],
        ["정보 검색 평가는 정확도와 재현율을 기반으로 시스템 성능을 측정합니다."],
        ["Kiwi는 한국어 형태소 분석에 특화된 오픈소스 라이브러리입니다."]
    ]
    
    print(f"📋 Evaluation Data | 평가 데이터: {len(questions)}개 질문")
    print(f"📚 Document Collection | 문서 컬렉션: {len(retriever.documents)}개 문서")
    
    # 1. Simple Kiwi ROUGE evaluation
    print("\n1️⃣ Simple Kiwi ROUGE Evaluation | 간단한 Kiwi ROUGE 평가")
    print("-" * 30)
    
    start_time = time.time()
    simple_results = simple_kiwi_rouge_evaluation(
        retriever=retriever,
        questions=questions,
        reference_contexts=reference_contexts,
        k=5
    )
    simple_time = time.time() - start_time
    
    print(f"⏱️ Processing Time | 처리 시간: {simple_time:.2f}초")
    
    # 2. Enhanced ROUGE evaluation (morphs)
    print("\n2️⃣ Enhanced ROUGE Evaluation (morphs) | 향상된 ROUGE 평가 (morphs)")
    print("-" * 30)
    
    start_time = time.time()
    enhanced_morphs_results = rouge_kiwi_enhanced_evaluation(
        retriever=retriever,
        questions=questions,
        reference_contexts=reference_contexts,
        k=5,
        tokenize_method='morphs',
        use_stopwords=True
    )
    enhanced_morphs_time = time.time() - start_time
    
    print(f"⏱️ 처리 시간: {enhanced_morphs_time:.2f}초")
    
    # 3. Enhanced ROUGE evaluation (nouns)
    print("\n3️⃣ Enhanced ROUGE Evaluation (nouns) | 향상된 ROUGE 평가 (nouns)")
    print("-" * 30)
    
    start_time = time.time()
    enhanced_nouns_results = rouge_kiwi_enhanced_evaluation(
        retriever=retriever,
        questions=questions,
        reference_contexts=reference_contexts,
        k=5,
        tokenize_method='nouns',
        use_stopwords=True
    )
    enhanced_nouns_time = time.time() - start_time
    
    print(f"⏱️ Processing Time | 처리 시간: {enhanced_nouns_time:.2f}초")
    
    # 4. 결과 비교
    print("\n📊 Results Comparison | 결과 비교")
    print("=" * 50)
    
    methods = [
        ("Simple Kiwi ROUGE", simple_results, simple_time),
        ("Enhanced ROUGE (morphs)", enhanced_morphs_results, enhanced_morphs_time),
        ("Enhanced ROUGE (nouns)", enhanced_nouns_results, enhanced_nouns_time)
    ]
    
    print(f"{'Method | 방법':<25} {'ROUGE-1':<10} {'ROUGE-2':<10} {'ROUGE-L':<10} {'Time(s) | 시간(s)':<8}")
    print("-" * 70)
    
    for method_name, results, exec_time in methods:
        # 결과에서 ROUGE 점수 추출
        rouge1 = next((v for k, v in results.items() if 'rouge1' in k.lower()), 0.0)
        rouge2 = next((v for k, v in results.items() if 'rouge2' in k.lower()), 0.0)
        rougeL = next((v for k, v in results.items() if 'rougel' in k.lower()), 0.0)
        
        print(f"{method_name:<25} {rouge1:<10.3f} {rouge2:<10.3f} {rougeL:<10.3f} {exec_time:<8.2f}")
    
    # 5. 질문별 상세 분석
    print("\n🔍 Question-wise Search Result Analysis | 질문별 검색 결과 분석")
    print("=" * 50)
    
    for i, question in enumerate(questions[:3]):  # 처음 3개 질문만
        print(f"\nQuestion | 질문 {i+1}: {question}")
        retrieved_docs = retriever.invoke(question)[:3]  # 상위 3개
        reference = reference_contexts[i][0]
        
        print(f"Answer | 정답: {reference}")
        print("Search Results | 검색 결과:")
        for j, doc in enumerate(retrieved_docs, 1):
            print(f"  {j}. {doc.page_content}")
    
    # 6. 성능 최적화 팁 시연
    print("\n⚡ Performance Optimization Tips | 성능 최적화 팁")
    print("=" * 30)
    
    # 배치 크기별 Performance comparison
    batch_sizes = [1, 3, 5]
    
    for batch_size in batch_sizes:
        start_time = time.time()
        
        # 배치 단위로 처리 시뮬레이션
        for i in range(0, len(questions), batch_size):
            batch_questions = questions[i:i+batch_size]
            batch_contexts = reference_contexts[i:i+batch_size]
            
            if batch_questions:  # 배치가 비어있지 않은 경우만
                simple_kiwi_rouge_evaluation(
                    retriever=retriever,
                    questions=batch_questions,
                    reference_contexts=batch_contexts,
                    k=3  # k를 줄여서 속도 향상
                )
        
        batch_time = time.time() - start_time
        print(f"Batch Size | 배치 크기 {batch_size}: {batch_time:.2f}초")
    
    print("\n✅ ROUGE Evaluation Example Completed | ROUGE 평가 예제 완료!")
    print("\n💡 Next Steps | 다음 단계:")
    print("- ranx_evaluation.py: ranx metric evaluation | ranx 메트릭 평가")
    print("- comprehensive_comparison.py: comprehensive comparison | 종합 비교")

if __name__ == "__main__":
    main()