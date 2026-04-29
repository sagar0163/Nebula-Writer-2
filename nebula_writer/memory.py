"""
Nebula-Writer Memory System
ChromaDB integration for semantic search and RAG
"""

from pathlib import Path
from typing import Dict, List

# Try to import chromadb
try:
    import chromadb
except ImportError:
    import subprocess

    subprocess.run(["pip", "install", "chromadb"], check=True)
    import chromadb


class MemorySystem:
    """Vector memory using ChromaDB for semantic search"""

    def __init__(self, persist_dir: str = None):
        if persist_dir is None:
            persist_dir = Path(__file__).parent.parent / "data" / "memory"

        Path(persist_dir).mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=str(persist_dir))

        # Collections
        self.chapters = self.client.get_or_create_collection("chapters")
        self.entities = self.client.get_or_create_collection("entities")
        self.events = self.client.get_or_create_collection("events")

    def index_chapter(self, chapter_id: int, summary: str, content: str = None):
        """Index a chapter for semantic search"""
        doc = summary
        if content:
            doc = f"{summary}\n\n{content[:1000]}"  # Truncate long content

        self.chapters.upsert(ids=[str(chapter_id)], documents=[doc], metadatas=[{"chapter_id": chapter_id}])

    def search_chapters(self, query: str, n_results: int = 3) -> List[Dict]:
        """Semantic search across chapters"""
        results = self.chapters.query(query_texts=[query], n_results=n_results)

        return [
            {
                "id": results["ids"][0][i],
                "summary": results["documents"][0][i],
                "distance": results["distances"][0][i] if "distances" in results else None,
            }
            for i in range(len(results["ids"][0]))
        ]

    def index_entity(self, entity_id: int, name: str, description: str, attributes: List[Dict]):
        """Index an entity"""
        doc = f"{name}: {description}"
        if attributes:
            attrs = ", ".join([f"{a['key']}: {a['value']}" for a in attributes])
            doc += f" | {attrs}"

        self.entities.upsert(ids=[str(entity_id)], documents=[doc], metadatas=[{"entity_id": entity_id, "name": name}])

    def search_entities(self, query: str, n_results: int = 5) -> List[Dict]:
        """Semantic search across entities"""
        results = self.entities.query(query_texts=[query], n_results=n_results)

        return [
            {
                "id": results["ids"][0][i],
                "name": results["metadatas"][0][i].get("name"),
                "document": results["documents"][0][i],
                "distance": results["distances"][0][i] if "distances" in results else None,
            }
            for i in range(len(results["ids"][0]))
        ]

    def get_relevant_context(self, query: str, db) -> Dict:
        """Get comprehensive context for writing"""
        # Search chapters
        chapter_hits = self.search_chapters(query, n_results=3)

        # Search entities
        entity_hits = self.search_entities(query, n_results=5)

        # Get full entity details
        entities = db.get_entities()
        entity_map = {e["id"]: e for e in entities}

        relevant_entities = []
        for hit in entity_hits:
            eid = int(hit["id"])
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
                summary += f"- Chapter {ch['id']}: {ch['summary'][:200]}...\n"

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
        chapter_docs = []
        chapter_ids = []
        chapter_metas = []

        for ch in chapters:
            summary = ch.get("summary") or f"Chapter {ch['number']}: {ch.get('title', 'Untitled')}"
            content = ch.get("content", "")
            doc = f"{summary}\n\n{content[:1000]}" if content else summary
            
            chapter_docs.append(doc)
            chapter_ids.append(str(ch["id"]))
            chapter_metas.append({"chapter_id": ch["id"]})

        if chapter_ids:
            self.chapters.upsert(ids=chapter_ids, documents=chapter_docs, metadatas=chapter_metas)

        # 2. Batch Index Entities
        entities = db.get_entities()
        entity_docs = []
        entity_ids = []
        entity_metas = []

        for e in entities:
            attrs = db.get_attributes(e["id"])
            attr_str = ", ".join([f"{a['key']}: {a['value']}" for a in attrs])
            doc = f"{e['name']}: {e.get('description', '')}"
            if attr_str:
                doc += f" | {attr_str}"
            
            entity_docs.append(doc)
            entity_ids.append(str(e["id"]))
            entity_metas.append({"entity_id": e["id"], "name": e["name"]})

        if entity_ids:
            self.entities.upsert(ids=entity_ids, documents=entity_docs, metadatas=entity_metas)

        return {"indexed_chapters": len(chapters), "indexed_entities": len(entities)}


if __name__ == "__main__":
    print("Testing Memory System...")
    # Will work once chromadb is installed
