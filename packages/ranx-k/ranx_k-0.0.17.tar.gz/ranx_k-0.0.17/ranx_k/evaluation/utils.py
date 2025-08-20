"""
Utility functions for ranx-k evaluation.

This module provides comprehensive comparison utilities and helper functions
for Korean RAG system evaluation.
"""

from typing import List, Dict, Any, Optional
from .kiwi_rouge import simple_kiwi_rouge_evaluation
from .enhanced_rouge import rouge_kiwi_enhanced_evaluation
from .similarity_ranx import evaluate_with_ranx_similarity


def comprehensive_evaluation_comparison(retriever, questions: List[str], 
                                      reference_contexts: List[List[str]], 
                                      k: int = 5) -> Dict[str, Dict[str, float]]:
    """
    Perform comprehensive evaluation using all available methods.
    
    This function runs all evaluation methods provided by ranx-k and presents
    a unified comparison of results. It's ideal for getting a complete picture
    of your RAG system's performance across different evaluation approaches.
    
    Args:
        retriever: RAG retriever object with invoke() method.
        questions: List of questions to evaluate.
        reference_contexts: List of reference document lists for each question.
        k: Number of top retrieved documents to evaluate.
        
    Returns:
        Dictionary containing results from all evaluation methods:
        - 'Kiwi ROUGE': Results from simple_kiwi_rouge_evaluation
        - 'Enhanced ROUGE': Results from rouge_kiwi_enhanced_evaluation  
        - 'Similarity ranx': Results from evaluate_with_ranx_similarity
        
    Example:
        >>> from krag.evaluation import comprehensive_evaluation_comparison
        >>> comparison = comprehensive_evaluation_comparison(
        ...     retriever=my_retriever,
        ...     questions=["RAG 시스템이란?"],
        ...     reference_contexts=[["RAG는 검색 증강 생성..."]], 
        ...     k=5
        ... )
        >>> print("Comprehensive evaluation completed!")
        >>> for method, results in comparison.items():
        ...     print(f"{method}: {results}")
    """
    print("🚀 RAG Evaluation Methods Comprehensive Comparison | RAG 평가 방법 종합 비교\n")
    print("="*60)
    
    all_results = {}
    
    # 1. Kiwi ROUGE evaluation
    print("\n1️⃣ Kiwi ROUGE Evaluation | Kiwi ROUGE 평가")
    print("-" * 30)
    try:
        kiwi_rouge_results = simple_kiwi_rouge_evaluation(
            retriever, questions, reference_contexts, k
        )
        all_results['Kiwi ROUGE'] = kiwi_rouge_results
    except Exception as e:
        print(f"❌ Kiwi ROUGE Evaluation Failed | Kiwi ROUGE 평가 실패: {e}")
        all_results['Kiwi ROUGE'] = {}
    
    # 2. Enhanced ROUGE evaluation
    print("\n2️⃣ Enhanced ROUGE Evaluation | 향상된 ROUGE 평가")
    print("-" * 30)
    try:
        enhanced_rouge_results = rouge_kiwi_enhanced_evaluation(
            retriever, questions, reference_contexts, k
        )
        all_results['Enhanced ROUGE'] = enhanced_rouge_results
    except Exception as e:
        print(f"❌ Enhanced ROUGE Evaluation Failed | Enhanced ROUGE 평가 실패: {e}")
        all_results['Enhanced ROUGE'] = {}
    
    # 3. Similarity-based ranx evaluation
    print("\n3️⃣ Similarity-based ranx Evaluation | 유사도 기반 ranx 평가")
    print("-" * 30)
    try:
        ranx_results = evaluate_with_ranx_similarity(
            retriever, questions, reference_contexts, k, 
            method='kiwi_rouge', similarity_threshold=0.6
        )
        if ranx_results:
            all_results['Similarity ranx'] = ranx_results
        else:
            print("❌ No valid results obtained from ranx evaluation | ranx 평가에서 유효한 결과를 얻지 못했습니다.")
            all_results['Similarity ranx'] = {}
    except Exception as e:
        print(f"❌ Similarity ranx Evaluation Failed | Similarity ranx 평가 실패: {e}")
        all_results['Similarity ranx'] = {}
    
    # Results comparison
    print("\n🏆 Comprehensive Performance Comparison | 종합 성능 비교")
    print("="*60)
    
    _print_comparison_table(all_results, k)
    
    return all_results


