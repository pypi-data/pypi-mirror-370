"""
Simple Kiwi ROUGE evaluation for Korean RAG systems.

This module provides a streamlined ROUGE evaluation function that uses
Kiwi morphological analyzer for accurate Korean tokenization.

Based on concepts from rouge_score library with Korean language optimizations.
"""

import numpy as np
from collections import Counter
import re
from typing import List, Dict, Any
from tqdm import tqdm

try:
    from kiwipiepy import Kiwi
    KIWI_AVAILABLE = True
except ImportError:
    KIWI_AVAILABLE = False


def simple_kiwi_rouge_evaluation(retriever, questions: List[str], 
                                reference_contexts: List[List[str]], 
                                k: int = 5) -> Dict[str, float]:
    """
    Simple and fast Kiwi-based ROUGE evaluation for Korean RAG systems.
    
    This function provides a streamlined evaluation using Kiwi tokenizer
    for accurate Korean text processing. It calculates ROUGE-1, ROUGE-2,
    and ROUGE-L scores between retrieved documents and reference contexts.
    
    Args:
        retriever: RAG retriever object with invoke() method.
        questions: List of questions to evaluate.
        reference_contexts: List of reference document lists for each question.
        k: Number of top retrieved documents to evaluate.
        
    Returns:
        Dictionary containing ROUGE scores:
        - kiwi_rouge1@k: ROUGE-1 F1 score
        - kiwi_rouge2@k: ROUGE-2 F1 score  
        - kiwi_rougeL@k: ROUGE-L F1 score
        
    Example:
        >>> from krag.evaluation import simple_kiwi_rouge_evaluation
        >>> results = simple_kiwi_rouge_evaluation(
        ...     retriever=my_retriever,
        ...     questions=["RAG 시스템이란?"],
        ...     reference_contexts=[["RAG는 검색 증강 생성..."]], 
        ...     k=5
        ... )
        >>> print(f"ROUGE-1: {results['kiwi_rouge1@5']:.3f}")
        
    Raises:
        ImportError: If kiwipiepy is not installed.
    """
    if not KIWI_AVAILABLE:
        raise ImportError(
            "Kiwi is required for this evaluation. Install with: pip install kiwipiepy"
        )
    
    print(f"🔍 Starting Kiwi ROUGE evaluation | Kiwi ROUGE 평가 시작 (k={k})")
    
    # Initialize Kiwi
    kiwi = Kiwi()
    
    # Korean stopwords
    stopwords = {
        '은', '는', '이', '가', '을', '를', '에', '의', '로', '도', '만', 
        '하다', '되다', '있다', '것', '들', '등', '및', '또는', '그리고'
    }
    
    def tokenize(text: str) -> List[str]:
        """Tokenize text using Kiwi morphological analyzer."""
        text = re.sub(r'[^\w\s]', ' ', text)  # Remove punctuation
        try:
            analyzed = kiwi.analyze(text)
            tokens = []
            for token, pos, _, _ in analyzed[0][0]:
                if (pos.startswith(('N', 'V', 'M')) and 
                    len(token) > 1 and 
                    token not in stopwords):
                    tokens.append(token.lower())
            return tokens
        except:
            return [t.lower() for t in text.split() if len(t) > 1 and t not in stopwords]
    
    def rouge_score(ref_tokens: List[str], pred_tokens: List[str]) -> Dict[str, float]:
        """Calculate ROUGE scores between reference and prediction tokens."""
        if not ref_tokens or not pred_tokens:
            return {'rouge1': 0, 'rouge2': 0, 'rougeL': 0}
        
        # ROUGE-1: Unigram overlap
        ref_1 = Counter(ref_tokens)
        pred_1 = Counter(pred_tokens)
        overlap_1 = sum((ref_1 & pred_1).values())
        rouge1 = overlap_1 / len(ref_tokens) if ref_tokens else 0
        
        # ROUGE-2: Bigram overlap
        ref_2 = Counter([tuple(ref_tokens[i:i+2]) for i in range(len(ref_tokens)-1)])
        pred_2 = Counter([tuple(pred_tokens[i:i+2]) for i in range(len(pred_tokens)-1)])
        overlap_2 = sum((ref_2 & pred_2).values())
        rouge2 = overlap_2 / len(ref_2) if ref_2 else 0
        
        # ROUGE-L: Longest Common Subsequence
        def lcs_length(a: List[str], b: List[str]) -> int:
            """Calculate LCS length using dynamic programming."""
            m, n = len(a), len(b)
            dp = [[0] * (n + 1) for _ in range(m + 1)]
            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    if a[i-1] == b[j-1]:
                        dp[i][j] = dp[i-1][j-1] + 1
                    else:
                        dp[i][j] = max(dp[i-1][j], dp[i][j-1])
            return dp[m][n]
        
        lcs = lcs_length(ref_tokens, pred_tokens)
        rougeL = lcs / len(ref_tokens) if ref_tokens else 0
        
        return {'rouge1': rouge1, 'rouge2': rouge2, 'rougeL': rougeL}
    
    # Evaluation loop
    rouge1_scores, rouge2_scores, rougeL_scores = [], [], []
    
    # Track total retrieved documents
    total_retrieved = 0
    
    for i, (question, ref_docs) in enumerate(tqdm(zip(questions, reference_contexts), 
                                                  desc="Kiwi ROUGE evaluation | Kiwi ROUGE 평가", 
                                                  total=len(questions))):
        # Retrieve documents
        retrieved_docs = retriever.invoke(question)[:k]
        retrieved_texts = [doc.page_content for doc in retrieved_docs]
        total_retrieved += len(retrieved_docs)
        
        # Calculate best scores for each reference document
        question_scores = {'rouge1': [], 'rouge2': [], 'rougeL': []}
        
        for ref_doc in ref_docs:
            # Handle both Document objects and strings
            ref_text = ref_doc.page_content if hasattr(ref_doc, 'page_content') else ref_doc
            ref_tokens = tokenize(ref_text)
            
            best_scores = {'rouge1': 0, 'rouge2': 0, 'rougeL': 0}
            
            for ret_doc in retrieved_texts:
                ret_tokens = tokenize(ret_doc)
                scores = rouge_score(ref_tokens, ret_tokens)
                
                for rouge_type in ['rouge1', 'rouge2', 'rougeL']:
                    if scores[rouge_type] > best_scores[rouge_type]:
                        best_scores[rouge_type] = scores[rouge_type]
            
            for rouge_type in ['rouge1', 'rouge2', 'rougeL']:
                question_scores[rouge_type].append(best_scores[rouge_type])
        
        # Average scores for this question
        rouge1_scores.append(np.mean(question_scores['rouge1']))
        rouge2_scores.append(np.mean(question_scores['rouge2']))
        rougeL_scores.append(np.mean(question_scores['rougeL']))
    
    # Final results
    results = {
        f'kiwi_rouge1@{k}': np.mean(rouge1_scores),
        f'kiwi_rouge2@{k}': np.mean(rouge2_scores),
        f'kiwi_rougeL@{k}': np.mean(rougeL_scores)
    }
    
    print("\n📊 Kiwi ROUGE Evaluation Results | Kiwi ROUGE 평가 결과:")
    for metric, score in results.items():
        print(f"  {metric}: {score:.3f}")
    
    print(f"\n📈 Analysis information | 분석 정보:")
    print(f"  Total queries | 총 질문 수: {len(questions)}")
    print(f"  Total retrieved docs | 총 검색 문서 수: {total_retrieved}")
    print(f"  Avg docs per query | 질문당 평균 검색 문서: {total_retrieved/len(questions):.1f}")
    
    return results
