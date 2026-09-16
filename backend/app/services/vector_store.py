"""
Hybrid Vector and Keyword Retrieval Engine.
Combines TF-IDF n-gram embeddings with cosine similarity and BM25-style keyword boosting.
Saves persistent index to disk (JSON + NumPy / joblib) for fast cross-platform execution.
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

from backend.app.services.ingestion import TranscriptChunkItem


class HybridVectorStore:
    """Persistent hybrid retrieval store combining n-gram semantic vectors and keyword scoring."""

    def __init__(self, index_dir: str):
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.chunks_path = self.index_dir / "chunks.json"
        self.metadata_path = self.index_dir / "metadata.json"
        self.vectorizer_path = self.index_dir / "vectorizer.joblib"
        self.matrix_path = self.index_dir / "matrix.joblib"

        self.chunks: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.doc_matrix = None

        self.load_index()

    def is_indexed(self) -> bool:
        return (
            self.chunks_path.exists()
            and self.metadata_path.exists()
            and self.vectorizer_path.exists()
            and self.matrix_path.exists()
            and self.chunks_path.stat().st_size > 0
        )

    def load_index(self) -> bool:
        """Load persistent index from disk if available."""
        if not self.is_indexed():
            return False

        try:
            with open(self.chunks_path, "r", encoding="utf-8") as f:
                self.chunks = json.load(f)
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
            self.vectorizer = joblib.load(self.vectorizer_path)
            self.doc_matrix = joblib.load(self.matrix_path)
            return True
        except Exception as e:
            print(f"[!] Warning: Failed loading existing vector index: {e}")
            return False

    def build_index(
        self,
        chunk_items: List[TranscriptChunkItem],
        sources_summary: List[Dict[str, Any]],
    ):
        """Build and persist the hybrid index from parsed chunks."""
        if not chunk_items:
            return

        self.chunks = []
        texts = []

        for item in chunk_items:
            chunk_dict = {
                "source_title": item.source_title,
                "source_guest": item.source_guest,
                "source_type": item.source_type,
                "source_url": item.source_url,
                "chunk_index": item.chunk_index,
                "speaker": item.speaker,
                "timestamp_str": item.timestamp_str,
                "text": item.text,
                "word_count": item.word_count,
            }
            self.chunks.append(chunk_dict)
            # Enrich text with title and guest for stronger retrieval grounding
            enriched_text = f"{item.source_title} {item.source_guest or ''} {item.speaker or ''} {item.text}"
            texts.append(enriched_text)

        # Build sublinear TF-IDF vectorizer (unigrams + bigrams)
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            max_features=16000,
            stop_words="english",
        )
        self.doc_matrix = self.vectorizer.fit_transform(texts)

        self.metadata = {
            "total_chunks": len(self.chunks),
            "total_sources": len(sources_summary),
            "vocab_size": len(self.vectorizer.vocabulary_),
            "sources": sources_summary,
        }

        # Save to disk
        with open(self.chunks_path, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=2)
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

        joblib.dump(self.vectorizer, self.vectorizer_path)
        joblib.dump(self.doc_matrix, self.matrix_path)

    def query(
        self,
        query_text: str,
        top_k: int = 4,
        threshold: float = 0.16,
    ) -> List[Dict[str, Any]]:
        """
        Execute hybrid search over the transcript knowledge base.
        Returns top-k chunks with scores, metadata, and relevance flag.
        """
        if not self.is_indexed() or not self.vectorizer or self.doc_matrix is None:
            return []

        clean_query = query_text.strip()
        if not clean_query:
            return []

        # 1. Cosine similarity via TF-IDF vector
        query_vec = self.vectorizer.transform([clean_query])
        cosine_scores = (self.doc_matrix @ query_vec.T).toarray().flatten()

        # 2. Keyword exact matching bonus (ignoring common stop words)
        stop_words = {
            "what", "when", "where", "which", "while", "with", "would", "about", "above", "after",
            "again", "against", "all", "and", "any", "are", "because", "been", "before", "being",
            "below", "between", "both", "but", "by", "could", "did", "does", "doing", "down",
            "during", "each", "few", "for", "from", "further", "had", "has", "have", "having",
            "her", "here", "hers", "herself", "him", "himself", "his", "how", "into", "its",
            "itself", "just", "more", "most", "other", "our", "ours", "ourselves", "out", "over",
            "own", "same", "she", "should", "some", "such", "than", "that", "the", "their",
            "theirs", "them", "themselves", "then", "there", "these", "they", "this", "those",
            "through", "too", "under", "until", "very", "was", "were", "will", "your", "yours",
        }
        query_words = {w for w in re.findall(r"\w+", clean_query.lower()) if len(w) > 2 and w not in stop_words}
        keyword_scores = np.zeros(len(self.chunks))

        if query_words:
            for idx, chunk in enumerate(self.chunks):
                chunk_content = (
                    f"{chunk.get('source_title', '')} {chunk.get('source_guest', '')} {chunk.get('text', '')}"
                ).lower()
                matches = sum(1 for w in query_words if w in chunk_content)
                if matches > 0:
                    keyword_scores[idx] = min(1.0, matches / len(query_words))

        # 3. Hybrid fusion: 70% semantic vector, 30% exact keywords
        hybrid_scores = 0.70 * cosine_scores + 0.30 * keyword_scores

        # Rank indices
        top_indices = np.argsort(hybrid_scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(hybrid_scores[idx])
            chunk = self.chunks[idx]
            match_ratio = keyword_scores[idx]  # keyword_scores holds matches / len(query_words)
            # A chunk is grounded if at least 50% of query content terms match and score meets threshold,
            # or if semantic cosine similarity is exceptionally high (>= 0.35)
            is_grounded = (score >= threshold and match_ratio >= 0.50) or (cosine_scores[idx] >= 0.35)
            results.append({
                "chunk": chunk,
                "score": round(score, 4),
                "is_grounded": bool(is_grounded),
            })

        return results

    def get_status(self) -> Dict[str, Any]:
        """Return current status of the knowledge base."""
        return {
            "is_indexed": self.is_indexed(),
            "total_sources": self.metadata.get("total_sources", 0),
            "total_chunks": self.metadata.get("total_chunks", 0),
            "vocab_size": self.metadata.get("vocab_size", 0),
            "sources": self.metadata.get("sources", []),
        }