def _print_comparison_table(all_results: Dict[str, Dict[str, float]], k: int) -> None:
    """
    Print a formatted comparison table of all evaluation results.
    
    Args:
        all_results: Dictionary containing results from different methods.
        k: Number of top documents evaluated.
    """
    if not all_results:
        print("❌ No results to compare | 비교할 결과가 없습니다.")
        return
    
    # Prepare comparison data
    comparison_data = []
    for method_name, results in all_results.items():
        if not results:
            continue
            
        row = {'Method': method_name}
        
        # Extract ROUGE scores with more flexible matching
        rouge_mappings = {
            'ROUGE1': ['rouge1', 'kiwi_rouge1', 'enhanced_rouge1'],
            'ROUGE2': ['rouge2', 'kiwi_rouge2', 'enhanced_rouge2'], 
            'ROUGEL': ['rougeL', 'rougel', 'kiwi_rougeL', 'enhanced_rougeL']
        }
        
        for display_name, possible_keys in rouge_mappings.items():
            found = False
            for key, value in results.items():
                # Check if any of the possible keys match (case insensitive)
                key_lower = key.lower()
                for possible_key in possible_keys:
                    if (possible_key.lower() in key_lower and 
                        not key.endswith('_std') and 
                        isinstance(value, (int, float))):
                        row[display_name] = f"{value:.3f}"
                        found = True
                        break
                if found:
                    break
            if not found:
                row[display_name] = 'N/A'
        
        # Extract ranx metrics with flexible k value detection
        k_value = str(k)  # Default k value
        
        # Try to find actual k value from the results
        for key in results.keys():
            if '@' in key:
                try:
                    k_value = key.split('@')[1]
                    break
                except IndexError:
                    continue
        
        # More flexible metric matching
        ranx_mappings = {
            'Hit@k': [f'hit_rate@{k_value}', f'hit_rate@{k}', 'hit_rate'],
            'NDCG@k': [f'ndcg@{k_value}', f'ndcg@{k}', 'ndcg'],
            'MRR': ['mrr', 'MRR'],
            'MAP@k': [f'map@{k_value}', f'map@{k}', 'map']
        }
        
        for display_name, possible_keys in ranx_mappings.items():
            found = False
            for possible_key in possible_keys:
                if possible_key in results and isinstance(results[possible_key], (int, float)):
                    row[display_name] = f"{results[possible_key]:.3f}"
                    found = True
                    break
            if not found:
                row[display_name] = 'N/A'
        
        comparison_data.append(row)
    
    # Print table with dynamic headers based on available data
    if comparison_data:
        # Determine which columns actually have data
        all_headers = ['Method', 'ROUGE1', 'ROUGE2', 'ROUGEL', 'Hit@k', 'NDCG@k', 'MAP@k', 'MRR']
        useful_headers = ['Method']
        
        for header in all_headers[1:]:  # Skip 'Method'
            has_data = any(row.get(header, 'N/A') != 'N/A' for row in comparison_data)
            if has_data:
                useful_headers.append(header)
        
        # Print header
        header_line = ""
        for header in useful_headers:
            header_line += f"{header:<15}"
        print(header_line)
        print("-" * len(header_line))
        
        # Print data rows
        for row in comparison_data:
            data_line = ""
            for header in useful_headers:
                value = row.get(header, 'N/A')
                if len(str(value)) > 14:
                    value = str(value)[:11] + "..."
                data_line += f"{str(value):<15}"
            print(data_line)
    
    # Print recommendations
    print(f"\n💡 Recommended Usage Scenarios | 추천 사용 시나리오:")
    print("• Kiwi ROUGE: Fast prototyping and development feedback | 빠른 프로토타이핑 및 개발 중 피드백")
    print("• Enhanced ROUGE: Stable production environment evaluation | 안정적인 프로덕션 환경 평가")
    print("• Similarity ranx: Precise research and benchmarking | 정밀한 연구 및 벤치마킹")


def interpret_scores(results: Dict[str, float]) -> Dict[str, str]:
    """
    Interpret evaluation scores and provide recommendations.
    
    Args:
        results: Dictionary containing evaluation scores.
        
    Returns:
        Dictionary with score interpretations and recommendations.
        
    Example:
        >>> from krag.evaluation.utils import interpret_scores
        >>> scores = {'kiwi_rouge1@5': 0.65, 'kiwi_rouge2@5': 0.45}
        >>> interpretations = interpret_scores(scores)
        >>> for metric, interpretation in interpretations.items():
        ...     print(f"{metric}: {interpretation}")
    """
    interpretations = {}
    
    for metric, score in results.items():
        if isinstance(score, (int, float)):
            if score >= 0.7:
                level = "🟢 Excellent"
                action = "Maintain current settings"
            elif score >= 0.5:
                level = "🟡 Good"
                action = "Consider minor adjustments"
            elif score >= 0.3:
                level = "🟠 Average"
                action = "Improvement needed"
            else:
                level = "🔴 Low"
                action = "System review required"
            
            interpretations[metric] = f"{level} (Score: {score:.3f}) - {action}"
    
    return interpretations


