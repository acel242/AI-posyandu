"""
Semantic Search Embeddings Module for AI-Posyandu RAG System.

Provides semantic search upgrade from keyword LIKE search to TF-IDF/cosine similarity.
Architecture is provider-agnostic — current providers:

1. TFIDFProvider  (default, no external deps beyond numpy)
2. DeepseekEmbedProvider  (planned, when Deepseek embeddings API is available)
3. GroqEmbedProvider       (planned, when Groq adds embedding support)

Usage:
    from embeddings import get_embedding_provider, semantic_search_lessons

    provider = get_embedding_provider()
    query_vec = provider.encode("stunting anak")
    results = await semantic_search_lessons("stunting", top_k=5)
"""

import os
import json
import logging
import numpy as np
from typing import Optional

logger = logging.getLogger("posyandu.embeddings")

# ─── Config ───────────────────────────────────────────────────────────────────

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_EMBED_MODEL = os.getenv("DEEPSEEK_EMBED_MODEL", "deepseek-embed")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_EMBED_MODEL = "multilingual-e5-small"  # or whatever Groq supports

# In-memory TF-IDF state (small enough for the lesson corpus)
_TFIDF_WORD_INDEX: Optional[dict] = None
_TFIDF_IDF: Optional[np.ndarray] = None
_TFIDF_VECTOR_SIZE: int = 0
_TFIDF_DOC_COUNT: int = 0
_TFIDF_STORED_VECTORS: dict[int, np.ndarray] = {}

# ─── Vector Storage (SQLite-backed) ───────────────────────────────────────────
# Embeddings stored as JSON in the agent_lessons table (embedding column).
# Schema migration handled at import time via migrate().

VECTOR_DIM = 384  # TF-IDF sparse→dense projection dimension


def _get_connection():
    import aiosqlite, database as db_module
    return db_module.DATABASE_PATH


async def migrate():
    """Add embedding column to agent_lessons if not present."""
    import aiosqlite, database as db_module
    async with aiosqlite.connect(db_module.DATABASE_PATH) as db:
        try:
            await db.execute(
                "ALTER TABLE agent_lessons ADD COLUMN embedding TEXT"
            )
            await db.commit()
            logger.info("Migration: added embedding column to agent_lessons")
        except Exception:
            pass  # column already exists


# ─── TF-IDF Provider ──────────────────────────────────────────────────────────

class TFIDFProvider:
    """Local TF-IDF + cosine similarity semantic search.

    Works entirely offline. Steps:
    1. fit() — build word index and IDF from corpus
    2. encode() — convert text → sparse vector → normalized dense vector
    3. Vector comparison uses cosine similarity (dot product of normalized vecs)
    """

    name = "tfidf"

    def __init__(self):
        self.word_index: dict[str, int] = {}
        self.idf: np.ndarray = np.array([])
        self.doc_count: int = 0
        self.built: bool = False

    def fit(self, texts: list[str]) -> "TFIDFProvider":
        """Build TF-IDF vocabulary and IDF weights from corpus."""
        import re
        # Tokenize
        tokenized = []
        for text in texts:
            tokens = re.findall(r"[a-zA-Z]{2,}", text.lower())
            tokenized.append(tokens)

        # Build word index
        word_count: dict[str, int] = {}
        for tokens in tokenized:
            for t in set(tokens):
                word_count[t] = word_count.get(t, 0) + 1

        # Filter rare words (< 1 document or stopword-like)
        vocab = {w: i for i, (w, c) in enumerate(word_count.items()) if c >= 1}
        self.word_index = vocab
        self.doc_count = len(texts)
        n = len(vocab)

        # IDF: log((N - n_t + 0.5) / (n_t + 0.5) + 1)
        idf = np.zeros(n)
        for word, idx in vocab.items():
            df = sum(1 for tokens in tokenized if word in tokens)
            idf[idx] = max(0.5, np.log((self.doc_count - df + 0.5) / (df + 0.5)) + 1)

        self.idf = idf
        self.built = True
        logger.info(f"TF-IDF built: vocab={n}, docs={self.doc_count}")
        return self

    def _text_to_tf(self, text: str) -> np.ndarray:
        """Text → term-frequency vector (normalized)."""
        import re
        tokens = re.findall(r"[a-zA-Z]{2,}", text.lower())
        n = len(self.word_index)
        tf = np.zeros(n)
        for t in tokens:
            if t in self.word_index:
                tf[self.word_index[t]] += 1
        norm = np.linalg.norm(tf)
        if norm > 0:
            tf /= norm
        return tf

    def encode(self, text: str) -> np.ndarray:
        """Single text → weighted TF-IDF vector (L2-normalized)."""
        if not self.built:
            raise ValueError("TF-IDF not built. Call fit() first.")
        import re
        tokens = re.findall(r"[a-zA-Z]{2,}", text.lower())
        n = len(self.word_index)
        vec = np.zeros(n)
        for t in tokens:
            if t in self.word_index:
                idx = self.word_index[t]
                vec[idx] += 1.0
        # Apply IDF weighting
        vec *= self.idf
        # L2 normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec

    def batch_encode(self, texts: list[str]) -> np.ndarray:
        """Multiple texts → matrix of vectors (rows)."""
        return np.vstack([self.encode(t) for t in texts])

    def cosine_similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """Cosine similarity between two vectors."""
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))


