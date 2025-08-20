#!/usr/bin/env python3
"""
ranx-k Comprehensive Evaluation Comparison Example

이 예제는 Comprehensively compares and analyzes all evaluation methods.
"""

import time
import numpy as np
from typing import List, Dict, Any
from ranx_k.evaluation import (
    simple_kiwi_rouge_evaluation,
    rouge_kiwi_enhanced_evaluation,
    evaluate_with_ranx_similarity,
    comprehensive_evaluation_comparison
)
from ranx_k.tokenizers import KiwiTokenizer

class Document:
    def __init__(self, content: str, doc_id: str = None):
        self.page_content = content
        self.doc_id = doc_id or str(hash(content))

class ComprehensiveRetriever:
    """Advanced retriever for comprehensive evaluation"""
    
    def __init__(self, documents: List[str]):
        self.documents = [Document(doc, f"doc_{i}") for i, doc in enumerate(documents)]
        self.tokenizer = KiwiTokenizer(method='morphs', use_stopwords=True)
        
    def invoke(self, query: str, top_k: int = 10) -> List[Document]:
        """TF-IDF based search"""
        query_tokens = self.tokenizer.tokenize(query)
        
        # Calculate relevance score for each document
        doc_scores = []
        
        for doc in self.documents:
            doc_tokens = self.tokenizer.tokenize(doc.page_content)
            
            # Simple TF-IDF score calculation
            score = 0
            for token in query_tokens:
                if token in doc_tokens:
                    tf = doc_tokens.count(token) / len(doc_tokens)
                    score += tf
            
            if score > 0:
                doc_scores.append((score, doc))
        
        # Sort by score
        doc_scores.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in doc_scores[:top_k]]

def create_evaluation_dataset():
    """Create evaluation dataset"""
    
    # Domain-specific document collection
    documents = [
        # Natural language processing related
        "자연어처리는 컴퓨터가 인간의 언어를 이해하고 생성하는 인공지능 기술 분야입니다.",
        "형태소 분석은 한국어 자연어처리의 핵심 기술로 단어를 의미 단위로 분해합니다.",
        "토큰화 과정에서 한국어의 교착어적 특성을 고려해야 정확한 분석이 가능합니다.",
        
        # RAG system related  
        "RAG는 Retrieval-Augmented Generation의 줄임말로 검색과 생성을 결합한 기술입니다.",
        "검색 증강 생성 시스템은 관련 문서를 찾아 더 정확한 답변을 생성합니다.",
        "RAG 시스템의 성능은 검색 품질과 생성 품질에 모두 의존합니다.",
        
        # Information retrieval related
        "정보 검색 시스템의 성능은 정밀도, 재현율, F1 점수로 평가됩니다.",
        "검색 엔진은 사용자 쿼리에 맞는 관련 문서를 빠르게 찾아 제공합니다.",
        "벡터 검색은 의미적 유사도를 기반으로 문서를 검색하는 방법입니다.",
        
        # Evaluation metrics related
        "ROUGE 메트릭은 요약문의 품질을 평가하는 대표적인 자동 평가 방법입니다.",
        "NDCG는 검색 결과의 순위 품질을 측정하는 정보 검색 평가 지표입니다.",
        "Hit@K는 상위 K개 결과 중 정답이 포함된 비율을 나타내는 메트릭입니다.",
        
        # Machine learning related
        "머신러닝 모델의 성능 평가에는 다양한 메트릭과 검증 방법이 사용됩니다.",
        "교차 검증은 모델의 일반화 성능을 평가하는 신뢰할 수 있는 방법입니다.",
        "과적합을 방지하기 위해 정규화 기법과 조기 종료를 활용합니다.",
        
        # Deep learning related
        "트랜스포머 아키텍처는 자연어처리 분야에 혁신을 가져온 신경망 구조입니다.",
        "어텐션 메커니즘은 입력 시퀀스의 중요한 부분에 집중할 수 있게 해줍니다.",
        "사전 훈련된 언어 모델은 다양한 하위 작업에 파인튜닝하여 사용할 수 있습니다."
    ]
    
    # Question-answer pairs for evaluation
    questions = [
        "자연어처리란 무엇인가요?",
        "한국어 토큰화의 특징은?", 
        "RAG 시스템은 어떻게 작동하나요?",
        "정보 검색 성능 평가 방법은?",
        "ROUGE 메트릭의 특징은?",
        "머신러닝 모델 평가 방법은?",
        "트랜스포머의 특징은?",
        "검색 엔진의 역할은?"
    ]
    
    # Correct documents for each question
    reference_contexts = [
        ["자연어처리는 컴퓨터가 인간의 언어를 이해하고 생성하는 인공지능 기술 분야입니다."],
        ["토큰화 과정에서 한국어의 교착어적 특성을 고려해야 정확한 분석이 가능합니다."],
        ["RAG는 Retrieval-Augmented Generation의 줄임말로 검색과 생성을 결합한 기술입니다."],
        ["정보 검색 시스템의 성능은 정밀도, 재현율, F1 점수로 평가됩니다."],
        ["ROUGE 메트릭은 요약문의 품질을 평가하는 대표적인 자동 평가 방법입니다."],
        ["머신러닝 모델의 성능 평가에는 다양한 메트릭과 검증 방법이 사용됩니다."],
        ["트랜스포머 아키텍처는 자연어처리 분야에 혁신을 가져온 신경망 구조입니다."],
        ["검색 엔진은 사용자 쿼리에 맞는 관련 문서를 빠르게 찾아 제공합니다."]
    ]
    
    return documents, questions, reference_contexts

