"""
Enhanced ROUGE evaluation using rouge_score library with Kiwi tokenizer.

This module integrates the proven rouge_score library with Kiwi tokenizer
to provide accurate Korean ROUGE evaluation while maintaining compatibility
with the original rouge_score interface.

Original rouge_score library: Copyright (c) 2022 The rouge_score Authors
Modified for Korean language support with Kiwi tokenizer integration.
"""

from typing import List, Dict
from tqdm import tqdm

try:
    from rouge_score import rouge_scorer
    ROUGE_SCORE_AVAILABLE = True
except ImportError:
    ROUGE_SCORE_AVAILABLE = False

from ..tokenizers import KiwiTokenizer


def rouge_kiwi_enhanced_evaluation(retriever, questions: List[str], 
                                  reference_contexts: List[List[str]], 
                                  k: int = 5,
                                  tokenize_method: str = 'morphs', 
                                  use_stopwords: bool = True) -> Dict[str, float]:
    """
    Enhanced ROUGE evaluation using rouge_score library with Kiwi tokenizer.
    
    This function leverages the proven rouge_score library while using
    Kiwi tokenizer for accurate Korean text processing. It provides
    all the robustness of the original library with Korean language optimization.
    
    Args:
        retriever: RAG retriever object with invoke() method.
        questions: List of questions to evaluate.
        reference_contexts: List of reference document lists for each question.
        k: Number of top retrieved documents to evaluate.
        tokenize_method: Kiwi tokenization method ('morphs' or 'nouns').
        use_stopwords: Whether to filter Korean stopwords.
        
    Returns:
        Dictionary containing enhanced ROUGE scores:
        - enhanced_rouge1@k: ROUGE-1 F1 score
        - enhanced_rouge2@k: ROUGE-2 F1 score
        - enhanced_rougeL@k: ROUGE-L F1 score
        
    Example:
        >>> from krag.evaluation import rouge_kiwi_enhanced_evaluation
        >>> results = rouge_kiwi_enhanced_evaluation(
        ...     retriever=my_retriever,
        ...     questions=["RAG 시스템이란?"],
        ...     reference_contexts=[["RAG는 검색 증강 생성..."]], 
        ...     k=5,
        ...     tokenize_method='morphs',
        ...     use_stopwords=True
        ... )
        >>> print(f"Enhanced ROUGE-1: {results['enhanced_rouge1@5']:.3f}")
        
    Raises:
        ImportError: If rouge_score or kiwipiepy is not installed.
    """
    if not ROUGE_SCORE_AVAILABLE:
        raise ImportError(
            "rouge_score is required. Install with: pip install rouge-score"
        )
    
    print(f"🚀 Starting Rouge Score + Kiwi Tokenizer Evaluation (method: {tokenize_method}) | Rouge Score + Kiwi 토크나이저 평가 시작")
    
    # Create Kiwi tokenizer
    kiwi_tokenizer = KiwiTokenizer(
        method=tokenize_method, 
        use_stopwords=use_stopwords
    )
    
    # Create RougeScorer with custom Kiwi tokenizer
    scorer = rouge_scorer.RougeScorer(
        ['rouge1', 'rouge2', 'rougeL'], 
        tokenizer=kiwi_tokenizer  # Key: Use custom tokenizer
    )
    
    rouge1_scores = []
    rouge2_scores = []
    rougeL_scores = []

    for i, (question, ref_docs) in tqdm(enumerate(zip(questions, reference_contexts)), 
                                       desc="Enhanced ROUGE Evaluation | 향상된 ROUGE 평가"):
        # Retrieve documents
        retrieved_docs = retriever.invoke(question)[:k]
        retrieved_texts = [doc.page_content for doc in retrieved_docs]
        
        # Calculate best ROUGE scores for each reference document
        question_scores = {'rouge1': [], 'rouge2': [], 'rougeL': []}
        
        for ref_doc in ref_docs:
            # Extract text from Document object or use string directly
            ref_text = ref_doc.page_content if hasattr(ref_doc, 'page_content') else ref_doc
            
            best_scores = {'rouge1': 0, 'rouge2': 0, 'rougeL': 0}
            
            for ret_doc in retrieved_texts:
                # Use original rouge_score library with Kiwi tokenizer
                scores = scorer.score(ref_text, ret_doc)
                
                for rouge_type in ['rouge1', 'rouge2', 'rougeL']:
                    f_score = scores[rouge_type].fmeasure
                    if f_score > best_scores[rouge_type]:
                        best_scores[rouge_type] = f_score
            
            for rouge_type in ['rouge1', 'rouge2', 'rougeL']:
                question_scores[rouge_type].append(best_scores[rouge_type])
        
        # Average scores for this question
        rouge1_scores.append(sum(question_scores['rouge1']) / len(question_scores['rouge1']))
        rouge2_scores.append(sum(question_scores['rouge2']) / len(question_scores['rouge2']))
        rougeL_scores.append(sum(question_scores['rougeL']) / len(question_scores['rougeL']))
    
    # Calculate final results
    results = {
        f'enhanced_rouge1@{k}': sum(rouge1_scores) / len(rouge1_scores),
        f'enhanced_rouge2@{k}': sum(rouge2_scores) / len(rouge2_scores),
        f'enhanced_rougeL@{k}': sum(rougeL_scores) / len(rougeL_scores),
    }

    print("\n📊 Enhanced ROUGE Evaluation Results | 향상된 ROUGE 평가 결과:")
    for metric, score in results.items():
        print(f"  {metric}: {score:.3f}")
    
    return results


