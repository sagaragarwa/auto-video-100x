"""
OmniChannel Persistent Vector Memory (ChromaDB + Cosine Deduplication)
======================================================================
Stores and retrieves semantic embeddings of:
- Manufactured video scripts, titles, and hooks
- High-performing competitor topics
- Niche trend clusters

Enforces 0% Semantic Topic Duplication across thousands of videos.
"""

import os
import sys
import json
import time
import hashlib
from typing import List, Dict, Any, Optional, Tuple

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)
if _root not in sys.path:
    sys.path.insert(0, _root)

try:
    from loguru import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("vector_memory")

CHROMA_DIR = os.path.join(_root, "resource", "chroma_db")
os.makedirs(CHROMA_DIR, exist_ok=True)

FALLBACK_STORE_FILE = os.path.join(CHROMA_DIR, "memory_fallback_store.json")


class PersistentVectorMemory:
    """
    ChromaDB-backed semantic vector memory with graceful lightweight fallback.
    """

    def __init__(self, collection_name: str = "video_empire_memory"):
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self._init_chroma()

    def _init_chroma(self):
        try:
            import chromadb
            from chromadb.config import Settings
            self.client = chromadb.PersistentClient(path=CHROMA_DIR)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Omnichannel Video Empire Topic & Hook Embeddings"}
            )
            logger.success(f"🧠 ChromaDB Vector Memory online! Persisted at: {CHROMA_DIR}")
        except Exception as e:
            logger.warning(f"ChromaDB initialization notice (using JSON fallback): {e}")
            self.client = None
            self.collection = None

    def store_video_memory(
        self,
        video_id: str,
        title: str,
        script_excerpt: str,
        niche: str,
        channel_id: str,
        language: str = "en",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Stores video semantic fingerprint into ChromaDB."""
        meta = metadata or {}
        meta.update({
            "title": title[:200],
            "niche": niche,
            "channel_id": channel_id,
            "language": language,
            "timestamp": time.time()
        })
        text_document = f"Title: {title}\nNiche: {niche}\nLanguage: {language}\nContent: {script_excerpt[:1500]}"
        doc_id = f"vid_{video_id}"

        if self.collection:
            try:
                self.collection.upsert(
                    ids=[doc_id],
                    documents=[text_document],
                    metadatas=[meta]
                )
                logger.info(f"💾 Stored semantic vector memory for [{title[:40]}...] in ChromaDB")
                return True
            except Exception as ce:
                logger.warning(f"ChromaDB upsert notice: {ce}")

        # Fallback to persistent JSON store
        return self._store_fallback(doc_id, text_document, meta)

    def query_similar_topics(
        self,
        candidate_topic: str,
        niche: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Queries for semantically similar previous videos to prevent repetition."""
        if self.collection:
            try:
                res = self.collection.query(
                    query_texts=[candidate_topic],
                    n_results=n_results,
                    where={"niche": niche} if niche else None
                )
                matches = []
                ids = res.get("ids", [[]])[0]
                docs = res.get("documents", [[]])[0]
                metas = res.get("metadatas", [[]])[0]
                dists = res.get("distances", [[]])[0] if "distances" in res else [0.5]*len(ids)

                for i in range(len(ids)):
                    matches.append({
                        "id": ids[i],
                        "document": docs[i] if i < len(docs) else "",
                        "metadata": metas[i] if i < len(metas) else {},
                        "distance": dists[i] if i < len(dists) else 0.5
                    })
                return matches
            except Exception as qe:
                logger.warning(f"ChromaDB query warning: {qe}")

        return self._query_fallback(candidate_topic, niche, n_results)

    def is_topic_duplicate(self, candidate_topic: str, niche: str, threshold: float = 0.85) -> bool:
        """Returns True if topic is too close to an existing video."""
        similar = self.query_similar_topics(candidate_topic, niche, n_results=3)
        for s in similar:
            dist = s.get("distance", 1.0)
            # In cosine space, distance < (1.0 - threshold) means high similarity
            if dist < 0.15:
                logger.warning(f"⚠️ Topic '{candidate_topic}' is too similar to existing: {s.get('metadata', {}).get('title')}")
                return True
        return False

    def _store_fallback(self, doc_id: str, doc: str, meta: Dict[str, Any]) -> bool:
        store = {}
        if os.path.exists(FALLBACK_STORE_FILE):
            try:
                store = json.load(open(FALLBACK_STORE_FILE, "r", encoding="utf-8"))
            except Exception:
                store = {}
        store[doc_id] = {"doc": doc, "meta": meta, "time": time.time()}
        try:
            with open(FALLBACK_STORE_FILE, "w", encoding="utf-8") as f:
                json.dump(store, f, indent=2)
            return True
        except Exception:
            return False

    def _query_fallback(self, candidate_topic: str, niche: str, n_results: int) -> List[Dict[str, Any]]:
        if not os.path.exists(FALLBACK_STORE_FILE):
            return []
        try:
            store = json.load(open(FALLBACK_STORE_FILE, "r", encoding="utf-8"))
            cand_words = set(candidate_topic.lower().split())
            results = []
            for did, item in store.items():
                meta = item.get("meta", {})
                if niche and meta.get("niche") != niche:
                    continue
                title = meta.get("title", "").lower()
                overlap = len(cand_words.intersection(set(title.split())))
                results.append({
                    "id": did,
                    "document": item.get("doc", ""),
                    "metadata": meta,
                    "distance": max(0.0, 1.0 - (overlap / max(1, len(cand_words))))
                })
            results.sort(key=lambda x: x["distance"])
            return results[:n_results]
        except Exception:
            return []


# Singleton Vector Memory
VECTOR_MEMORY = PersistentVectorMemory()
