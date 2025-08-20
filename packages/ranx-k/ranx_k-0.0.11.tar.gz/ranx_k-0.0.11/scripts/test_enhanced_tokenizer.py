#!/usr/bin/env python3
"""
Test script for enhanced Korean tokenizer functionality.

Tests the new features:
1. Custom word addition with setup_korean_tokenizer function
2. POS filtering capabilities 
3. Enhanced KiwiTokenizer class methods
"""

from ranx_k.tokenizers.kiwi_tokenizer import setup_korean_tokenizer, korean_tokenizer_function, KiwiTokenizer

def test_basic_functionality():
    """Test basic tokenizer functionality."""
    print("🧪 Test 1: Basic Functionality | 기본 기능 테스트")
    print("=" * 60)
    
    # Test text
    test_text = "리비안은 언제 설립되었나요?"
    
    # Basic tokenizer
    tokenizer = KiwiTokenizer(method='morphs')
    tokens = tokenizer.tokenize(test_text)
    
    print(f"📝 Original text | 원문: {test_text}")
    print(f"🔤 Basic tokens | 기본 토큰: {tokens}")
    print()

def test_setup_korean_tokenizer():
    """Test the setup_korean_tokenizer function."""
    print("🧪 Test 2: setup_korean_tokenizer Function | setup_korean_tokenizer 함수 테스트")
    print("=" * 60)
    
    # Custom words to add
    custom_words = [
        ('리비안', 'NNP'),  # Proper noun
        ('테슬라', 'NNP'),  # Proper noun
        ('전기차', 'NNG'),  # General noun
        ('자율주행', 'NNG'),  # General noun
    ]
    
    # Setup tokenizer with custom words
    tokenizer = setup_korean_tokenizer(
        custom_words=custom_words,
        method='morphs',
        pos_filter=['N', 'V']  # Only nouns and verbs
    )
    
    # Test texts
    test_texts = [
        "리비안은 언제 설립되었나요?",
        "테슬라의 전기차 라인업에서 Model X는 어떤 위치를 차지하나요?",
        "자율주행 기술은 어떻게 발전하고 있나요?"
    ]
    
    print("\n📋 Test Results | 테스트 결과:")
    for i, text in enumerate(test_texts, 1):
        tokens = tokenizer.tokenize(text)
        print(f"  {i}. Original | 원문: {text}")
        print(f"     Tokens | 토큰: {tokens}")
        print()

def test_pos_filtering():
    """Test POS filtering functionality."""
    print("🧪 Test 3: POS Filtering | 품사 필터링 테스트")
    print("=" * 60)
    
    test_text = "리비안은 전기차를 제조하는 혁신적인 회사입니다."
    
    # Test different POS filters
    pos_filters = [
        (['N'], "Nouns only | 명사만"),
        (['V'], "Verbs only | 동사만"),
        (['N', 'V'], "Nouns and Verbs | 명사와 동사"),
        (['N', 'V', 'M'], "Nouns, Verbs, Modifiers | 명사, 동사, 수식언")
    ]
    
    print(f"📝 Test text | 테스트 텍스트: {test_text}")
    print()
    
    for pos_filter, description in pos_filters:
        tokenizer = KiwiTokenizer(method='morphs', pos_filter=pos_filter)
        tokens = tokenizer.tokenize(test_text)
        print(f"🔧 {description}")
        print(f"   Filter | 필터: {pos_filter}")
        print(f"   Tokens | 토큰: {tokens}")
        print()

def test_korean_tokenizer_function():
    """Test the korean_tokenizer_function for compatibility."""
    print("🧪 Test 4: korean_tokenizer_function Compatibility | korean_tokenizer_function 호환성 테스트")
    print("=" * 60)
    
    # Setup tokenizer
    kiwi_model = setup_korean_tokenizer()
    
    # Test text
    test_text = "리비안은 언제 설립되었나요?"
    
    # Use compatibility function
    tokens = korean_tokenizer_function(test_text, kiwi_model)
    
    print(f"📝 Original | 원문: {test_text}")
    print(f"🔤 Tokens | 토큰: {tokens}")
    print()

def test_custom_word_methods():
    """Test custom word addition methods."""
    print("🧪 Test 5: Custom Word Methods | 커스텀 단어 메서드 테스트")
    print("=" * 60)
    
    # Create tokenizer
    tokenizer = KiwiTokenizer(method='morphs')
    
    # Test before adding custom words
    test_text = "BYD와 NIO는 중국의 전기차 회사입니다."
    tokens_before = tokenizer.tokenize(test_text)
    print(f"📝 Test text | 테스트 텍스트: {test_text}")
    print(f"🔤 Before custom words | 커스텀 단어 추가 전: {tokens_before}")
    
    # Add custom words
    custom_words = [('BYD', 'NNP'), ('NIO', 'NNP')]
    tokenizer.add_custom_words(custom_words)
    
    # Test after adding custom words
    tokens_after = tokenizer.tokenize(test_text)
    print(f"🔤 After custom words | 커스텀 단어 추가 후: {tokens_after}")
    print()

def main():
    """Run all tests."""
    print("🚀 Enhanced Korean Tokenizer Test Suite | 개선된 한국어 토크나이저 테스트 모음")
    print("🚀 Testing new features | 새로운 기능 테스트")
    print("=" * 80)
    print()
    
    try:
        test_basic_functionality()
        test_setup_korean_tokenizer()
        test_pos_filtering()
        test_korean_tokenizer_function()
        test_custom_word_methods()
        
        print("✅ All tests completed successfully | 모든 테스트가 성공적으로 완료되었습니다!")
        
    except Exception as e:
        print(f"❌ Test failed | 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()