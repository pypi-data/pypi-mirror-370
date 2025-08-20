#!/usr/bin/env python3
"""
Script to convert Korean comments and docstrings to English
in the ranx-k codebase following CLAUDE.md guidelines.
"""

import os
import re
from pathlib import Path

# Translation mappings
TRANSLATIONS = {
    # OpenAI specific terms
    "OpenAI Embeddings API를 사용한 유사도 계산기": "Similarity calculator using OpenAI Embeddings API",
    "OpenAI 임베딩 유사도 계산기 초기화": "Initialize OpenAI embedding similarity calculator",
    "처리할 텍스트 개수": "Number of texts to process",
    "텍스트당 평균 토큰 수": "Average tokens per text",
    "OpenAI 모델명": "OpenAI model name",
    "비용 정보 딕셔너리": "Cost information dictionary",
    # Module/file descriptions
    "기본 토크나이저 사용 예제": "Basic Tokenizer Usage Example",
    "이 예제는 KiwiTokenizer의 기본 사용법을 보여줍니다": "This example demonstrates the basic usage of KiwiTokenizer",
    "종합 평가 비교 예제": "Comprehensive Evaluation Comparison Example", 
    "모든 평가 방법을 종합적으로 비교하고 분석합니다": "Comprehensively compares and analyzes all evaluation methods",
    "ROUGE 평가 예제": "ROUGE Evaluation Example",
    "커스텀 검색기 구현 예제": "Custom Retriever Implementation Example",
    "BGE-M3 모델을 사용한 한국어 RAG 평가 예제": "Korean RAG Evaluation Example Using BGE-M3 Model",
    "OpenAI Embeddings를 사용한 한국어 RAG 평가 예제": "Korean RAG Evaluation Example Using OpenAI Embeddings",
    
    # Common function/class descriptions
    "메인 실행 함수": "Main execution function",
    "종합 평가를 위한 고도화된 검색기": "Advanced retriever for comprehensive evaluation",
    "예제용 가상 검색기": "Example virtual retriever",
    "테스트용 간단한 검색기": "Simple test retriever",
    "간단한 벡터 기반 검색기": "Simple vector-based retriever",
    "키워드 기반 검색기": "Keyword-based retriever",
    "하이브리드 검색기": "Hybrid retriever",
    
    # Technical terms
    "기본 형태소 분석 토크나이저": "Basic morphological analysis tokenizer",
    "명사 추출 토크나이저": "Noun extraction tokenizer",
    "불용어 커스터마이징": "Stopword customization",
    "토크나이저 비교": "Tokenizer comparison",
    "토크나이저 성능 테스트": "Tokenizer performance test",
    "성능 특성 분석": "Performance characteristics analysis",
    
    # Evaluation terms
    "간단한 Kiwi ROUGE 평가": "Simple Kiwi ROUGE evaluation",
    "향상된 ROUGE 평가": "Enhanced ROUGE evaluation",
    "유사도 기반 ranx 평가": "Similarity-based ranx evaluation",
    "종합 평가": "Comprehensive evaluation",
    "상세 성능 분석": "Detailed performance analysis",
    "결과 분석": "Result analysis",
    "성능 비교": "Performance comparison",
    
    # Data and processing
    "평가용 데이터셋 생성": "Create evaluation dataset",
    "TF-IDF 기반 검색": "TF-IDF based search",
    "관련성 점수 계산": "Relevance score calculation",
    "질문별 검색 결과 분석": "Question-wise search result analysis",
    
    # System components
    "RAG 평가 방법 종합 비교": "Comprehensive Comparison of RAG Evaluation Methods",
    "비용 추정": "Cost estimation",
    "사용량에 따라 비용이 발생합니다": "Costs are incurred based on usage",
    
    # Status and messages
    "매우 좋음": "Very Good",
    "양호": "Good", 
    "보통": "Average",
    "낮음": "Low",
    "추천 사용 시나리오": "Recommended Usage Scenarios",
    
    # Common comments
    "기본 불용어로 토큰화": "Tokenization with default stopwords",
    "커스텀 불용어 추가": "Add custom stopwords", 
    "현재 불용어 확인": "Check current stopwords",
    "불용어 사용 vs 미사용": "Stopwords usage vs non-usage comparison",
    "각 문서의 관련성 점수 계산": "Calculate relevance score for each document",
    "간단한 TF-IDF 점수 계산": "Simple TF-IDF score calculation",
    "점수 순으로 정렬": "Sort by score",
    "도메인별 문서 컬렉션": "Domain-specific document collection",
    "자연어처리 관련": "Natural language processing related",
    "정보 검색 관련": "Information retrieval related", 
    "평가 메트릭 관련": "Evaluation metrics related",
    "머신러닝 관련": "Machine learning related",
    "딥러닝 관련": "Deep learning related",
    "평가용 질문-답변 쌍": "Question-answer pairs for evaluation",
    "각 질문에 대한 정답 문서들": "Correct documents for each question",
    "권장사항 생성": "Generate recommendations",
}

def translate_korean_text(text):
    """Translate Korean text to English using the mappings."""
    for korean, english in TRANSLATIONS.items():
        text = text.replace(korean, english)
    return text

def process_file(file_path):
    """Process a single Python file to translate Korean comments and docstrings."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Process docstrings (""" or ''')
        def replace_docstring(match):
            docstring = match.group(0)
            translated = translate_korean_text(docstring)
            return translated
        
        # Match docstrings
        content = re.sub(r'"""[^"]*"""', replace_docstring, content, flags=re.DOTALL)
        content = re.sub(r"'''[^']*'''", replace_docstring, content, flags=re.DOTALL)
        
        # Process single-line comments
        def replace_comment(match):
            comment = match.group(0)
            translated = translate_korean_text(comment)
            return translated
        
        # Match comments starting with # followed by Korean characters
        content = re.sub(r'#[^\n]*[가-힣][^\n]*', replace_comment, content)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated: {file_path}")
            return True
        else:
            print(f"⏭️  No changes: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main function to process all Python files."""
    print("🔄 Converting Korean comments and docstrings to English...")
    print("=" * 60)
    
    # Get project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Directories to process
    directories = [
        project_root / "examples",
        project_root / "ranx_k",
        project_root / "scripts"
    ]
    
    total_files = 0
    updated_files = 0
    
    for directory in directories:
        if directory.exists():
            print(f"\n📁 Processing directory: {directory}")
            for py_file in directory.rglob("*.py"):
                if py_file.name == "fix_korean_comments.py":
                    continue  # Skip this script itself
                total_files += 1
                if process_file(py_file):
                    updated_files += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Summary:")
    print(f"   Total files processed: {total_files}")
    print(f"   Files updated: {updated_files}")
    print(f"   Files unchanged: {total_files - updated_files}")
    print("✅ Korean to English conversion completed!")

if __name__ == "__main__":
    main()