# Singleton TF-IDF provider
_tfidf_provider: Optional[TFIDFProvider] = None


def get_tfidf_provider() -> TFIDFProvider:
    global _tfidf_provider
    if _tfidf_provider is None:
        _tfidf_provider = TFIDFProvider()
    return _tfidf_provider


# ─── Deepseek Embed Provider (planned / experimental) ──────────────────────────

class DeepseekEmbedProvider:
    """Deepseek API embedding provider.

    Currently the Deepseek embeddings endpoint (api.deepseek.com/embeddings)
    returns empty for all model names. This provider is a placeholder that
    gracefully falls back to TFIDFProvider when the API is unavailable.

    To enable when API works:
        export DEEPSEEK_EMBED_MODEL=deepseek-embed
        # API should respond at https://api.deepseek.com/embeddings
    """

    name = "deepseek"
    url = "https://api.deepseek.com/embeddings"
    dim = 0  # set after first call

    def __init__(self):
        self.key = DEEPSEEK_API_KEY
        self.model = DEEPSEEK_EMBED_MODEL
        self._embedding_dim = 0

    async def _call_api(self, texts: list[str]) -> list[np.ndarray]:
        import httpx
        payload = {
            "model": self.model,
            "input": texts,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                self.url,
                headers={
                    "Authorization": f"Bearer {self.key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
        if resp.status_code != 200:
            logger.warning(
                f"Deepseek embed API error {resp.status_code}: {resp.text[:200]}"
            )
            resp.raise_for_status()
        data = resp.json()
        embeddings = []
        for item in data.get("data", []):
            vec = np.array(item["embedding"], dtype=np.float32)
            embeddings.append(vec)
            if self._embedding_dim == 0:
                self._embedding_dim = len(vec)
        return embeddings

    async def encode(self, text: str) -> np.ndarray:
        """Get embedding for a single text via Deepseek API."""
        vectors = await self._call_api([text])
        return vectors[0]

    async def batch_encode(self, texts: list[str]) -> np.ndarray:
        """Batch encode via Deepseek API."""
        return np.vstack(await self._call_api(texts))


# ─── Provider Factory ─────────────────────────────────────────────────────────

def get_embedding_provider() -> TFIDFProvider:
    """Return the best available embedding provider.

    Current priority:
    1. TFIDFProvider (always available, offline)
    2. DeepseekEmbedProvider (planned, requires working API)

    Returns TFIDFProvider unconditionally for now since Deepseek embed
    API is not responding. The architecture supports hot-swap when it works.
    """
    return get_tfidf_provider()


# ─── Semantic Search ───────────────────────────────────────────────────────────

async def build_lesson_embeddings() -> TFIDFProvider:
    """Load all lessons from DB, build TF-IDF model, and cache vectors."""
    import database as db

    lessons = await db.get_all_lessons()
    if not lessons:
        provider = get_tfidf_provider()
        return provider

    # Build corpus from lesson_text + trigger_keywords
    corpus = []
    for lesson in lessons:
        combined = f"{lesson.get('lesson_text', '')} {lesson.get('trigger_keywords', '')} {lesson.get('error_type', '')}"
        corpus.append(combined)

    provider = get_tfidf_provider()
    provider.fit(corpus)

    # Pre-compute and cache all lesson vectors
    global _TFIDF_STORED_VECTORS, _TFIDF_VECTOR_SIZE, _TFIDF_DOC_COUNT
    for i, lesson in enumerate(lessons):
        _TFIDF_STORED_VECTORS[lesson["id"]] = provider.encode(corpus[i])

    _TFIDF_VECTOR_SIZE = len(provider.word_index)
    _TFIDF_DOC_COUNT = len(lessons)

    logger.info(
        f"Built lesson embeddings: {len(lessons)} lessons, "
        f"vocab={_TFIDF_VECTOR_SIZE}"
    )
    return provider


async def semantic_search_lessons(
    query: str,
    top_k: int = 5,
    min_score: float = 0.05,
) -> list[dict]:
    """Find lessons most similar to query using semantic (TF-IDF cosine) search.

    Returns list of dicts with lesson fields + similarity score.
    Falls back to keyword LIKE search if TF-IDF is not yet built.
    """
    import database as db

    provider = get_tfidf_provider()

    # If TF-IDF not built yet, build it on demand
    if not provider.built or _TFIDF_DOC_COUNT == 0:
        await build_lesson_embeddings()

    if not provider.built or _TFIDF_DOC_COUNT == 0:
        # No lessons yet — fall back to keyword search
        return await db.get_lessons_by_keywords(query)

    query_vec = provider.encode(query)

    lessons = await db.get_all_lessons()
    results = []

    for lesson in lessons:
        lesson_vec = _TFIDF_STORED_VECTORS.get(lesson["id"])
        if lesson_vec is None:
            # Re-encode missing vector
            combined = f"{lesson.get('lesson_text', '')} {lesson.get('trigger_keywords', '')}"
            lesson_vec = provider.encode(combined)
            _TFIDF_STORED_VECTORS[lesson["id"]] = lesson_vec

        score = provider.cosine_similarity(query_vec, lesson_vec)
        if score >= min_score:
            results.append({**lesson, "semantic_score": round(score, 4)})

    # Sort by score descending
    results.sort(key=lambda x: x["semantic_score"], reverse=True)

    return results[:top_k]


# ─── Embedding Cache Management ───────────────────────────────────────────────

async def index_lesson(lesson_id: int, lesson_text: str, trigger_keywords: str = "", error_type: str = ""):
    """Index a single lesson — compute embedding and store in DB."""
    import database as db

    provider = get_embedding_provider()
    if not provider.built:
        await build_lesson_embeddings()

    combined = f"{lesson_text} {trigger_keywords} {error_type}"
    vec = provider.encode(combined)

    # Store as JSON in DB
    embedding_json = json.dumps(vec.tolist())

    async with aiosqlite.connect(db.DATABASE_PATH) as db_conn:
        await db_conn.execute(
            "UPDATE agent_lessons SET embedding = ? WHERE id = ?",
            (embedding_json, lesson_id),
        )
        await db_conn.commit()

    _TFIDF_STORED_VECTORS[lesson_id] = vec


# ─── Re-index All ──────────────────────────────────────────────────────────────

async def reindex_all_lessons() -> int:
    """Re-compute and store embeddings for all lessons. Returns count."""
    import database as db

    lessons = await db.get_all_lessons()
    await build_lesson_embeddings()

    for lesson in lessons:
        await index_lesson(
            lesson["id"],
            lesson.get("lesson_text", ""),
            lesson.get("trigger_keywords", ""),
            lesson.get("error_type", ""),
        )

    logger.info(f"Re-indexed {len(lessons)} lessons")
    return len(lessons)


# Import aiosqlite at module level for the index_lesson function
import aiosqlite
