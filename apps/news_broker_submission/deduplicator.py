import logging
from typing import List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity



logger = logging.getLogger(__name__)

class NewsDeduplicator:
    """
    Implements similarity metrics to identify and filter duplicate headlines
    within a sliding window.
    """
    def __init__(self, threshold: float = 0.8, window_size: int = 20):
        self.threshold = threshold
        self.window_size = window_size
        self.history: List[str] = []
        self.vectorizer = TfidfVectorizer()

    def is_duplicate(self, candidate_headline: str) -> bool:
        if not self.history:
            self.history.append(candidate_headline)
            return False
        
        corpus = self.history + [candidate_headline]
        tfidf = self.vectorizer.fit_transform(corpus)

        scores = cosine_similarity(tfidf[-1], tfidf[:-1])[0]
        max_score = max(scores)
        
        if max_score >= self.threshold:
            return True
        
        self.history.append(candidate_headline)
        
        if len(self.history) > self.window_size:
            self.history.pop(0)
        
        return False
        
        
        
