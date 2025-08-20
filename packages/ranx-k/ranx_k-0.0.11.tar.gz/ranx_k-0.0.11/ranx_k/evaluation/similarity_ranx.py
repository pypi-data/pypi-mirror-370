"""
Similarity-based ranx evaluation for Korean RAG systems.

This module provides ranx-compatible evaluation using semantic similarity
instead of traditional document ID matching. It supports multiple similarity
calculation methods including embedding similarity and Kiwi-based ROUGE.

Based on ranx library concepts: Copyright (c) 2021 Elias Bassani (MIT License)
Extended for semantic similarity evaluation in Korean RAG systems.
"""

import numpy as np
from tqdm import tqdm
from typing import List, Dict, Tuple, Any
import re

try:
    from ranx import Qrels, Run, evaluate
    RANX_AVAILABLE = True
except ImportError:
    RANX_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False

try:
    from rouge_score import rouge_scorer
    ROUGE_AVAILABLE = True
except ImportError:
    ROUGE_AVAILABLE = False

try:
    from kiwipiepy import Kiwi
    KIWI_AVAILABLE = True
except ImportError:
    KIWI_AVAILABLE = False

try:
    from .openai_similarity import OpenAISimilarityCalculator
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def evaluate_with_ranx_similarity(retriever, questions: List[str], 
                                 reference_contexts: List[List[str]], 
                                 k: int = 5,
                                 method: str = 'embedding', 
                                 similarity_threshold: float = 0.7,
                                 embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                                 use_graded_relevance: bool = False,
                                 evaluation_mode: str = 'reference_based',
                                 tokenize_method: str = 'morphs',
                                 use_stopwords: bool = True,
                                 rouge_type: str = 'rougeL') -> Dict[str, float]:
    """
    Evaluate RAG system using ranx with semantic similarity matching.
    
    This function converts semantic similarity scores into ranx-compatible
    relevance judgments, enabling the use of traditional IR metrics while
    accounting for semantic relatedness rather than exact document ID matching.
    
    Args:
        retriever: RAG retriever object with invoke() method.
        questions: List of questions to evaluate.
        reference_contexts: List of reference document lists for each question.
        k: Number of top retrieved documents to evaluate.
        method: Similarity calculation method ('embedding', 'rouge', 'kiwi_rouge', 'openai').
        similarity_threshold: Minimum similarity score to consider relevant (0.0-1.0).
        embedding_model: Sentence transformer model name for embedding method.
        use_graded_relevance: If True, use similarity scores as relevance grades. 
                             If False, use binary relevance (0 or 1).
        evaluation_mode: 'reference_based' calculates proper recall by including all reference 
                        documents in evaluation (measures how many reference docs were retrieved).
                        'retrieval_based' only evaluates actually retrieved documents 
                        (measures precision of retrieval but cannot calculate proper recall).
        tokenize_method: For 'kiwi_rouge' method - tokenization method ('morphs' or 'nouns').
        use_stopwords: For 'kiwi_rouge' method - whether to filter Korean stopwords.
        rouge_type: For 'kiwi_rouge' method - ROUGE metric to use ('rouge1', 'rouge2', 'rougeL').
        
    Returns:
        Dictionary containing ranx evaluation metrics:
        - hit_rate@k: Hit rate at k
        - ndcg@k: Normalized Discounted Cumulative Gain at k
        - map@k: Mean Average Precision at k  
        - mrr: Mean Reciprocal Rank
        
    Examples:
        Basic usage with default embedding model:
        >>> from ranx_k.evaluation import evaluate_with_ranx_similarity
        >>> results = evaluate_with_ranx_similarity(
        ...     retriever=my_retriever,
        ...     questions=["RAG 시스템이란?"],
        ...     reference_contexts=[["RAG는 검색 증강 생성..."]], 
        ...     k=5,
        ...     method='embedding',
        ...     similarity_threshold=0.6
        ... )
        >>> print(f"Hit@5: {results['hit_rate@5']:.3f}")
        
        Using different embedding models:
        >>> # More accurate multilingual model
        >>> results = evaluate_with_ranx_similarity(
        ...     retriever=my_retriever,
        ...     questions=questions,
        ...     reference_contexts=references,
        ...     method='embedding',
        ...     similarity_threshold=0.7,
        ...     embedding_model="sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        ... )
        
        >>> # Latest BGE-M3 model
        >>> results = evaluate_with_ranx_similarity(
        ...     retriever=my_retriever,
        ...     questions=questions,
        ...     reference_contexts=references,
        ...     method='embedding',
        ...     embedding_model="BAAI/bge-m3"
        ... )
        
        Reference-based evaluation (properly calculates recall):
        >>> results = evaluate_with_ranx_similarity(
        ...     retriever=my_retriever,
        ...     questions=questions,
        ...     reference_contexts=references,
        ...     method='kiwi_rouge',
        ...     similarity_threshold=0.3,
        ...     evaluation_mode='reference_based'  # Evaluates against all reference docs
        ... )
        
        Using graded relevance instead of binary:
        >>> results = evaluate_with_ranx_similarity(
        ...     retriever=my_retriever,
        ...     questions=questions,
        ...     reference_contexts=references,
        ...     method='embedding',
        ...     use_graded_relevance=True,  # Uses similarity scores as relevance grades
        ...     evaluation_mode='reference_based'
        ... )
        
        Using Korean-optimized Kiwi ROUGE:
        >>> results = evaluate_with_ranx_similarity(
        ...     retriever=my_retriever,
        ...     questions=questions,
        ...     reference_contexts=references,
        ...     method='kiwi_rouge',
        ...     similarity_threshold=0.3  # Lower threshold for Kiwi ROUGE
        ... )
        
        Using OpenAI Embeddings:
        >>> results = evaluate_with_ranx_similarity(
        ...     retriever=my_retriever,
        ...     questions=questions,
        ...     reference_contexts=references,
        ...     method='openai',
        ...     similarity_threshold=0.7,
        ...     embedding_model="text-embedding-3-small"  # OpenAI model name
        ... )
        
    Raises:
        ImportError: If required dependencies are not installed.
    """
    if not RANX_AVAILABLE:
        raise ImportError(
            "ranx is required for this evaluation. Install with: pip install ranx"
        )
    
    # Validate evaluation mode
    if evaluation_mode not in ['reference_based', 'retrieval_based']:
        raise ValueError(f"Invalid evaluation_mode: {evaluation_mode}. Must be 'reference_based' or 'retrieval_based'")
    
    print(f"🔍 Starting similarity-based ranx evaluation | 유사도 기반 ranx 평가 시작")
    print(f"   Method | 방법: {method}, Threshold | 임계값: {similarity_threshold}, Mode | 모드: {evaluation_mode}")
    
    if evaluation_mode == 'reference_based':
        print(f"   📊 Reference-based mode: Will calculate proper recall metrics | 참조 기반 모드: 정확한 재현율 계산")
    else:
        print(f"   📊 Retrieval-based mode: Will measure precision of retrieved documents | 검색 기반 모드: 검색된 문서의 정밀도 측정")
    
    # Initialize similarity calculator based on method
    if method == 'embedding':
        if not EMBEDDING_AVAILABLE:
            raise ImportError(
                "sentence-transformers and scikit-learn required for embedding method. "
                "Install with: pip install sentence-transformers scikit-learn"
            )
        similarity_calculator = EmbeddingSimilarityCalculator(model_name=embedding_model)
    elif method == 'rouge':
        if not ROUGE_AVAILABLE:
            raise ImportError(
                "rouge_score required for rouge method. Install with: pip install rouge-score"
            )
        similarity_calculator = RougeSimilarityCalculator()
    elif method == 'kiwi_rouge':
        if not KIWI_AVAILABLE:
            raise ImportError(
                "kiwipiepy required for kiwi_rouge method. Install with: pip install kiwipiepy"
            )
        # Use enhanced Kiwi ROUGE with configurable tokenization and ROUGE type
        similarity_calculator = KiwiRougeSimilarityCalculator(
            tokenize_method=tokenize_method, 
            use_stopwords=use_stopwords, 
            rouge_type=rouge_type
        )
    elif method == 'openai':
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "openai required for openai method. Install with: pip install openai"
            )
        similarity_calculator = OpenAISimilarityCalculator(model_name=embedding_model)
    else:
        raise ValueError(f"Unsupported similarity method: {method}")
    
    qrels_dict = {}
    run_dict = {}
    
    # Track total retrieved documents
    total_retrieved_docs = 0
    
    # Create iterator that shows progress bar only after first 3 iterations
    iterator = enumerate(zip(questions, reference_contexts))
    total_questions = len(questions)
    
    # Initialize progress bar as None
    pbar = None
    
    for i, (question, ref_docs) in iterator:
        # Create progress bar after first 3 iterations
        if i == 3 and pbar is None:
            pbar = tqdm(total=total_questions, 
                       desc="ranx similarity evaluation | ranx 유사도 평가",
                       initial=3)  # Start from 3 since we've already done 3
        
        # Update progress bar if it exists
        if pbar is not None:
            pbar.update(1)
        
        query_id = f"q_{i+1}"
        
        # Retrieve documents
        retrieved_docs = retriever.invoke(question)[:k]
        retrieved_texts = [doc.page_content for doc in retrieved_docs]
        total_retrieved_docs += len(retrieved_docs)
        
        # Extract reference texts with proper type handling (robust to str)
        ref_texts = []
        for ref_doc in ref_docs:
            if isinstance(ref_doc, str):
                ref_text = ref_doc
            elif hasattr(ref_doc, 'page_content'):
                ref_text = ref_doc.page_content
            else:
                ref_text = str(ref_doc)
            ref_texts.append(ref_text)
        
        # Calculate similarity matrix (reference docs x retrieved docs)
        try:
            similarity_matrix = similarity_calculator.calculate_similarity_matrix(
                ref_texts, retrieved_texts
            )
            # Handle NaN values in similarity matrix
            if similarity_matrix.size > 0 and np.isnan(similarity_matrix).any():
                similarity_matrix = np.nan_to_num(similarity_matrix, nan=0.0)
        except Exception as e:
            print(f"⚠️ Warning: Error calculating similarity matrix for query {query_id}: {e}")
            # Create empty matrix as fallback
            similarity_matrix = np.zeros((len(ref_texts), len(retrieved_texts)))
        
        # Build qrels and run based on evaluation mode
        qrels_dict[query_id] = {}
        run_dict[query_id] = {}

        if evaluation_mode == 'reference_based':
            # Reference-based evaluation: Compare retrieved docs against reference docs
            # This mode calculates proper recall by including reference documents in evaluation
            
            for j in range(len(retrieved_texts)):
                doc_id = f"doc_{j}"
                
                # Calculate maximum similarity between this retrieved doc and any reference doc
                if similarity_matrix.shape[0] > 0:
                    max_similarity = np.max(similarity_matrix[:, j])
                else:
                    max_similarity = 0.0
                
                # Add to run: all retrieved documents with their similarity scores
                run_dict[query_id][doc_id] = float(max_similarity)
                
                # Add to qrels: only documents that meet similarity threshold
                if max_similarity >= similarity_threshold:
                    if use_graded_relevance:
                        # Graded relevance: use scaled similarity scores as relevance grades
                        # Scale from [threshold, 1.0] to [1.0, 10.0] for ranx compatibility
                        scaled_score = 1.0 + (max_similarity - similarity_threshold) * 9.0 / (1.0 - similarity_threshold)
                        qrels_dict[query_id][doc_id] = float(scaled_score)
                    else:
                        # Binary relevance: use 1.0 for all relevant documents
                        qrels_dict[query_id][doc_id] = 1.0
        else:
            # Retrieval-based evaluation: Evaluate only actually retrieved documents
            # This mode measures precision of retrieval but cannot calculate proper recall
            
            for j in range(len(retrieved_texts)):
                doc_id = f"doc_{j}"
                
                # Calculate maximum similarity between this retrieved doc and any reference doc
                if similarity_matrix.shape[0] > 0:
                    max_similarity = np.max(similarity_matrix[:, j])
                else:
                    max_similarity = 0.0
                
                # Add to run: all retrieved documents with their similarity scores
                run_dict[query_id][doc_id] = float(max_similarity)
                
                # Add to qrels: only documents that meet similarity threshold
                if max_similarity >= similarity_threshold:
                    if use_graded_relevance:
                        # Graded relevance: use scaled similarity scores as relevance grades
                        # Scale from [threshold, 1.0] to [1.0, 10.0] for ranx compatibility
                        scaled_score = 1.0 + (max_similarity - similarity_threshold) * 9.0 / (1.0 - similarity_threshold)
                        qrels_dict[query_id][doc_id] = float(scaled_score)
                    else:
                        # Binary relevance: use 1.0 for all relevant documents
                        qrels_dict[query_id][doc_id] = 1.0
        
        # Debug info for first few queries
        if i < 3:
            print(f"\n🔍 Question | 질문 {i+1}: {question[:50]}...")
            print(f"📊 Reference docs | 참조 문서: {len(ref_texts)}, Retrieved docs | 검색 문서: {len(retrieved_texts)}")
            print(f"📊 Similarity matrix shape | 유사도 매트릭스 shape: {similarity_matrix.shape}")
            if similarity_matrix.size > 0:
                print(f"📈 Max similarity | 최대 유사도: {np.max(similarity_matrix):.3f}")
            print(f"📋 Qrels items | qrels 항목 수: {len(qrels_dict[query_id])}")
            print(f"📋 Run items | run 항목 수: {len(run_dict[query_id])}")
            if evaluation_mode == 'reference_based':
                retrieved_count = len([doc for doc in run_dict[query_id] if doc.startswith('ref_')])
                print(f"📋 Retrieved reference docs | 검색된 참조 문서: {retrieved_count}/{len(ref_texts)}")
            print("-" * 50)
    
    # Close progress bar if it was created
    if pbar is not None:
        pbar.close()
    
    # Evaluate using ranx
    try:
        qrels = Qrels(qrels_dict)
        run = Run(run_dict)
        
        # Calculate IR metrics
        metrics = [f"hit_rate@{k}", f"ndcg@{k}", f"map@{k}", "mrr"]
        results = evaluate(qrels, run, metrics)
        
        # Ensure results is a dictionary for type safety
        if not isinstance(results, dict):
            print(f"❌ Error: ranx evaluate returned unexpected type: {type(results)}")
            return {}
        
        print(f"\n📊 Similarity-based ranx evaluation results | 유사도 기반 ranx 평가 결과 ({method}):")
        for metric, score in results.items():
            print(f"  {metric}: {score:.3f}")
        
        # Additional analysis information
        total_relevant_docs = sum(len(qrels) for qrels in qrels_dict.values())
        total_queries = len(qrels_dict)
        avg_relevant_per_query = total_relevant_docs / total_queries if total_queries > 0 else 0
        
        print(f"\n📈 Analysis information | 분석 정보:")
        print(f"  Total queries | 총 질문 수: {total_queries}")
        print(f"  Total retrieved docs | 총 검색 문서 수: {total_retrieved_docs}")
        print(f"  Avg docs per query | 질문당 평균 검색 문서: {total_retrieved_docs/total_queries:.1f}")
        print(f"  Total relevant docs | 관련 문서 총 개수: {total_relevant_docs}")
        print(f"  Avg relevant per query | 질문당 평균 관련 문서: {avg_relevant_per_query:.1f}")
        print(f"  Threshold used | 사용된 임계값: {similarity_threshold}")
        
        if evaluation_mode == 'reference_based':
            # Count documents in qrels (relevant documents that were retrieved)
            total_retrieved = sum(len(qrels) for qrels in qrels_dict.values())
            total_reference = sum(len(ref_docs) for ref_docs in reference_contexts)
            overall_recall = total_retrieved / total_reference if total_reference > 0 else 0
            print(f"  Overall recall | 전체 재현율: {overall_recall:.3f} ({total_retrieved}/{total_reference})")
        
        return results
        
    except Exception as e:
        print(f"❌ Error during ranx evaluation | ranx 평가 중 오류: {e}")
        print("💡 qrels or run may be empty. Try lowering the threshold | qrels나 run이 비어있을 가능성이 있습니다. 임계값을 낮춰보세요.")
        return {}