def compare_tokenizers(retriever, questions: List[str], 
                      reference_contexts: List[List[str]], 
                      k: int = 5) -> Dict[str, Dict[str, float]]:
    """
    Compare different tokenization methods for ROUGE evaluation.
    
    This function compares the performance of different tokenizers:
    - Default rouge_score tokenizer (English-based)
    - Kiwi morpheme tokenizer
    - Kiwi noun tokenizer
    
    Args:
        retriever: RAG retriever object.
        questions: List of questions to evaluate.
        reference_contexts: List of reference document lists.
        k: Number of top documents to evaluate.
        
    Returns:
        Dictionary containing comparison results for each method.
        
    Example:
        >>> from krag.evaluation.enhanced_rouge import compare_tokenizers
        >>> comparison = compare_tokenizers(
        ...     retriever=my_retriever,
        ...     questions=questions,
        ...     reference_contexts=references,
        ...     k=5
        ... )
        >>> print("Tokenizer comparison completed!")
    """
    if not ROUGE_SCORE_AVAILABLE:
        raise ImportError(
            "rouge_score is required. Install with: pip install rouge-score"
        )
    
    print("🔍 Tokenizer Performance Comparison | 토크나이저 성능 비교")
    print("="*50)
    
    results = {}
    
    # 1. Default rouge_score tokenizer (English-based)
    print("\n1️⃣ Basic Rouge Score (English Tokenizer) | 기본 Rouge Score (영어 토크나이저)")
    basic_scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'])
    
    basic_rouge1, basic_rouge2, basic_rougeL = [], [], []
    
    for question, ref_docs in tqdm(zip(questions, reference_contexts), 
                                  desc="Basic Tokenizer Evaluation | 기본 토크나이저 평가"):
        retrieved_docs = retriever.invoke(question)[:k]
        retrieved_texts = [doc.page_content for doc in retrieved_docs]
        
        for ref_doc in ref_docs:
            ref_text = ref_doc.page_content if hasattr(ref_doc, 'page_content') else ref_doc
            
            for ret_doc in retrieved_texts:
                scores = basic_scorer.score(ref_text, ret_doc)
                basic_rouge1.append(scores['rouge1'].fmeasure)
                basic_rouge2.append(scores['rouge2'].fmeasure)
                basic_rougeL.append(scores['rougeL'].fmeasure)
    
    results['basic'] = {
        f'basic_rouge1@{k}': sum(basic_rouge1) / len(basic_rouge1) if basic_rouge1 else 0,
        f'basic_rouge2@{k}': sum(basic_rouge2) / len(basic_rouge2) if basic_rouge2 else 0,
        f'basic_rougeL@{k}': sum(basic_rougeL) / len(basic_rougeL) if basic_rougeL else 0,
    }
    
    print("📊 Basic Tokenizer Results | 기본 토크나이저 결과:")
    for metric, score in results['basic'].items():
        print(f"  {metric}: {score:.3f}")
    
    # 2. Kiwi morpheme tokenizer
    print("\n2️⃣ Kiwi Morpheme Tokenizer | Kiwi 형태소 토크나이저")
    results['kiwi_morphs'] = rouge_kiwi_enhanced_evaluation(
        retriever, questions, reference_contexts, k, 
        tokenize_method='morphs', use_stopwords=True
    )
    
    # 3. Kiwi noun tokenizer
    print("\n3️⃣ Kiwi Noun Tokenizer | Kiwi 명사 토크나이저")
    results['kiwi_nouns'] = rouge_kiwi_enhanced_evaluation(
        retriever, questions, reference_contexts, k, 
        tokenize_method='nouns', use_stopwords=True
    )
    
    # 4. Performance comparison summary
    print("\n🏆 Tokenizer Performance Comparison Results | 토크나이저 성능 비교 결과:")
    print("="*50)
    
    methods = {
        'Basic Tokenizer | 기본 토크나이저': results['basic'],
        'Kiwi Morphs | Kiwi 형태소': results['kiwi_morphs'],
        'Kiwi Nouns | Kiwi 명사': results['kiwi_nouns']
    }
    
    for rouge_type in ['rouge1', 'rouge2', 'rougeL']:
        print(f"\n🎯 {rouge_type.upper()} Comparison | {rouge_type.upper()} 비교:")
        best_score = 0
        best_method = ""
        
        for method_name, method_results in methods.items():
            # Find the appropriate key for this method and rouge type
            score = 0
            for key, value in method_results.items():
                if rouge_type in key.lower() and not key.endswith('_std'):
                    score = value
                    break
            
            improvement = ""
            if score > best_score:
                best_score = score
                best_method = method_name
                improvement = " 🥇"
            elif score > 0 and best_score > 0:
                improvement = f" (+{((score/best_score-1)*100):+.1f}%)"
            
            print(f"  {method_name:15s}: {score:.3f}{improvement}")
    
    return results
