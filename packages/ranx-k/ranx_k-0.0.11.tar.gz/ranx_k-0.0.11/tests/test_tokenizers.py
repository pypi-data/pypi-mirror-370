"""
Basic tests for ranx-k tokenizers.
"""

import pytest
from ranx_k.tokenizers import KiwiTokenizer


class TestKiwiTokenizer:
    """Test cases for KiwiTokenizer class."""
    
    def test_tokenizer_initialization(self):
        """Test that KiwiTokenizer initializes correctly."""
        tokenizer = KiwiTokenizer(method='morphs', use_stopwords=True)
        assert tokenizer.method == 'morphs'
        assert tokenizer.use_stopwords == True
        assert isinstance(tokenizer.korean_stopwords, set)
    
    def test_basic_tokenization(self):
        """Test basic tokenization functionality."""
        tokenizer = KiwiTokenizer(method='morphs', use_stopwords=True)
        
        # Test Korean text
        text = "자연어처리는 인공지능의 핵심 기술입니다."
        tokens = tokenizer.tokenize(text)
        
        assert isinstance(tokens, list)
        assert len(tokens) > 0
        assert all(isinstance(token, str) for token in tokens)
    
    def test_empty_text(self):
        """Test tokenization of empty or whitespace-only text."""
        tokenizer = KiwiTokenizer()
        
        assert tokenizer.tokenize("") == []
        assert tokenizer.tokenize("   ") == []
        assert tokenizer.tokenize(None) == []
    
    def test_stopword_filtering(self):
        """Test that stopwords are properly filtered."""
        tokenizer_with_stopwords = KiwiTokenizer(use_stopwords=True)
        tokenizer_without_stopwords = KiwiTokenizer(use_stopwords=False)
        
        text = "이것은 테스트입니다."
        
        tokens_with = tokenizer_with_stopwords.tokenize(text)
        tokens_without = tokenizer_without_stopwords.tokenize(text)
        
        # Should have fewer tokens when stopwords are filtered
        assert len(tokens_with) <= len(tokens_without)
    
    def test_morphs_vs_nouns(self):
        """Test difference between morphs and nouns methods."""
        morphs_tokenizer = KiwiTokenizer(method='morphs')
        nouns_tokenizer = KiwiTokenizer(method='nouns')
        
        text = "자연어처리 기술이 발전하고 있습니다."
        
        morphs_tokens = morphs_tokenizer.tokenize(text)
        nouns_tokens = nouns_tokenizer.tokenize(text)
        
        assert isinstance(morphs_tokens, list)
        assert isinstance(nouns_tokens, list)
        # Both should produce some tokens
        assert len(morphs_tokens) > 0
        assert len(nouns_tokens) > 0
    
    def test_add_remove_stopwords(self):
        """Test adding and removing custom stopwords."""
        tokenizer = KiwiTokenizer(use_stopwords=True)
        
        original_count = len(tokenizer.get_stopwords())
        
        # Add custom stopwords
        tokenizer.add_stopwords(['커스텀', '불용어'])
        assert len(tokenizer.get_stopwords()) == original_count + 2
        
        # Remove stopwords
        tokenizer.remove_stopwords(['커스텀'])
        assert len(tokenizer.get_stopwords()) == original_count + 1
        assert '커스텀' not in tokenizer.get_stopwords()
        assert '불용어' in tokenizer.get_stopwords()


class TestTokenizerIntegration:
    """Integration tests for tokenizer usage scenarios."""
    
    def test_rouge_integration_simulation(self):
        """Test that tokenizer works in a rouge-like scenario."""
        tokenizer = KiwiTokenizer()
        
        ref_text = "RAG는 검색 증강 생성 시스템입니다."
        pred_text = "RAG는 검색을 통해 향상된 생성 모델입니다."
        
        ref_tokens = tokenizer.tokenize(ref_text)
        pred_tokens = tokenizer.tokenize(pred_text)
        
        # Should have some overlapping tokens
        overlap = set(ref_tokens) & set(pred_tokens)
        assert len(overlap) > 0


if __name__ == "__main__":
    pytest.main([__file__])