class EmbeddingSimilarityCalculator:
    """Embedding-based similarity calculator using sentence transformers."""
    
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialize embedding similarity calculator.
        
        Args:
            model_name: Name of the sentence transformer model to use.
        """
        self.model = SentenceTransformer(model_name)
    
    def calculate_similarity_matrix(self, ref_texts: List[str], 
                                   ret_texts: List[str]) -> np.ndarray:
        """
        Calculate cosine similarity matrix between reference and retrieved texts.
        
        Args:
            ref_texts: List of reference text strings.
            ret_texts: List of retrieved text strings.
            
        Returns:
            2D numpy array with shape (len(ref_texts), len(ret_texts)).
        """
        if not ref_texts or not ret_texts:
            return np.array([[]])
        
        # For very large document sets, use batch processing to avoid memory issues
        batch_size = 50  # Process in batches if more than 50 documents
        total_docs = len(ref_texts) + len(ret_texts)
        
        if total_docs > batch_size:
            # Use show_progress_bar=False for cleaner output during batch processing
            ref_embeddings = self.model.encode(ref_texts, show_progress_bar=False)
            ret_embeddings = self.model.encode(ret_texts, show_progress_bar=False)
        else:
            ref_embeddings = self.model.encode(ref_texts)
            ret_embeddings = self.model.encode(ret_texts)
        
        return cosine_similarity(ref_embeddings, ret_embeddings)


class RougeSimilarityCalculator:
    """ROUGE-based similarity calculator using rouge_score library."""
    
    def __init__(self):
        """Initialize ROUGE similarity calculator."""
        self.scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'])
    
    def calculate_similarity_matrix(self, ref_texts: List[str], 
                                   ret_texts: List[str]) -> np.ndarray:
        """
        Calculate ROUGE-L F1 similarity matrix.
        
        Args:
            ref_texts: List of reference text strings.
            ret_texts: List of retrieved text strings.
            
        Returns:
            2D numpy array with ROUGE-L F1 scores.
        """
        if not ref_texts or not ret_texts:
            return np.array([[]])
        
        similarity_matrix = np.zeros((len(ref_texts), len(ret_texts)))
        
        for i, ref_text in enumerate(ref_texts):
            for j, ret_text in enumerate(ret_texts):
                scores = self.scorer.score(ref_text, ret_text)
                # Use ROUGE-L F1 score as similarity measure
                similarity_matrix[i, j] = scores['rougeL'].fmeasure
        
        return similarity_matrix


class KiwiRougeSimilarityCalculator:
    """Enhanced Kiwi + ROUGE similarity calculator for Korean text."""
    
    def __init__(self, tokenize_method: str = 'morphs', use_stopwords: bool = True, rouge_type: str = 'rougeL'):
        """
        Initialize enhanced Kiwi ROUGE similarity calculator.
        
        Args:
            tokenize_method: Tokenization method ('morphs' or 'nouns').
            use_stopwords: Whether to filter Korean stopwords.
            rouge_type: ROUGE metric to use ('rouge1', 'rouge2', 'rougeL').
        """
        self.rouge_type = rouge_type
        if rouge_type not in ['rouge1', 'rouge2', 'rougeL']:
            raise ValueError(f"Unsupported rouge_type: {rouge_type}. Must be 'rouge1', 'rouge2', or 'rougeL'")
            
        try:
            # Try to use existing KiwiTokenizer from the project
            from ..tokenizers import KiwiTokenizer
            self.tokenizer = KiwiTokenizer(method=tokenize_method, use_stopwords=use_stopwords)
            self.use_custom_tokenizer = True
        except ImportError:
            # Fallback to simple Kiwi implementation
            self.kiwi = Kiwi()
            self.tokenize_method = tokenize_method
            self.use_stopwords = use_stopwords
            self.korean_stopwords = {
                '은', '는', '이', '가', '을', '를', '에', '의', '로', '도', '만', 
                '하다', '되다', '있다', '것', '들', '등', '및', '또는', '그리고'
            }
            self.use_custom_tokenizer = False
    
    def tokenize_with_kiwi(self, text: str) -> List[str]:
        """
        Tokenize Korean text using Kiwi morphological analyzer.
        
        Args:
            text: Text to tokenize.
            
        Returns:
            List of meaningful Korean morphemes.
        """
        if self.use_custom_tokenizer:
            return self.tokenizer.tokenize(text)
        
        # Fallback implementation
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        try:
            analyzed = self.kiwi.analyze(text)
            tokens = []
            for result in analyzed[0][0]:
                # Handle different Kiwi API versions
                if isinstance(result, tuple) and len(result) >= 2:
                    token, pos = result[0], result[1]
                elif hasattr(result, 'form') and hasattr(result, 'tag'):
                    token, pos = result.form, result.tag
                else:
                    continue
                    
                if self.tokenize_method == 'nouns':
                    # Only nouns for noun method
                    if (pos.startswith('N') and len(token) > 1):
                        if not self.use_stopwords or token.lower() not in self.korean_stopwords:
                            tokens.append(token.lower())
                else:
                    # Morphs method: nouns, verbs, modifiers
                    if (pos.startswith(('N', 'V', 'M')) and len(token) > 1):
                        if not self.use_stopwords or token.lower() not in self.korean_stopwords:
                            tokens.append(token.lower())
            return tokens
        except:
            # Simple fallback tokenization
            simple_tokens = [t.lower() for t in text.split() if len(t) > 1]
            if self.use_stopwords:
                simple_tokens = [t for t in simple_tokens if t not in self.korean_stopwords]
            return simple_tokens
    
    def calculate_rouge_scores(self, ref_tokens: List[str], ret_tokens: List[str]) -> Dict[str, float]:
        """
        Calculate comprehensive ROUGE scores between token lists.
        
        Args:
            ref_tokens: Reference document tokens.
            ret_tokens: Retrieved document tokens.
            
        Returns:
            Dictionary with ROUGE-1, ROUGE-2, and ROUGE-L F1 scores.
        """
        if not ref_tokens or not ret_tokens:
            return {'rouge1': 0.0, 'rouge2': 0.0, 'rougeL': 0.0}
        
        from collections import Counter
        
        # ROUGE-1: Unigram overlap F1 score
        ref_1 = Counter(ref_tokens)
        ret_1 = Counter(ret_tokens)
        overlap_1 = sum((ref_1 & ret_1).values())
        
        if overlap_1 == 0:
            rouge1_f1 = 0.0
        else:
            rouge1_precision = overlap_1 / len(ret_tokens)
            rouge1_recall = overlap_1 / len(ref_tokens)
            rouge1_f1 = 2 * (rouge1_precision * rouge1_recall) / (rouge1_precision + rouge1_recall)
        
        # ROUGE-2: Bigram overlap F1 score
        if len(ref_tokens) < 2 or len(ret_tokens) < 2:
            rouge2_f1 = 0.0
        else:
            ref_2 = Counter([tuple(ref_tokens[i:i+2]) for i in range(len(ref_tokens)-1)])
            ret_2 = Counter([tuple(ret_tokens[i:i+2]) for i in range(len(ret_tokens)-1)])
            overlap_2 = sum((ref_2 & ret_2).values())
            
            if overlap_2 == 0:
                rouge2_f1 = 0.0
            else:
                rouge2_precision = overlap_2 / len(ret_2)
                rouge2_recall = overlap_2 / len(ref_2)
                rouge2_f1 = 2 * (rouge2_precision * rouge2_recall) / (rouge2_precision + rouge2_recall)
        
        # ROUGE-L: Longest Common Subsequence F1 score
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
        
        lcs = lcs_length(ref_tokens, ret_tokens)
        
        if lcs == 0:
            rougeL_f1 = 0.0
        else:
            rougeL_precision = lcs / len(ret_tokens)
            rougeL_recall = lcs / len(ref_tokens)
            rougeL_f1 = 2 * (rougeL_precision * rougeL_recall) / (rougeL_precision + rougeL_recall)
        
        return {
            'rouge1': rouge1_f1,
            'rouge2': rouge2_f1,
            'rougeL': rougeL_f1
        }
    
    def calculate_similarity_matrix(self, ref_texts: List[str], 
                                   ret_texts: List[str]) -> np.ndarray:
        """
        Calculate Kiwi ROUGE similarity matrix using ROUGE-L F1 scores.
        
        Args:
            ref_texts: List of reference text strings.
            ret_texts: List of retrieved text strings.
            
        Returns:
            2D numpy array with Kiwi ROUGE-L F1 scores.
        """
        if not ref_texts or not ret_texts:
            return np.array([[]])
        
        similarity_matrix = np.zeros((len(ref_texts), len(ret_texts)))
        
        for i, ref_text in enumerate(ref_texts):
            ref_tokens = self.tokenize_with_kiwi(ref_text)
            
            for j, ret_text in enumerate(ret_texts):
                ret_tokens = self.tokenize_with_kiwi(ret_text)
                scores = self.calculate_rouge_scores(ref_tokens, ret_tokens)
                # Use the specified ROUGE type as similarity score
                similarity_matrix[i, j] = scores[self.rouge_type]
        
        return similarity_matrix


def compare_ranx_methods(retriever, questions: List[str], 
                        reference_contexts: List[List[str]], 
                        k: int = 5) -> Dict[str, Dict[str, float]]:
    """
    Compare different similarity methods for ranx evaluation.
    
    This function evaluates the same RAG system using different similarity
    calculation methods and provides a comprehensive comparison.
    
    Args:
        retriever: RAG retriever object.
        questions: List of questions to evaluate.
        reference_contexts: List of reference document lists.
        k: Number of top documents to evaluate.
        
    Returns:
        Dictionary containing comparison results for each method.
        
    Example:
        >>> from krag.evaluation.similarity_ranx import compare_ranx_methods
        >>> comparison = compare_ranx_methods(
        ...     retriever=my_retriever,
        ...     questions=questions,
        ...     reference_contexts=references,
        ...     k=5
        ... )
        >>> print("Method comparison completed!")
    """
    print("🔍 ranx Similarity Method Comparison Evaluation | ranx 유사도 방법 비교 평가")
    print("="*60)
    
    methods = {
        'embedding': '임베딩 유사도',
        'rouge': '기본 ROUGE',
        'kiwi_rouge': 'Kiwi ROUGE'
    }
    
    all_results = {}
    
    for method_key, method_name in methods.items():
        print(f"\n🚀 Evaluating {method_name} | {method_name} 평가 중...")
        
        try:
            results = evaluate_with_ranx_similarity(
                retriever, questions, reference_contexts, 
                k=k, method=method_key, similarity_threshold=0.5
            )
            
            if results:
                all_results[method_name] = results
            else:
                print(f"❌ {method_name} Evaluation Failed | {method_name} 평가 실패")
                
        except Exception as e:
            print(f"❌ Error during {method_name} evaluation | {method_name} 평가 중 오류: {e}")
    
    # Results comparison
    if all_results:
        print("\n🏆 ranx Method Performance Comparison | ranx 방법별 성능 비교:")
        print("="*60)
        
        for metric in ['hit_rate@5', 'ndcg@5', 'map@5', 'mrr']:
            print(f"\n📊 {metric}:")
            
            for method_name, results in all_results.items():
                if metric in results:
                    score = results[metric]
                    print(f"  {method_name:15s}: {score:.3f}")
    
    return all_results
