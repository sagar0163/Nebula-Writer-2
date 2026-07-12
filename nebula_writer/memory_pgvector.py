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
        self._psycopg2 = psycopg2
        
        # Initialize embedding model
        self._embedding_model = None
        self._init_embedding_model()

    def _init_embedding_model(self):
        """Initialize the embedding model (lazy load)"""
        try:
            from sentence_transformers import SentenceTransformer
            # Use a small, fast model for embeddings
            self._embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embedding_dim = 384  # all-MiniLM-L6-v2 dimension
        except ImportError:
            # Fallback: use OpenAI embeddings if available
            try:
                from openai import OpenAI
                self._openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
                self.embedding_dim = 1536  # text-embedding-3-small
            except ImportError:
                self._embedding_model = None
                self._openai_client = None
                self.embedding_dim = 384

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using available model"""
        if self._embedding_model:
            return self._embedding_model.encode(text).tolist()
        elif hasattr(self, '_openai_client') and self._openai_client:
            response = self._openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        else:
            # Fallback: random embedding (for testing only)
            import random
            return [random.random() for _ in range(self.embedding_dim)]

    def _get_conn(self):
        """Get database connection"""
        return self._psycopg2.connect(self.conn_str)

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
                    "id": str(row[0]),
                    "summary": row[1][:200] + "..." if len(row[1]) > 200 else row[1],
                    "distance": 1 - row[3],  # Convert similarity to distance
                    "metadata": row[2]
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
                    "id": str(row[0]),
                    "name": row[2].get("name") if row[2] else None,
                    "document": row[1],
                    "distance": 1 - row[3],
                    "metadata": row[2]
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