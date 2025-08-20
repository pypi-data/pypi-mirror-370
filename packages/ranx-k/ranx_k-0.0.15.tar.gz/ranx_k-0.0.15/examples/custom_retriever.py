#!/usr/bin/env python3
"""
ranx-k Custom Retriever Implementation Example

This example demonstrates how to implement custom retrievers compatible with ranx-k.
"""

import numpy as np
from typing import List, Any
from ranx_k.tokenizers import KiwiTokenizer
from ranx_k.evaluation import simple_kiwi_rouge_evaluation

class Document:
    """Document class"""
    def __init__(self, content: str, metadata: dict = None):
        self.page_content = content
        self.metadata = metadata or {}

class SimpleVectorRetriever:
    """Simple vector-based retriever"""
    
    def __init__(self, documents: List[str]):
        self.documents = [Document(doc) for doc in documents]
        self.tokenizer = KiwiTokenizer(method='morphs', use_stopwords=True)
        self.vocab = self._build_vocabulary()
        self.doc_vectors = self._vectorize_documents()
    
    def _build_vocabulary(self):
        """Build vocabulary from all documents"""
        vocab = set()
        for doc in self.documents:
            tokens = self.tokenizer.tokenize(doc.page_content)
            vocab.update(tokens)
        return {word: i for i, word in enumerate(sorted(vocab))}
    
    def _vectorize_documents(self):
        """Convert documents to vectors"""
        vectors = []
        for doc in self.documents:
            vector = self._text_to_vector(doc.page_content)
            vectors.append(vector)
        return np.array(vectors)
    
    def _text_to_vector(self, text: str):
        """Convert text to TF vector"""
        tokens = self.tokenizer.tokenize(text)
        vector = np.zeros(len(self.vocab))
        
        for token in tokens:
            if token in self.vocab:
                vector[self.vocab[token]] += 1
        
        # L2 normalization
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector
    
    def invoke(self, query: str, top_k: int = 10) -> List[Document]:
        """Search for relevant documents for query"""
        query_vector = self._text_to_vector(query)
        
        # Calculate cosine similarity
        similarities = np.dot(self.doc_vectors, query_vector)
        
        # Select top k documents
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        return [self.documents[i] for i in top_indices if similarities[i] > 0]

class KeywordRetriever:
    """Keyword-based retriever"""
    
    def __init__(self, documents: List[str]):
        self.documents = [Document(doc) for doc in documents]
        self.tokenizer = KiwiTokenizer(method='morphs', use_stopwords=True)
    
    def invoke(self, query: str, top_k: int = 10) -> List[Document]:
        """Keyword matching based search"""
        query_tokens = set(self.tokenizer.tokenize(query))
        
        scored_docs = []
        for doc in self.documents:
            doc_tokens = set(self.tokenizer.tokenize(doc.page_content))
            
            # Calculate intersection-based score
            overlap = len(query_tokens & doc_tokens)
            if overlap > 0:
                # Jaccard similarity
                union = len(query_tokens | doc_tokens)
                score = overlap / union
                scored_docs.append((score, doc))
        
        # Sort by score
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        return [doc for score, doc in scored_docs[:top_k]]

class HybridRetriever:
    """Vector + Keyword Hybrid retriever"""
    
    def __init__(self, documents: List[str], vector_weight: float = 0.7):
        self.vector_retriever = SimpleVectorRetriever(documents)
        self.keyword_retriever = KeywordRetriever(documents)
        self.vector_weight = vector_weight
        self.keyword_weight = 1.0 - vector_weight
    
    def invoke(self, query: str, top_k: int = 10) -> List[Document]:
        """Perform hybrid search"""
        # Get results from each retriever
        vector_results = self.vector_retriever.invoke(query, top_k * 2)
        keyword_results = self.keyword_retriever.invoke(query, top_k * 2)
        
        # Aggregate scores by document
        doc_scores = {}
        
        # Vector search scores
        for i, doc in enumerate(vector_results):
            score = (len(vector_results) - i) / len(vector_results)  # Rank-based score
            doc_scores[doc.page_content] = doc_scores.get(doc.page_content, 0) + \
                                         score * self.vector_weight
        
        # Keyword search scores
        for i, doc in enumerate(keyword_results):
            score = (len(keyword_results) - i) / len(keyword_results)
            doc_scores[doc.page_content] = doc_scores.get(doc.page_content, 0) + \
                                         score * self.keyword_weight
        
        # Sort by score
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return Document objects
        result_docs = []
        doc_map = {doc.page_content: doc for doc in 
                  self.vector_retriever.documents}
        
        for content, score in sorted_docs[:top_k]:
            if content in doc_map:
                result_docs.append(doc_map[content])
        
        return result_docs