def detailed_performance_analysis(results: Dict[str, Any]):
    """Detailed performance analysis"""
    
    analysis = {
        'rouge_scores': {},
        'ranx_metrics': {},
        'overall_performance': {}
    }
    
    # Extract ROUGE scores
    for method, metrics in results.items():
        rouge_scores = {}
        ranx_scores = {}
        
        for metric_name, score in metrics.items():
            if 'rouge' in metric_name.lower():
                rouge_type = 'rouge1' if 'rouge1' in metric_name.lower() else \
                           'rouge2' if 'rouge2' in metric_name.lower() else \
                           'rougeL' if 'rougel' in metric_name.lower() else 'other'
                rouge_scores[rouge_type] = score
            
            elif any(x in metric_name.lower() for x in ['hit_rate', 'ndcg', 'map', 'mrr']):
                ranx_scores[metric_name] = score
        
        if rouge_scores:
            analysis['rouge_scores'][method] = rouge_scores
        if ranx_scores:
            analysis['ranx_metrics'][method] = ranx_scores
    
    return analysis

def generate_recommendations(analysis: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on result analysis"""
    
    recommendations = []
    
    # ROUGE score-based recommendations
    if 'rouge_scores' in analysis:
        best_rouge_method = None
        best_rouge_score = 0
        
        for method, scores in analysis['rouge_scores'].items():
            avg_score = np.mean(list(scores.values()))
            if avg_score > best_rouge_score:
                best_rouge_score = avg_score
                best_rouge_method = method
        
        if best_rouge_method:
            if best_rouge_score > 0.6:
                recommendations.append(f"✅ {best_rouge_method} shows the highest ROUGE performance ({best_rouge_score:.3f}).")
            elif best_rouge_score > 0.4:
                recommendations.append(f"⚠️ {best_rouge_method} is relatively good ({best_rouge_score:.3f}), but has room for improvement.")
            else:
                recommendations.append(f"🔴 All methods have low ROUGE scores. System review is required.")
    
    # ranx metric-based recommendations
    if 'ranx_metrics' in analysis:
        recommendations.append("📊 Traditional IR evaluation through ranx metrics is available.")
    
    # General recommendations
    recommendations.extend([
        "🔧 Experiment with tokenization methods (morphs vs nouns).",
        "🎯 Optimize performance by adjusting similarity_threshold values.",
        "⚡ Consider batch processing for large datasets.",
        "📈 Make comprehensive judgments by combining multiple evaluation methods."
    ])
    
    return recommendations

def main():
    print("🏆 ranx-k Comprehensive Evaluation Comparison Example | ranx-k 종합 평가 비교 예제")
    print("=" * 60)
    
    # Prepare dataset
    print("📊 Preparing Evaluation Dataset | 평가 데이터셋 준비 중...")
    documents, questions, reference_contexts = create_evaluation_dataset()
    retriever = ComprehensiveRetriever(documents)
    
    print(f"📚 Number of Documents | 문서 수: {len(documents)}")
    print(f"❓ Number of Questions | 질문 수: {len(questions)}")
    print(f"📝 Answer Pairs | 정답 쌍: {len(reference_contexts)}")
    
    # 1. Execute individual evaluation methods
    print("\n1️⃣ Individual Evaluation Methods Execution | 개별 평가 방법 실행")
    print("-" * 40)
    
    evaluation_results = {}
    execution_times = {}
    
    # Simple Kiwi ROUGE
    print("🔤 Simple Kiwi ROUGE Evaluation | Simple Kiwi ROUGE 평가...")
    start_time = time.time()
    try:
        simple_results = simple_kiwi_rouge_evaluation(
            retriever=retriever,
            questions=questions,
            reference_contexts=reference_contexts,
            k=5
        )
        evaluation_results['Simple Kiwi ROUGE'] = simple_results
        execution_times['Simple Kiwi ROUGE'] = time.time() - start_time
        print(f"   ✅ Completed | 완료 ({execution_times['Simple Kiwi ROUGE']:.2f}초)")
    except Exception as e:
        print(f"   ❌ Error | 오류: {str(e)}")
    
    # Enhanced ROUGE (morphs)
    print("🔬 Enhanced ROUGE (morphs) Evaluation | Enhanced ROUGE (morphs) 평가...")
    start_time = time.time()
    try:
        enhanced_results = rouge_kiwi_enhanced_evaluation(
            retriever=retriever,
            questions=questions,
            reference_contexts=reference_contexts,
            k=5,
            tokenize_method='morphs'
        )
        evaluation_results['Enhanced ROUGE (morphs)'] = enhanced_results
        execution_times['Enhanced ROUGE (morphs)'] = time.time() - start_time
        print(f"   ✅ Completed | 완료 ({execution_times['Enhanced ROUGE (morphs)']:.2f}초)")
    except Exception as e:
        print(f"   ❌ Error | 오류: {str(e)}")
    
    # Enhanced ROUGE (nouns)
    print("🔬 Enhanced ROUGE (nouns) Evaluation | Enhanced ROUGE (nouns) 평가...")
    start_time = time.time()
    try:
        enhanced_nouns_results = rouge_kiwi_enhanced_evaluation(
            retriever=retriever,
            questions=questions,
            reference_contexts=reference_contexts,
            k=5,
            tokenize_method='nouns'
        )
        evaluation_results['Enhanced ROUGE (nouns)'] = enhanced_nouns_results
        execution_times['Enhanced ROUGE (nouns)'] = time.time() - start_time
        print(f"   ✅ Completed | 완료 ({execution_times['Enhanced ROUGE (nouns)']:.2f}초)")
    except Exception as e:
        print(f"   ❌ Error | 오류: {str(e)}")
    
    # ranx Similarity (Kiwi ROUGE)
    print("📊 ranx Similarity (Kiwi ROUGE) Evaluation | ranx Similarity (Kiwi ROUGE) 평가...")
    start_time = time.time()
    try:
        ranx_results = evaluate_with_ranx_similarity(
            retriever=retriever,
            questions=questions,
            reference_contexts=reference_contexts,
            k=5,
            method='kiwi_rouge',
            similarity_threshold=0.5
        )
        evaluation_results['ranx Similarity (Kiwi ROUGE)'] = ranx_results
        execution_times['ranx Similarity (Kiwi ROUGE)'] = time.time() - start_time
        print(f"   ✅ Completed | 완료 ({execution_times['ranx Similarity (Kiwi ROUGE)']:.2f}초)")
    except Exception as e:
        print(f"   ❌ Error | 오류: {str(e)}")
    
    # 2. Execute comprehensive comparison
    print("\n2️⃣ Comprehensive Comparison Evaluation Execution | 종합 비교 평가 실행")
    print("-" * 30)
    
    start_time = time.time()
    try:
        comprehensive_results = comprehensive_evaluation_comparison(
            retriever=retriever,
            questions=questions,
            reference_contexts=reference_contexts,
            k=5
        )
        comprehensive_time = time.time() - start_time
        print(f"✅ Comprehensive Comparison Completed | 종합 비교 완료 ({comprehensive_time:.2f}초)")
    except Exception as e:
        print(f"❌ Comprehensive Comparison Error | 종합 비교 오류: {str(e)}")
        comprehensive_results = evaluation_results
    
    # 3. Comprehensive result analysis
    print("\n3️⃣ Comprehensive Result Analysis | 결과 종합 분석")
    print("=" * 40)
    
    # Performance comparison table
    print("\n📊 Performance Comparison Table | 성능 비교 테이블")
    print("-" * 80)
    print(f"{'Method | 방법':<25} {'ROUGE-1':<10} {'ROUGE-2':<10} {'ROUGE-L':<10} {'Time(s) | 실행시간(s)':<12}")
    print("-" * 80)
    
    for method_name in evaluation_results.keys():
        results = evaluation_results[method_name]
        exec_time = execution_times.get(method_name, 0)
        
        # Extract ROUGE scores
        rouge1 = next((v for k, v in results.items() if 'rouge1' in k.lower()), 0.0)
        rouge2 = next((v for k, v in results.items() if 'rouge2' in k.lower()), 0.0)
        rougeL = next((v for k, v in results.items() if 'rougel' in k.lower()), 0.0)
        
        print(f"{method_name:<25} {rouge1:<10.3f} {rouge2:<10.3f} {rougeL:<10.3f} {exec_time:<12.2f}")
    
    # ranx metrics table
    ranx_methods = [name for name in evaluation_results.keys() if 'ranx' in name.lower()]
    if ranx_methods:
        print(f"\n📈 ranx Metrics Comparison | ranx 메트릭 비교")
        print("-" * 60)
        print(f"{'Method | 방법':<25} {'Hit@5':<10} {'NDCG@5':<10} {'MRR':<10}")
        print("-" * 60)
        
        for method_name in ranx_methods:
            results = evaluation_results[method_name]
            hit_rate = results.get('hit_rate@5', 0.0)
            ndcg = results.get('ndcg@5', 0.0) 
            mrr = results.get('mrr', 0.0)
            
            print(f"{method_name:<25} {hit_rate:<10.3f} {ndcg:<10.3f} {mrr:<10.3f}")
    
    # 4. Detailed analysis
    print("\n4️⃣ Detailed Performance Analysis | 상세 성능 분석")
    print("-" * 25)
    
    analysis = detailed_performance_analysis(evaluation_results)
    
    # Identify best performance method
    if 'rouge_scores' in analysis and analysis['rouge_scores']:
        print("\n🏆 ROUGE Performance Rankings | ROUGE 성능 순위:")
        rouge_rankings = []
        
        for method, scores in analysis['rouge_scores'].items():
            avg_score = np.mean(list(scores.values()))
            rouge_rankings.append((method, avg_score))
        
        rouge_rankings.sort(key=lambda x: x[1], reverse=True)
        
        for i, (method, score) in enumerate(rouge_rankings, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📊"
            print(f"  {emoji} {i}위 | Rank {i}: {method:<25} ({score:.3f})")
    
    # 5. Generate recommendations
    print("\n5️⃣ Recommendations | 권장사항")
    print("-" * 15)
    
    recommendations = generate_recommendations(analysis)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i:2d}. {rec}")
    
    # 6. Use case-specific recommended methods
    print("\n6️⃣ Recommended Methods by Use Case | 사용 사례별 권장 방법")
    print("-" * 30)
    
    use_cases = [
        ("🚀 빠른 프로토타이핑", "Simple Kiwi ROUGE - 가장 빠르고 간단"),
        ("🏢 프로덕션 환경", "Enhanced ROUGE (morphs) - 안정적이고 검증된 방법"),
        ("🔬 연구/벤치마킹", "ranx Similarity - 전통적인 IR 메트릭 제공"),
        ("🎯 높은 정확도", "Enhanced ROUGE + ranx 조합 - 다각도 평가"),
        ("💾 메모리 제약", "Kiwi ROUGE (임베딩 미사용) - 메모리 효율적")
    ]
    
    for use_case, recommendation in use_cases:
        print(f"{use_case:<20} → {recommendation}")
    
    # 7. Performance optimization tips
    print("\n7️⃣ Performance Optimization Tips | 성능 최적화 팁")
    print("-" * 20)
    
    optimization_tips = [
        "🔧 토큰화 방법 선택: 정확도는 morphs, 속도는 nouns",
        "🎯 임계값 조정: similarity_threshold를 데이터에 맞게 튜닝",
        "⚡ 배치 처리: 대량 데이터는 배치 단위로 나누어 처리",
        "💾 캐싱 활용: 반복 실행 시 토큰화 결과 캐싱",
        "📊 k 값 최적화: 검색 깊이와 성능의 균형점 찾기"
    ]
    
    for tip in optimization_tips:
        print(f"  {tip}")
    
    print(f"\n✅ Comprehensive Evaluation Comparison Completed | 종합 평가 비교 완료!")
    print(f"📊 Total {len(evaluation_results)} methods evaluated {len(questions)} questions | 총 {len(evaluation_results)}개 방법으로 {len(questions)}개 질문 평가")
    print(f"⏱️ Total Execution Time | 총 실행 시간: {sum(execution_times.values()):.2f}초")

if __name__ == "__main__":
    main()