"""
Text Preprocessing Pipeline for Resume NLP.

WHY PREPROCESSING?
Raw text from PDFs contains noise that hurts ML performance:
- Mixed case ('Python' vs 'python' vs 'PYTHON')
- Special characters and punctuation
- Common words that don't add meaning ('the', 'is', 'and')
- Word variants ('programming', 'programmed', 'programmer')

Preprocessing normalizes this so the ML model can focus on meaningful content.

INTERVIEW TIP: Preprocessing is the first step in any NLP pipeline.
Without it, 'Python' and 'python' would be treated as different features
by TF-IDF, reducing the quality of similarity calculations.
"""

import re
import logging

logger = logging.getLogger(__name__)

# ============================================================
# NLTK setup with graceful fallbacks
# ============================================================
_NLTK_AVAILABLE = False
_STOPWORDS_AVAILABLE = False
_WORDNET_AVAILABLE = False

try:
    import nltk

    # Download required resources quietly (no-op if already present, break on network error)
    for resource in ['punkt_tab', 'stopwords', 'wordnet', 'averaged_perceptron_tagger_eng']:
        try:
            success = nltk.download(resource, quiet=True)
            if not success:
                break
        except Exception:
            break

    # Check what's actually available
    try:
        from nltk.tokenize import word_tokenize
        word_tokenize("test")  # Verify it works
        _NLTK_AVAILABLE = True
    except (LookupError, Exception):
        logger.warning("NLTK punkt tokenizer not available, using regex fallback")

    try:
        from nltk.corpus import stopwords as _sw
        _sw.words('english')
        _STOPWORDS_AVAILABLE = True
    except (LookupError, Exception):
        logger.warning("NLTK stopwords not available, using built-in list")

    try:
        from nltk.stem import WordNetLemmatizer
        _lem = WordNetLemmatizer()
        _lem.lemmatize("test")
        _WORDNET_AVAILABLE = True
    except (LookupError, Exception):
        logger.warning("NLTK WordNet not available, skipping lemmatization")

except ImportError:
    logger.warning("NLTK not installed, using fallback preprocessing")


# Built-in stopwords list (subset of NLTK's English stopwords)
# Used as fallback when NLTK data can't be downloaded
FALLBACK_STOPWORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
    'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
    'would', 'could', 'should', 'may', 'might', 'shall', 'can', 'need',
    'dare', 'ought', 'used', 'it', 'its', 'this', 'that', 'these', 'those',
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',
    'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
    'she', 'her', 'hers', 'herself', 'they', 'them', 'their', 'theirs',
    'themselves', 'what', 'which', 'who', 'whom', 'when', 'where', 'why',
    'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other',
    'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
    'than', 'too', 'very', 'just', 'because', 'if', 'then', 'else',
    'about', 'above', 'after', 'again', 'against', 'between', 'into',
    'through', 'during', 'before', 'below', 'down', 'up', 'out', 'off',
    'over', 'under', 'further', 'once', 'here', 'there', 'also',
    'resume', 'curriculum', 'vitae', 'cv', 'page',
}

# Programming languages that look like stopwords but must be kept
KEEP_WORDS = {'c', 'r'}


class TextPreprocessor:
    """NLP text preprocessing pipeline for resume text."""

    def __init__(self):
        # Build stopwords set
        if _STOPWORDS_AVAILABLE:
            from nltk.corpus import stopwords
            self.stop_words = set(stopwords.words('english'))
        else:
            self.stop_words = FALLBACK_STOPWORDS.copy()

        # Add resume-specific stopwords
        self.stop_words.update({'resume', 'curriculum', 'vitae', 'cv', 'page'})

        # Keep programming language names that overlap with stopwords
        self.stop_words -= KEEP_WORDS

        # Initialize lemmatizer if available
        if _WORDNET_AVAILABLE:
            from nltk.stem import WordNetLemmatizer
            self.lemmatizer = WordNetLemmatizer()
        else:
            self.lemmatizer = None

    def clean_text(self, text: str) -> str:
        """
        Clean raw text by removing noise.

        Removes URLs, emails, phone numbers, and special characters
        while preserving hyphens (important for terms like 'CI/CD', 'e-commerce').
        """
        if not text:
            return ""

        text = text.lower()

        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', ' ', text)

        # Remove email addresses
        text = re.sub(r'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}', ' ', text)

        # Remove phone numbers
        text = re.sub(r'\+?\d[\d\-\s()]{8,15}\d', ' ', text)

        # Remove special characters but keep hyphens and alphanumeric
        text = re.sub(r'[^a-z0-9\s\-]', ' ', text)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def tokenize(self, text: str) -> list[str]:
        """
        Split text into individual tokens (words).

        Uses NLTK's word_tokenize if available, falls back to regex-based
        tokenization. Filters out punctuation-only tokens and very short tokens
        (except 'c' and 'r' which are programming languages).
        """
        if not text:
            return []

        # Tokenize
        if _NLTK_AVAILABLE:
            from nltk.tokenize import word_tokenize
            try:
                tokens = word_tokenize(text)
            except Exception:
                tokens = re.findall(r'\b[a-z0-9][\w-]*\b', text.lower())
        else:
            # Regex fallback: split on word boundaries
            tokens = re.findall(r'\b[a-z0-9][\w-]*\b', text.lower())

        # Filter
        filtered = []
        for token in tokens:
            # Skip pure punctuation
            if not re.search(r'[a-z0-9]', token):
                continue
            # Skip very short tokens (except programming languages)
            if len(token) < 2 and token not in KEEP_WORDS:
                continue
            filtered.append(token)

        return filtered

    def remove_stopwords(self, tokens: list[str]) -> list[str]:
        """Remove common English stopwords while preserving technical terms."""
        return [t for t in tokens if t not in self.stop_words]

    def lemmatize(self, tokens: list[str]) -> list[str]:
        """
        Reduce words to their base/root form.

        Example: 'programming' -> 'programming' (noun), 'developed' -> 'developed'
        Uses WordNet lemmatizer if available, otherwise returns tokens unchanged.
        """
        if self.lemmatizer is None:
            return tokens
        return [self.lemmatizer.lemmatize(t) for t in tokens]

    def preprocess_pipeline(self, text: str) -> str:
        """
        Full preprocessing pipeline: clean -> tokenize -> remove stopwords -> lemmatize.
        Returns a single string of preprocessed text.
        """
        tokens = self.get_tokens(text)
        return ' '.join(tokens)

    def get_tokens(self, text: str) -> list[str]:
        """
        Full preprocessing pipeline returning a list of tokens.
        Useful for feature extraction (TF-IDF) later.
        """
        cleaned = self.clean_text(text)
        tokens = self.tokenize(cleaned)
        tokens = self.remove_stopwords(tokens)
        tokens = self.lemmatize(tokens)
        return tokens
