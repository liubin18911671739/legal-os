from typing import List, Set
import jieba
import re


class ChineseTokenizer:
    """Chinese text tokenizer using jieba for segmentation"""

    # Chinese stop words
    STOP_WORDS = {
        "的", "了", "在", "是", "我", "有", "和", "就", "不", "人",
        "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去",
        "你", "会", "着", "没有", "看", "好", "自己", "这", "那", "里",
        "给", "把", "被", "这个", "我们", "你们", "他们", "它们", "它",
        "他", "她", "它", "及", "其", "等", "与", "或", "但", "而",
        "且", "若", "若", "否则", "因此", "所以", "但是", "虽然", "尽管",
        "如果", "那么", "由于", "按照", "根据", "依据", "为了", "关于",
        "对", "对于", "向", "往", "从", "由", "于", "至", "直到",
        "以上", "以下", "之中", "之间", "之外", "以内", "以外",
    }

    def __init__(
        self,
        remove_stopwords: bool = True,
        cut_all: bool = False,
        custom_dict: str = None,
    ):
        """Initialize Chinese tokenizer

        Args:
            remove_stopwords: Whether to remove stop words
            cut_all: Full mode (cut all possible words) vs. precise mode
            custom_dict: Path to custom dictionary file
        """
        self.remove_stopwords = remove_stopwords
        self.cut_all = cut_all
        self.stop_words = self.STOP_WORDS if remove_stopwords else set()

        # Load custom dictionary if provided
        if custom_dict:
            jieba.load_userdict(custom_dict)

    def tokenize(self, text: str) -> List[str]:
        """Tokenize Chinese text

        Args:
            text: Input text string

        Returns:
            List of tokens
        """
        # Preprocess: keep Chinese characters, numbers, and English letters
        text = self._preprocess_text(text)

        # Tokenize using jieba
        tokens = jieba.lcut(text, cut_all=self.cut_all)

        # Filter tokens
        tokens = self._filter_tokens(tokens)

        return tokens

    def _preprocess_text(self, text: str) -> str:
        """Preprocess text before tokenization

        Args:
            text: Input text

        Returns:
            Preprocessed text
        """
        # Keep Chinese characters, numbers, and English letters
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', ' ', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _filter_tokens(self, tokens: List[str]) -> List[str]:
        """Filter tokens by removing stopwords and short tokens

        Args:
            tokens: Raw tokens

        Returns:
            Filtered tokens
        """
        filtered = []
        for token in tokens:
            token = token.strip()
            # Skip empty tokens
            if not token:
                continue
            # Skip single characters (likely noise)
            if len(token) == 1 and token not in ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']:
                continue
            # Skip stop words
            if self.remove_stopwords and token in self.stop_words:
                continue
            # Skip pure numbers
            if token.isdigit():
                continue
            # Skip tokens longer than 20 characters (likely errors)
            if len(token) > 20:
                continue
            
            filtered.append(token)

        return filtered

    def tokenize_batch(self, texts: List[str]) -> List[List[str]]:
        """Tokenize multiple texts

        Args:
            texts: List of text strings

        Returns:
            List of token lists
        """
        return [self.tokenize(text) for text in texts]

    def add_stopwords(self, words: Set[str]) -> None:
        """Add custom stop words

        Args:
            words: Set of stop words to add
        """
        if self.remove_stopwords:
            self.stop_words.update(words)

    def remove_stopwords_set(self, words: Set[str]) -> None:
        """Remove words from stop words set

        Args:
            words: Set of stop words to remove
        """
        if self.remove_stopwords:
            self.stop_words -= words
