"""
Nebula-Writer Supabase Database Wrapper
Provides same interface as CodexDatabase for Supabase
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class SupabaseDB:
    """Supabase database interface matching CodexDatabase API"""

    def __init__(self):
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_ANON_KEY")

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY required")

        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    def _request(self, method: str, table: str, data: dict = None, filters: dict = None) -> dict:
        import urllib.parse
        import urllib.request

        url = f"{self.supabase_url}/rest/v1/{table}"
        params = {}
        if filters:
            for k, v in filters.items():
                params[f"{k}:eq"] = str(v)
            url += "?" + urllib.parse.urlencode(params)

        request_data = json.dumps(data).encode("utf-8") if data else None

        req = urllib.request.Request(url, data=request_data, headers=self.headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status == 204:
                    return {"message": "Success"}
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            return {"error": json.loads(error_body)} if error_body else {"error": str(e)}

    # ============ ENTITY OPERATIONS ============

    def get_entities(self, entity_type: str = None) -> List[Dict]:
        filters = {"entity_type": entity_type} if entity_type else None
        result = self._request("GET", "entities", filters=filters)
        return result if isinstance(result, list) else []

    def get_entity(self, entity_id: int) -> Optional[Dict]:
        result = self._request("GET", "entities", filters={"id": entity_id})
        return result[0] if isinstance(result, list) and result else None

    def add_entity(
        self,
        name: str,
        entity_type: str,
        description: str = None,
        current_location: str = None,
        is_alive: bool = True,
        image_url: str = None,
    ) -> str:
        data = {
            "name": name,
            "entity_type": entity_type,
            "description": description,
            "current_location": current_location,
            "is_alive": is_alive,
            "image_url": image_url,
        }
        result = self._request("POST", "entities", data=data)
        return result.get("id", "0") if isinstance(result, dict) else "0"

    def get_attributes(self, entity_id: int) -> List[Dict]:
        return self._request("GET", "attributes", filters={"entity_id": entity_id})

    def get_relationships(self, entity_id: int = None) -> List[Dict]:
        filters = {"from_entity_id": entity_id} if entity_id else None
        return self._request("GET", "relationships", filters=filters)

    def get_events(self, chapter: int = None) -> List[Dict]:
        filters = {"chapter": chapter} if chapter else None
        return self._request("GET", "events", filters=filters)

    def get_chapters(self) -> List[Dict]:
        return self._request("GET", "chapters")

    def get_chapter(self, chapter_id: int = None, number: int = None) -> Optional[Dict]:
        filters = {"id": chapter_id} if chapter_id else {"number": number}
        result = self._request("GET", "chapters", filters=filters)
        return result[0] if isinstance(result, list) and result else None

    def get_stats(self) -> Dict:
        try:
            entities = self._request("GET", "entities")
            chapters = self._request("GET", "chapters")
            relationships = self._request("GET", "relationships")
            events = self._request("GET", "events")

            return {
                "total_entities": len(entities) if isinstance(entities, list) else 0,
                "entities_by_type": self._count_by_type(entities),
                "total_chapters": len(chapters) if isinstance(chapters, list) else 0,
                "total_relationships": len(relationships) if isinstance(relationships, list) else 0,
                "total_events": len(events) if isinstance(events, list) else 0,
                "total_words": sum(c.get("word_count", 0) for c in (chapters if isinstance(chapters, list) else [])),
            }
        except:
            return {
                "total_entities": 0,
                "entities_by_type": {},
                "total_chapters": 0,
                "total_relationships": 0,
                "total_events": 0,
                "total_words": 0,
            }

    def _count_by_type(self, entities: list) -> Dict:
        counts = {}
        for e in entities or []:
            t = e.get("entity_type", "unknown")
            counts[t] = counts.get(t, 0) + 1
        return counts

    def add_chapter(self, number: int, title: str = None, content: str = "") -> str:
        data = {
            "number": number,
            "title": title,
            "content": content,
            "word_count": len(content.split()) if content else 0,
        }
        result = self._request("POST", "chapters", data=data)
        return result.get("id", "0")

    def update_chapter(self, chapter_id: int, content: str = None, title: str = None, summary: str = None) -> bool:
        data = {}
        if content is not None:
            data["content"] = content
            data["word_count"] = len(content.split())
        if title is not None:
            data["title"] = title
        if summary is not None:
            data["summary"] = summary
        data["updated_at"] = datetime.now().isoformat()

        self._request("PATCH", "chapters", data=data, filters={"id": chapter_id})
        return True

    def search(self, query: str) -> Dict:
        # Simple search - would need Full Text Search in production
        return {"entities": [], "chapters": [], "events": []}

    # ============ PLOT/WORLD (NEW TABLES) ============

    def get_plot_threads(self, status: str = None) -> List[Dict]:
        filters = {"status": status} if status else None
        return self._request("GET", "plot_threads", filters=filters)

    def add_plot_thread(
        self, title: str, description: str = None, planted_chapter: int = None, importance: str = "normal"
    ) -> str:
        data = {
            "title": title,
            "description": description,
            "planted_chapter": planted_chapter,
            "importance": importance,
            "status": "planted",
        }
        result = self._request("POST", "plot_threads", data=data)
        return result.get("id", "0")

    def resolve_plot_thread(self, thread_id: int, resolved_chapter: int = None) -> bool:
        data = {"status": "resolved", "resolved_chapter": resolved_chapter}
        self._request("PATCH", "plot_threads", data=data, filters={"id": thread_id})
        return True

    def get_foreshadowing(self, plot_thread_id: int = None, unfulfilled_only: bool = True) -> List[Dict]:
        filters = {"plot_thread_id": plot_thread_id} if plot_thread_id else None
        if unfulfilled_only:
            filters = filters or {}
            filters["fulfilled"] = False
        return self._request("GET", "foreshadowing", filters=filters)

    def add_foreshadowing(
        self, plot_thread_id: int, chapter_id: int, content: str, hint_level: str = "subtle", payoff_chapter: int = None
    ) -> str:
        data = {
            "plot_thread_id": plot_thread_id,
            "chapter_id": chapter_id,
            "content": content,
            "hint_level": hint_level,
            "payoff_expected_chapter": payoff_chapter,
        }
        result = self._request("POST", "foreshadowing", data=data)
        return result.get("id", "0")

    def get_world_rules(self, category: str = None) -> List[Dict]:
        filters = {"category": category} if category else None
        return self._request("GET", "world_rules", filters=filters)

    def add_world_rule(
        self, category: str, rule: str, description: str = None, exceptions: str = None, applies_to: str = None
    ) -> str:
        data = {
            "category": category,
            "rule": rule,
            "description": description,
            "exceptions": exceptions,
            "applies_to_entities": applies_to,
        }
        result = self._request("POST", "world_rules", data=data)
        return result.get("id", "0")

    def get_consistency_issues(self, chapter_id: int = None, unresolved_only: bool = False) -> List[Dict]:
        filters = {"chapter_id": chapter_id} if chapter_id else None
        if unresolved_only:
            filters = filters or {}
            filters["resolved"] = False
        return self._request("GET", "consistency_issues", filters=filters)

    def add_consistency_issue(
        self,
        chapter_id: int = None,
        entity_id: int = None,
        issue_type: str = "",
        description: str = "",
        severity: str = "medium",
    ) -> str:
        data = {
            "chapter_id": chapter_id,
            "entity_id": entity_id,
            "issue_type": issue_type,
            "description": description,
            "severity": severity,
        }
        result = self._request("POST", "consistency_issues", data=data)
        return result.get("id", "0")

    def resolve_consistency_issue(self, issue_id: int) -> bool:
        self._request("PATCH", "consistency_issues", data={"resolved": True}, filters={"id": issue_id})
        return True

    def run_consistency_check(self) -> List[Dict]:
        # Would need full implementation
        return []

    def get_templates(self) -> List[Dict]:
        return self._request("GET", "story_templates")

    def get_template(self, template_id: int) -> Optional[Dict]:
        result = self._request("GET", "story_templates", filters={"id": template_id})
        return result[0] if isinstance(result, list) and result else None

    def get_versions(self, chapter_id: int) -> List[Dict]:
        return self._request("GET", "chapter_versions", filters={"chapter_id": chapter_id})

    def get_version(self, version_id: int) -> Optional[Dict]:
        result = self._request("GET", "chapter_versions", filters={"id": version_id})
        return result[0] if isinstance(result, list) and result else None

    def save_version(self, chapter_id: int, content: str) -> str:
        data = {"chapter_id": chapter_id, "content": content, "word_count": len(content.split()) if content else 0}
        result = self._request("POST", "chapter_versions", data=data)
        return result.get("id", "0")

    def get_character_knowledge(self, entity_id: int, chapter_id: int = None) -> List[Dict]:
        filters = {"entity_id": entity_id}
        if chapter_id:
            filters["chapter_id"] = chapter_id
        return self._request("GET", "character_knowledge", filters=filters)

    def update_character_knowledge(self, entity_id: int, chapter_id: int, knowledge: str) -> str:
        data = {"entity_id": entity_id, "chapter_id": chapter_id, "knowledge": knowledge}
        result = self._request("POST", "character_knowledge", data=data)
        return result.get("id", "0")

    def extract_entities_from_text(self, text: str) -> Dict:
        # Simple extraction - would need NLP in production
        return {"characters": [], "locations": [], "items": []}

    def delete_entity(self, entity_id: int) -> bool:
        self._request("DELETE", "entities", filters={"id": entity_id})
        return True

    def delete_relationship(self, rel_id: int) -> bool:
        self._request("DELETE", "relationships", filters={"id": rel_id})
        return True

    def delete_chapter(self, chapter_id: int) -> bool:
        self._request("DELETE", "chapters", filters={"id": chapter_id})
        return True

    def add_attribute(self, entity_id: int, key: str, value: str) -> str:
        data = {"entity_id": entity_id, "key": key, "value": value}
        result = self._request("POST", "attributes", data=data)
        return result.get("id", "0")

    def delete_attribute(self, attr_id: int) -> bool:
        self._request("DELETE", "attributes", filters={"id": attr_id})
        return True

    def add_relationship(
        self, from_id: int, to_id: int, rel_type: str, strength: float = 0.5, description: str = None
    ) -> str:
        data = {
            "from_entity_id": from_id,
            "to_entity_id": to_id,
            "relationship_type": rel_type,
            "strength": strength,
            "description": description,
        }
        result = self._request("POST", "relationships", data=data)
        return result.get("id", "0")

    def add_event(
        self, title: str, description: str = None, chapter: int = None, scene: str = None, significance: str = "normal"
    ) -> str:
        data = {
            "title": title,
            "description": description,
            "chapter": chapter,
            "scene": scene,
            "significance": significance,
        }
        result = self._request("POST", "events", data=data)
        return result.get("id", "0")


def create_supabase_db() -> SupabaseDB:
    """Create Supabase database instance"""
    return SupabaseDB()
