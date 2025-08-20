"""
Kiwi-based Korean tokenizer for ROUGE evaluation.

This module provides KiwiTokenizer class that integrates Kiwi morphological analyzer
with rouge_score library for accurate Korean text tokenization.

Original concept inspired by rouge_score tokenizers module.
Modified and extended for Korean language support.
"""

import re
from typing import List, Set

try:
    from kiwipiepy import Kiwi
    KIWI_AVAILABLE = True
except ImportError:
    KIWI_AVAILABLE = False


class KiwiTokenizer:
    """
    Kiwi-based Korean tokenizer compatible with rouge_score library.
    
    This tokenizer integrates Kiwi morphological analyzer to provide accurate
    Korean text tokenization for ROUGE evaluation. It supports both morpheme-level
    and noun-only tokenization with Korean stopword filtering, custom word addition,
    and POS filtering capabilities.
    
    Args:
        use_stemmer (bool): Compatibility parameter (not used in Kiwi).
        method (str): Tokenization method - 'morphs' or 'nouns'.
        use_stopwords (bool): Whether to filter Korean stopwords.
        custom_words (List[tuple]): List of (word, pos_tag) tuples to add to dictionary.
        pos_filter (List[str]): List of POS tag prefixes to include in tokenization.
        
    Example:
        >>> custom_words = [('리비안', 'NNP'), ('테슬라', 'NNP')]
        >>> tokenizer = KiwiTokenizer(method='morphs', custom_words=custom_words)
        >>> tokens = tokenizer.tokenize("리비안은 언제 설립되었나요?")
        >>> print(tokens)
        ['리비안', '언제', '설립']
    """
    
    def __init__(self, use_stemmer: bool = False, method: str = 'morphs', 
                 use_stopwords: bool = True, custom_words: List[tuple] = None,
                 pos_filter: List[str] = None):
        """
        Initialize KiwiTokenizer.
        
        Args:
            use_stemmer: Compatibility parameter for rouge_score interface.
            method: Tokenization method ('morphs' for morphemes, 'nouns' for nouns only).
            use_stopwords: Whether to remove Korean stopwords.
            custom_words: List of (word, pos_tag) tuples to add to user dictionary.
            pos_filter: List of POS tag prefixes to filter (default: ['N', 'V', 'M']).
        """
        if not KIWI_AVAILABLE:
            raise ImportError(
                "Kiwi is required for KiwiTokenizer. Install with: pip install kiwipiepy"
            )
            
        self.kiwi = Kiwi()
        self.method = method
        self.use_stopwords = use_stopwords
        self.pos_filter = pos_filter or ['N', 'V', 'M']  # Default POS filters
        
        # Add custom words to user dictionary
        if custom_words:
            self.add_custom_words(custom_words)
        
        # Korean stopwords - can be extended based on needs
        self.korean_stopwords: Set[str] = {
            '은', '는', '이', '가', '을', '를', '에', '의', '로', '으로', '와', '과',
            '도', '만', '라', '이다', '있다', '없다', '하다', '되다', '수', '것',
            '들', '등', '및', '또는', '그리고', '하지만', '그러나', '따라서',
            '그', '이', '저', '그것', '이것', '저것', '여기', '거기', '저기',
            '때문', '위해', '통해', '대해', '에서', '부터', '까지', '동안'
        } if use_stopwords else set()
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text using Kiwi morphological analyzer.
        
        This is the main interface method called by rouge_score library.
        
        Args:
            text: Text to tokenize.
            
        Returns:
            List of tokens.
            
        Example:
            >>> tokenizer = KiwiTokenizer()
            >>> tokens = tokenizer.tokenize("한국어 자연어처리는 어렵습니다.")
            >>> print(tokens)
            ['한국어', '자연어', '처리', '어렵']
        """
        if not text or not text.strip():
            return []
        
        # Preprocess text
        text = self._preprocess_text(text)
        
        try:
            if self.method == 'morphs':
                return self._tokenize_morphs(text)
            elif self.method == 'nouns':
                return self._tokenize_nouns(text)
            else:
                raise ValueError(f"Unsupported tokenization method: {self.method}")
        except Exception as e:
            # Fallback to simple tokenization if Kiwi fails
            return self._fallback_tokenize(text)
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text by removing punctuation and normalizing whitespace.
        
        Args:
            text: Input text.
            
        Returns:
            Preprocessed text.
        """
        # Remove punctuation and normalize whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _tokenize_morphs(self, text: str) -> List[str]:
        """
        Tokenize using morphological analysis.
        
        Extracts meaningful morphemes based on configured POS filters
        while filtering out functional words and stopwords.
        
        Args:
            text: Preprocessed text.
            
        Returns:
            List of morpheme tokens.
        """
        analyzed = self.kiwi.analyze(text)
        tokens = []
        
        for token, pos, _, _ in analyzed[0][0]:
            # Use configurable POS filter instead of hardcoded tags
            if (any(pos.startswith(prefix) for prefix in self.pos_filter) and 
                len(token) > 1 and 
                token.lower() not in self.korean_stopwords):
                tokens.append(token.lower())
        
        return tokens
    
    def _tokenize_nouns(self, text: str) -> List[str]:
        """
        Extract only nouns from text.
        
        Uses Kiwi's morphological analysis to identify nouns.
        Filters for noun POS tags only.
        
        Args:
            text: Preprocessed text.
            
        Returns:
            List of noun tokens.
        """
        analyzed = self.kiwi.analyze(text)
        tokens = []
        
        for token, pos, _, _ in analyzed[0][0]:
            # Select only noun POS tags (N*)
            if (pos.startswith('N') and 
                len(token) > 1 and 
                token.lower() not in self.korean_stopwords):
                tokens.append(token.lower())
        
        return tokens
    
    def _fallback_tokenize(self, text: str) -> List[str]:
        """
        Fallback tokenization using simple space splitting.
        
        Used when Kiwi analysis fails. Applies basic filtering
        to remove short tokens and stopwords.
        
        Args:
            text: Text to tokenize.
            
        Returns:
            List of space-split tokens.
        """
        return [token.lower() for token in text.split() 
                if len(token) > 1 and token.lower() not in self.korean_stopwords]
    
    def add_stopwords(self, stopwords: List[str]) -> None:
        """
        Add custom stopwords to the existing set.
        
        Args:
            stopwords: List of stopwords to add.
            
        Example:
            >>> tokenizer = KiwiTokenizer()
            >>> tokenizer.add_stopwords(['커스텀', '불용어'])
        """
        self.korean_stopwords.update(stopwords)
    
    def remove_stopwords(self, stopwords: List[str]) -> None:
        """
        Remove stopwords from the existing set.
        
        Args:
            stopwords: List of stopwords to remove.
        """
        self.korean_stopwords.difference_update(stopwords)
    
    def get_stopwords(self) -> Set[str]:
        """
        Get current set of stopwords.
        
        Returns:
            Set of current stopwords.
        """
        return self.korean_stopwords.copy()
    
    def add_custom_words(self, custom_words: List[tuple]) -> None:
        """
        Add custom words to the Kiwi user dictionary.
        
        Args:
            custom_words: List of (word, pos_tag) tuples to add.
            
        Example:
            >>> tokenizer = KiwiTokenizer()
            >>> custom_words = [('리비안', 'NNP'), ('테슬라', 'NNP'), ('전기차', 'NNG')]
            >>> tokenizer.add_custom_words(custom_words)
        """
        for word, pos_tag in custom_words:
            try:
                self.kiwi.add_user_word(word, pos_tag)
                print(f"✅ Custom word added | 커스텀 단어 추가: {word} ({pos_tag})")
            except Exception as e:
                print(f"❌ Failed to add word | 단어 추가 실패: {word} - {e}")
    
    def set_pos_filter(self, pos_prefixes: List[str]) -> None:
        """
        Set POS tag prefixes to filter during tokenization.
        
        Args:
            pos_prefixes: List of POS tag prefixes (e.g., ['N', 'V', 'M']).
            
        Common POS prefixes:
            - N: Nouns (명사)
            - V: Verbs (동사)  
            - M: Modifiers (수식언)
            - J: Particles (조사)
            - E: Endings (어미)
            - X: Others (기타)
            
        Example:
            >>> tokenizer = KiwiTokenizer()
            >>> tokenizer.set_pos_filter(['N', 'V'])  # Only nouns and verbs
        """
        self.pos_filter = pos_prefixes
        print(f"🔧 POS filter updated | POS 필터 업데이트: {pos_prefixes}")
    
    def get_pos_filter(self) -> List[str]:
        """
        Get current POS filter prefixes.
        
        Returns:list
            Current POS filter prefixes.
        """
        return self.pos_filter.copy()


