import logging
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class NewsDeduplicator:
    def __init__(self, threshold: float = 0.8, window_size: int = 20):
        self.threshold = threshold
        self.window_size = window_size
        self.history: List[str] = []
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = None

    def is_duplicate(self, candidate_headline: str) -> bool:
        if not self.history:
            self.history.append(candidate_headline)
            self.tfidf_matrix = self.vectorizer.fit_transform(self.history)
            return False

        # Transform only new item
        candidate_vec = self.vectorizer.transform([candidate_headline])

        scores = cosine_similarity(candidate_vec, self.tfidf_matrix)[0]
        max_score = max(scores)

        if max_score >= self.threshold:
            return True

        self.history.append(candidate_headline)

        if len(self.history) > self.window_size:
            self.history.pop(0)

        self.tfidf_matrix = self.vectorizer.fit_transform(self.history)

        return False