def main():
    print("🔍 ranx-k Custom Retriever Example | ranx-k 커스텀 검색기 예제")
    print("=" * 50)
    
    # Sample document collection
    documents = [
        "자연어처리는 컴퓨터가 인간의 언어를 이해하고 처리하는 인공지능 기술입니다.",
        "RAG 시스템은 검색 증강 생성 기술로 정보 검색과 텍스트 생성을 결합합니다.",
        "한국어 토큰화는 교착어적 특성 때문에 형태소 분석이 중요합니다.",
        "정보 검색 시스템의 성능은 정밀도와 재현율로 평가됩니다.",
        "Kiwi는 한국어 형태소 분석에 특화된 오픈소스 라이브러리입니다.",
        "머신러닝 모델 훈련에는 대량의 라벨링된 데이터가 필요합니다.",
        "딥러닝 기반 언어 모델은 트랜스포머 아키텍처를 사용합니다.",
        "검색 엔진 최적화는 웹사이트 가시성을 향상시키는 기법입니다.",
        "텍스트 마이닝은 비구조화된 텍스트에서 유용한 정보를 추출합니다.",
        "추천 시스템은 사용자 선호도를 학습하여 개인화된 콘텐츠를 제공합니다.",
        "컴퓨터 비전 기술은 이미지와 영상을 분석하고 이해합니다.",
        "데이터 전처리는 머신러닝 파이프라인에서 중요한 단계입니다."
    ]
    
    print(f"📚 Document Collection | 문서 컬렉션: {len(documents)}개 문서")
    
    # Initialize various retrievers
    vector_retriever = SimpleVectorRetriever(documents)
    keyword_retriever = KeywordRetriever(documents)
    hybrid_retriever = HybridRetriever(documents, vector_weight=0.6)
    
    # Test queries
    test_queries = [
        "자연어처리 기술은 무엇인가요?",
        "RAG 시스템의 특징을 알려주세요",
        "한국어 토큰화 방법은?",
        "머신러닝 모델 훈련 과정은?"
    ]
    
    print(f"🔍 Test Queries | 테스트 쿼리: {len(test_queries)}개")
    
    # 1. Compare results by retriever type
    print("\n1️⃣ Results Comparison by Retriever Type | 검색기별 결과 비교")
    print("-" * 50)
    
    for i, query in enumerate(test_queries[:2]):  # First 2 queries only
        print(f"\nQuery | 쿼리 {i+1}: {query}")
        print("=" * 40)
        
        # Vector search
        vector_results = vector_retriever.invoke(query, 3)
        print(f"\n🔢 Vector Search | 벡터 검색 ({len(vector_results)}개):")
        for j, doc in enumerate(vector_results, 1):
            print(f"  {j}. {doc.page_content[:50]}...")
        
        # Keyword search
        keyword_results = keyword_retriever.invoke(query, 3)
        print(f"\n🔤 Keyword Search | 키워드 검색 ({len(keyword_results)}개):")
        for j, doc in enumerate(keyword_results, 1):
            print(f"  {j}. {doc.page_content[:50]}...")
        
        # Hybrid search
        hybrid_results = hybrid_retriever.invoke(query, 3)
        print(f"\n🔀 Hybrid Search | 하이브리드 검색 ({len(hybrid_results)}개):")
        for j, doc in enumerate(hybrid_results, 1):
            print(f"  {j}. {doc.page_content[:50]}...")
    
    # 2. Performance evaluation
    print("\n2️⃣ Retriever Performance Evaluation | 검색기 성능 평가")
    print("-" * 30)
    
    # Prepare evaluation data
    eval_questions = [
        "자연어처리 기술이란?",
        "RAG 시스템 설명",
        "한국어 토큰화 특징",
        "정보 검색 평가 방법"
    ]
    
    eval_references = [
        ["자연어처리는 컴퓨터가 인간의 언어를 이해하고 처리하는 인공지능 기술입니다."],
        ["RAG 시스템은 검색 증강 생성 기술로 정보 검색과 텍스트 생성을 결합합니다."],
        ["한국어 토큰화는 교착어적 특성 때문에 형태소 분석이 중요합니다."],
        ["정보 검색 시스템의 성능은 정밀도와 재현율로 평가됩니다."]
    ]
    
    retrievers = [
        ("Vector Retriever | 벡터 검색기", vector_retriever),
        ("Keyword Retriever | 키워드 검색기", keyword_retriever),  
        ("Hybrid Retriever | 하이브리드 검색기", hybrid_retriever)
    ]
    
    print(f"{'검색기':<15} {'ROUGE-1':<10} {'ROUGE-2':<10} {'ROUGE-L':<10}")
    print("-" * 50)
    
    for name, retriever in retrievers:
        try:
            results = simple_kiwi_rouge_evaluation(
                retriever=retriever,
                questions=eval_questions,
                reference_contexts=eval_references,
                k=3
            )
            
            rouge1 = results.get('kiwi_rouge1@3', 0.0)
            rouge2 = results.get('kiwi_rouge2@3', 0.0)
            rougeL = results.get('kiwi_rougeL@3', 0.0)
            
            print(f"{name:<15} {rouge1:<10.3f} {rouge2:<10.3f} {rougeL:<10.3f}")
            
        except Exception as e:
            print(f"{name:<15} Error | 오류: {str(e)}")
    
    # 3. 성능 분석
    print("\n3️⃣ Performance Characteristics Analysis | 성능 특성 분석")
    print("-" * 25)
    
    analysis_query = "머신러닝과 딥러닝의 차이점은?"
    
    print(f"Analysis Query | 분석 쿼리: {analysis_query}")
    print("\nRetriever Characteristics | 각 검색기의 특성:")
    
    # Vector retriever analysis
    vector_results = vector_retriever.invoke(analysis_query, 5)
    print(f"\n🔢 Vector Retriever | 벡터 검색기:")
    print(f"  - Semantic similarity-based | 의미적 유사도 기반")
    print(f"  - Search results | 검색 결과: {len(vector_results)}개")
    print(f"  - Advantages: Synonyms and similar concept search | 장점: 동의어, 유사 개념 검색 가능")
    
    # Keyword retriever analysis
    keyword_results = keyword_retriever.invoke(analysis_query, 5)
    print(f"\n🔤 Keyword Retriever | 키워드 검색기:")
    print(f"  - Exact keyword matching | 정확한 키워드 매칭")
    print(f"  - Search results | 검색 결과: {len(keyword_results)}개")
    print(f"  - Advantages: Fast speed, exact matching | 장점: 빠른 속도, 정확한 매칭")
    
    # Hybrid retriever analysis
    hybrid_results = hybrid_retriever.invoke(analysis_query, 5)
    print(f"\n🔀 Hybrid Retriever | 하이브리드 검색기:")
    print(f"  - Vector + Keyword combination | 벡터 + 키워드 결합")
    print(f"  - Search results | 검색 결과: {len(hybrid_results)}개")
    print(f"  - Advantages: Combines benefits of both approaches | 장점: 두 방식의 장점 결합")
    
    print("\n✅ Custom Retriever Example Completed | 커스텀 검색기 예제 완료!")
    print("\n💡 Implementation Guide | 구현 가이드:")
    print("1. Just implement invoke(query) method for ranx-k compatibility | invoke(query) 메서드만 구현하면 ranx-k와 호환")
    print("2. Document object needs page_content attribute | Document 객체의 page_content 속성 필요")
    print("3. Various search algorithm combinations possible | 다양한 검색 알고리즘 조합 가능")

if __name__ == "__main__":
    main()