def setup_korean_tokenizer(custom_words: List[tuple] = None, 
                          method: str = 'morphs',
                          pos_filter: List[str] = None,
                          use_stopwords: bool = True) -> KiwiTokenizer:
    """
    Setup Korean tokenizer with custom configuration.
    
    This is a convenience function that creates and configures a KiwiTokenizer
    with custom words, POS filtering, and other options.
    
    Args:
        custom_words: List of (word, pos_tag) tuples to add to dictionary.
        method: Tokenization method ('morphs' or 'nouns').
        pos_filter: List of POS tag prefixes to include.
        use_stopwords: Whether to filter Korean stopwords.
    
    Returns:
        Configured KiwiTokenizer instance.
        
    Example:
        >>> custom_words = [
        ...     ('리비안', 'NNP'),  # Proper noun
        ...     ('테슬라', 'NNP'),  # Proper noun  
        ...     ('전기차', 'NNG'),  # General noun
        ... ]
        >>> tokenizer = setup_korean_tokenizer(
        ...     custom_words=custom_words,
        ...     method='morphs',
        ...     pos_filter=['N', 'V']
        ... )
        >>> tokens = tokenizer.tokenize("리비안은 언제 설립되었나요?")
        >>> print(f"Tokens | 토큰: {tokens}")
    """
    print("🚀 Setting up Korean tokenizer | 한국어 토크나이저 설정 시작")
    
    # Default custom words for common terms
    default_custom_words = [
        ('리비안', 'NNP'),  # Rivian
        ('테슬라', 'NNP'),  # Tesla
        ('전기차', 'NNG'),  # Electric vehicle
        ('자율주행', 'NNG'),  # Autonomous driving
        ('배터리', 'NNG'),  # Battery
    ]
    
    # Merge default and user-provided custom words
    all_custom_words = default_custom_words.copy()
    if custom_words:
        all_custom_words.extend(custom_words)
    
    # Create tokenizer with configuration
    tokenizer = KiwiTokenizer(
        method=method,
        use_stopwords=use_stopwords,
        custom_words=all_custom_words,
        pos_filter=pos_filter
    )
    
    print("✅ Korean tokenizer setup completed | 한국어 토크나이저 설정 완료")
    return tokenizer


def korean_tokenizer_function(text: str, kiwi_model: KiwiTokenizer) -> List[str]:
    """
    Korean tokenizer function for compatibility with existing code.
    
    Args:
        text: Text to tokenize.
        kiwi_model: KiwiTokenizer instance.
        
    Returns:
        List of tokens.
        
    Example:
        >>> kiwi_model = setup_korean_tokenizer()
        >>> tokens = korean_tokenizer_function("리비안은 언제 설립되었나요?", kiwi_model)
        >>> print(f"Original | 원문: 리비안은 언제 설립되었나요?")
        >>> print(f"Tokens | 토큰: {tokens}")
    """
    return kiwi_model.tokenize(text)
