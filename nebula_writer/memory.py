"""
Nebula-Writer Memory System
Supabase pgvector integration for semantic search and RAG
Replaces ChromaDB with native PostgreSQL vector support
"""

from pathlib import Path
from typing import Dict, List, Optional
import json
import os
from dotenv import load_dotenv

load_dotenv()


class MemorySystem:
    """Vector memory using Supabase pgvector for semantic search"""

    def __init__(self, persist_dir: str = None):
        self.conn_str = os.environ.get("POSTGRES_CONNECTION_STRING")
        if not self.conn_str:
            raise ValueError("POSTGRES_CONNECTION_STRING environment variable is required")
        
        # Import here to avoid circular imports
        import psycopg2
        from psycopg2.extras import RealDictCursor
        self._psycopg2 = psycopg2
        self._RealDictCursor = RealDictCursor
        
        # Initialize embedding model (lazy load)
        self._embedding_model = None
        self.embedding_dim = 384  # all-MiniLM-L6-v2 dimension

    def _get_embedding_model(self):
        """Lazy load the embedding model"""
        if self._embedding_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            except ImportError:
                # Fallback: use random embeddings for testing
                import random
                class MockEmbedding:
                    def encode(self, text):
                        import hashlib
                        # Deterministic pseudo-random based on text hash
                        seed = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
                        random.seed(seed)
                        return [random.random() for _ in range(384)]
                self._embedding_model = MockEmbedding()
        return self._embedding_model

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using available model"""
        model = self._get_embedding_model()
        embedding = model.encode(text)
        # Convert numpy array to list if needed
        if hasattr(embedding, 'tolist'):
            return embedding.tolist()
        return list(embedding)

    def _get_conn(self):
        """Get database connection with dict cursor"""
        return self._psycopg2.connect(self.conn_str, cursor_factory=self._RealDictCursor)

    def index_chapter(self, chapter_id: str, summary: str, content: str = None):
        """Index a chapter for semantic search"""
        doc = summary
        if content:
            doc = f"{summary}\n\n{content[:1000]}"  # Truncate long content

        embedding = self._get_embedding(doc)

        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO chapter_vectors (chapter_id, content, embedding, metadata)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (chapter_id) DO UPDATE SET
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata,
                    created_at = NOW()
            """, (chapter_id, doc, embedding, json.dumps({"chapter_id": chapter_id})))
            conn.commit()
            cur.close()
        finally:
            conn.close()

    def search_chapters(self, query: str, n_results: int = 3) -> List[Dict]:
        """Semantic search across chapters"""
        query_embedding = self._get_embedding(query)

        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT cv.chapter_id, cv.content, cv.metadata,
                       1 - (cv.embedding <=> %s::vector) as similarity
                FROM chapter_vectors cv
                ORDER BY cv.embedding <=> %s::vector
                LIMIT %s
            """, (query_embedding, query_embedding, n_results))
            
            results = cur.fetchall()
            cur.close()
            
            return [
                {
                    "id": str(row["chapter_id"]),
                    "summary": row["content"][:200] + "..." if len(row["content"]) > 200 else row["content"],
                    "distance": 1 - row["similarity"],
                    "metadata": row["metadata"]
                }
                for row in results
            ]
        finally:
            conn.close()

    def index_entity(self, entity_id: str, name: str, description: str, attributes: List[Dict] = None):
        """Index an entity"""
        doc = f"{name}: {description}"
        if attributes:
            attrs = ", ".join([f"{a['key']}: {a['value']}" for a in attributes])
            doc += f" | {attrs}"

        embedding = self._get_embedding(doc)

        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO entity_vectors (entity_id, content, embedding, metadata)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (entity_id) DO UPDATE SET
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata,
                    created_at = NOW()
            """, (entity_id, doc, embedding, json.dumps({"entity_id": entity_id, "name": name})))
            conn.commit()
            cur.close()
        finally:
            conn.close()

    def search_entities(self, query: str, n_results: int = 5) -> List[Dict]:
        """Semantic search across entities"""
        query_embedding = self._get_embedding(query)

        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT ev.entity_id, ev.content, ev.metadata,
                       1 - (ev.embedding <=> %s::vector) as similarity
                FROM entity_vectors ev
                ORDER BY ev.embedding <=> %s::vector
                LIMIT %s
            """, (query_embedding, query_embedding, n_results))
            
            results = cur.fetchall()
            cur.close()
            
            return [
                {
                    "id": str(row["entity_id"]),
                    "name": row["metadata"].get("name") if row["metadata"] else None,
                    "document": row["content"],
                    "distance": 1 - row["similarity"],
                    "metadata": row["metadata"]
                }
                for row in results
            ]
        finally:
            conn.close()

    def get_relevant_context(self, query: str, db) -> Dict:
        """Get comprehensive context for writing"""
        # Search chapters
        chapter_hits = self.search_chapters(query, n_results=3)

        # Search entities
        entity_hits = self.search_entities(query, n_results=5)

        # Get full entity details
        entities = db.get_entities()
        entity_map = {str(e["id"]): e for e in entities}

        relevant_entities = []
        for hit in entity_hits:
            eid = hit["id"]
            if eid in entity_map:
                e = entity_map[eid]
                e["attributes"] = db.get_attributes(eid)
                relevant_entities.append(e)

        return {
            "chapter_hits": chapter_hits,
            "entities": relevant_entities,
            "context_summary": self._build_context_summary(chapter_hits, relevant_entities),
        }

    def _build_context_summary(self, chapter_hits: List[Dict], entities: List[Dict]) -> str:
        """Build a context summary for the AI"""
        summary = "Relevant context:\n"

        if chapter_hits:
            summary += "\n--- Related Chapters ---\n"
            for ch in chapter_hits:
                summary += f"- Chapter {ch['id']}: {ch['summary']}\n"

        if entities:
            summary += "\n--- Relevant Entities ---\n"
            for e in entities[:3]:
                attrs = ", ".join([f"{a['key']}: {a['value']}" for a in e.get("attributes", [])])
                summary += f"- {e['name']} ({e['type']}): {e.get('description', 'N/A')}\n"
                if attrs:
                    summary += f"  Attributes: {attrs}\n"

        return summary

    def rebuild_index(self, db):
        """Rebuild entire index from database using batch upserts"""
        # 1. Batch Index Chapters
        chapters = db.get_chapters()
        if chapters:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                for ch in chapters:
                    summary = ch.get("summary") or f"Chapter {ch['number']}: {ch.get('title', 'Untitled')}"
                    content = ch.get("content", "")
                    doc = f"{summary}\n\n{content[:1000]}" if content else summary
                    embedding = self._get_embedding(doc)
                    
                    cur.execute("""
                        INSERT INTO chapter_vectors (chapter_id, content, embedding, metadata)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (chapter_id) DO UPDATE SET
                            content = EXCLUDED.content,
                            embedding = EXCLUDED.embedding,
                            metadata = EXCLUDED.metadata,
                            created_at = NOW()
                    """, (str(ch["id"]), doc, embedding, json.dumps({"chapter_id": ch["id"]})))
                conn.commit()
                cur.close()
            finally:
                conn.close()

        # 2. Batch Index Entities
        entities = db.get_entities()
        if entities:
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                for e in entities:
                    attrs = db.get_attributes(e["id"])
                    attr_str = ", ".join([f"{a['key']}: {a['value']}" for a in attrs])
                    doc = f"{e['name']}: {e.get('description', '')}"
                    if attr_str:
                        doc += f" | {attr_str}"
                    embedding = self._get_embedding(doc)
                    
                    cur.execute("""
                        INSERT INTO entity_vectors (entity_id, content, embedding, metadata)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (entity_id) DO UPDATE SET
                            content = EXCLUDED.content,
                            embedding = EXCLUDED.embedding,
                            metadata = EXCLUDED.metadata,
                            created_at = NOW()
                    """, (str(e["id"]), doc, embedding, json.dumps({"entity_id": e["id"], "name": e["name"]})))
                conn.commit()
                cur.close()
            finally:
                conn.close()

        return {"indexed_chapters": len(chapters), "indexed_entities": len(entities)}


if __name__ == "__main__":
    print("Testing Supabase pgvector Memory System...")
    # Will work once dependencies are installed