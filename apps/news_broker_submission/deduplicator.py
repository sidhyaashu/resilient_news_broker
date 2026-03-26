import logging
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import vstack, csr_matrix 
logger = logging.getLogger(__name__)


class NewsDeduplicator:
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
        tfidf_matrix = self.vectorizer.fit_transform(corpus)

        candidate_vec = tfidf_matrix.getrow(tfidf_matrix.shape[0] - 1)

        history_rows = [
            tfidf_matrix.getrow(i)
            for i in range(tfidf_matrix.shape[0] - 1)
        ]

        history_vecs = vstack(history_rows)

        history_vecs = csr_matrix(history_vecs)
        candidate_vec = csr_matrix(candidate_vec)

        scores = cosine_similarity(candidate_vec, history_vecs)[0]
        max_score = max(scores)

        if max_score >= self.threshold:
            return True

        self.history.append(candidate_headline)

        if len(self.history) > self.window_size:
            self.history.pop(0)

        return False