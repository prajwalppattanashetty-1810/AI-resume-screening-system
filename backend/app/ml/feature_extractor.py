"""
Feature Extractor using TF-IDF for resume and job description text.
"""

from typing import List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer


class FeatureExtractor:
    """Extract features using TF-IDF."""

    def __init__(self, ngram_range=(1, 2), max_features=5000):
        self.vectorizer = TfidfVectorizer(
            ngram_range=ngram_range,
            max_features=max_features,
            stop_words="english",
            sublinear_tf=True
        )
        self.is_fitted = False

    def fit_tfidf(self, documents: List[str]) -> None:
        """Fit TF-IDF model on a corpus of documents."""
        if not documents:
            return
        self.vectorizer.fit(documents)
        self.is_fitted = True

    def transform_tfidf(self, text: str):
        """Transform text to TF-IDF features."""
        if not self.is_fitted:
            raise ValueError("FeatureExtractor must be fitted before transforming.")
        return self.vectorizer.transform([text or ""])

    def get_feature_names(self) -> List[str]:
        """Get TF-IDF feature names."""
        if not self.is_fitted:
            return []
        return list(self.vectorizer.get_feature_names_out())