def calculate_improvement(baseline_results: Dict[str, float], 
                         new_results: Dict[str, float]) -> Dict[str, str]:
    """
    Calculate improvement percentages between two evaluation results.
    
    Args:
        baseline_results: Baseline evaluation results.
        new_results: New evaluation results to compare.
        
    Returns:
        Dictionary with improvement percentages for each metric.
        
    Example:
        >>> from krag.evaluation.utils import calculate_improvement
        >>> baseline = {'rouge1@5': 0.3}
        >>> improved = {'rouge1@5': 0.45}
        >>> improvements = calculate_improvement(baseline, improved)
        >>> print(improvements['rouge1@5'])  # "+50.0%"
    """
    improvements = {}
    
    for metric in new_results:
        if metric in baseline_results:
            baseline_score = baseline_results[metric]
            new_score = new_results[metric]
            
            if baseline_score > 0:
                improvement_pct = ((new_score - baseline_score) / baseline_score) * 100
                if improvement_pct > 0:
                    improvements[metric] = f"+{improvement_pct:.1f}%"
                elif improvement_pct < 0:
                    improvements[metric] = f"{improvement_pct:.1f}%"
                else:
                    improvements[metric] = "0.0%"
            else:
                improvements[metric] = "N/A (baseline was 0)"
        else:
            improvements[metric] = "N/A (no baseline)"
    
    return improvements


def batch_evaluation(retriever, data_batches: List[Dict[str, Any]], 
                    batch_size: int = 10, method: str = 'kiwi_rouge') -> List[Dict[str, float]]:
    """
    Perform evaluation on large datasets in batches.
    
    This function is useful for evaluating large datasets that might cause
    memory issues if processed all at once.
    
    Args:
        retriever: RAG retriever object.
        data_batches: List of dictionaries containing 'questions' and 'reference_contexts'.
        batch_size: Number of questions to process in each batch.
        method: Evaluation method to use ('kiwi_rouge', 'enhanced_rouge', 'ranx').
        
    Returns:
        List of evaluation results for each batch.
        
    Example:
        >>> from krag.evaluation.utils import batch_evaluation
        >>> batches = [
        ...     {
        ...         'questions': questions_1_to_100,
        ...         'reference_contexts': references_1_to_100
        ...     },
        ...     {
        ...         'questions': questions_101_to_200, 
        ...         'reference_contexts': references_101_to_200
        ...     }
        ... ]
        >>> results = batch_evaluation(my_retriever, batches, method='kiwi_rouge')
    """
    all_results = []
    
    for i, batch in enumerate(data_batches):
        print(f"🔄 Processing batch {i+1}/{len(data_batches)} | 배치 {i+1}/{len(data_batches)} 처리 중...")
        
        questions = batch['questions']
        reference_contexts = batch['reference_contexts']
        
        # Split into smaller chunks if needed
        for j in range(0, len(questions), batch_size):
            chunk_questions = questions[j:j+batch_size]
            chunk_references = reference_contexts[j:j+batch_size]
            
            try:
                if method == 'kiwi_rouge':
                    results = simple_kiwi_rouge_evaluation(
                        retriever, chunk_questions, chunk_references
                    )
                elif method == 'enhanced_rouge':
                    results = rouge_kiwi_enhanced_evaluation(
                        retriever, chunk_questions, chunk_references
                    )
                elif method == 'ranx':
                    results = evaluate_with_ranx_similarity(
                        retriever, chunk_questions, chunk_references,
                        method='kiwi_rouge'
                    )
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                all_results.append(results)
                
            except Exception as e:
                print(f"❌ Batch {i+1}, chunk {j//batch_size + 1} processing failed | 배치 {i+1}, 청크 {j//batch_size + 1} 처리 실패: {e}")
                all_results.append({})
    
    return all_results


def export_results(results: Dict[str, Any], filepath: str, format: str = 'json') -> None:
    """
    Export evaluation results to file.
    
    Args:
        results: Evaluation results to export.
        filepath: Output file path.
        format: Export format ('json' or 'csv').
        
    Example:
        >>> from krag.evaluation.utils import export_results
        >>> export_results(my_results, 'evaluation_results.json', format='json')
    """
    import json
    import csv
    from pathlib import Path
    
    filepath_obj = Path(filepath)
    
    if format.lower() == 'json':
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"✅ Results saved to JSON format | 결과를 JSON 형식으로 저장: {filepath_obj}")
        
    elif format.lower() == 'csv':
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if results:
                fieldnames = set()
                for method_results in results.values():
                    if isinstance(method_results, dict):
                        fieldnames.update(method_results.keys())
                
                writer = csv.DictWriter(f, fieldnames=['method'] + list(fieldnames))
                writer.writeheader()
                
                for method_name, method_results in results.items():
                    if isinstance(method_results, dict):
                        row = {'method': method_name}
                        row.update(method_results)
                        writer.writerow(row)
        
        print(f"✅ Results saved to CSV format | 결과를 CSV 형식으로 저장: {filepath_obj}")
    else:
        raise ValueError(f"Unsupported format: {format}")
