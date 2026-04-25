"""
Nebula-Writer Supabase Client
Migrate from SQLite to Supabase (PostgreSQL) for cloud database
"""

import json
import os
from typing import Any, List


class SupabaseClient:
    """
    Supabase PostgreSQL client for Nebula-Writer
    Provides cloud storage with real-time subscriptions
    """

    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        self.supabase_url = supabase_url or os.environ.get("SUPABASE_URL")
        self.supabase_key = supabase_key or os.environ.get("SUPABASE_ANON_KEY")

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY required")

        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    def _request(self, method: str, endpoint: str, data: dict = None, params: dict = None) -> dict:
        """Make HTTP request to Supabase"""
        import urllib.parse
        import urllib.request

        url = f"{self.supabase_url}/rest/v1/{endpoint}"
        if params:
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
            try:
                error_json = json.loads(error_body)
                return {"error": error_json}
            except:
                return {"error": error_body}

    # ============ GENERIC CRUD ============

    def select(self, table: str, filters: dict = None, order: str = None, limit: int = None) -> List[dict]:
        """Select rows from table"""
        params = {}
        if filters:
            # Build filter string
            filter_parts = [f"{k}.eq.{v}" for k, v in filters.items()]
            params["filter"] = ",".join(filter_parts)
        if order:
            params["order"] = order
        if limit:
            params["limit"] = str(limit)

        return self._request("GET", table, params=params)

    def insert(self, table: str, data: dict) -> dict:
        """Insert row"""
        return self._request("POST", table, data=data)

    def update(self, table: str, data: dict, filters: dict) -> dict:
        """Update rows matching filters"""
        # Build URL with filters
        endpoint = table
        filter_parts = [f"{k}.eq.{v}" for k, v in filters.items()]
        if filter_parts:
            endpoint += "?" + "&".join([f"{k}.eq.{v}" for k, v in filters.items()])

        return self._request("PATCH", table, data=data)

    def delete(self, table: str, filters: dict) -> dict:
        """Delete rows matching filters"""
        endpoint = table + "?" + "&".join([f"{k}.eq.{v}" for k, v in filters.items()])
        return self._request("DELETE", endpoint)

    def execute_sql(self, sql: str) -> dict:
        """Execute raw SQL (RPC)"""
        return self._request("POST", "rpc/exec_sql", data={"query": sql})


class DatabaseFactory:
    """Factory to create database client based on environment"""

    @staticmethod
    def create(db_type: str = None) -> Any:
        """
        Create database client
        Use 'supabase' for cloud, 'sqlite' for local (default)
        """
        db_type = db_type or os.environ.get("NEBULA_DB", "sqlite")

        if db_type == "supabase":
            return SupabaseClient()
        else:
            # Use SQLite (original codex)
            from nebula_writer.codex import CodexDatabase

            data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
            os.makedirs(data_dir, exist_ok=True)
            return CodexDatabase(os.path.join(data_dir, "codex.db"))


# Environment variables needed for Supabase:
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_ANON_KEY=your-anon-key
#
# Optional: NEBULA_DB=supabase (to switch from SQLite)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("Testing Supabase connection...")
        try:
            client = SupabaseClient()
            result = client.select("entities", limit=1)
            print(f"Connected! Found {len(result)} entities")
        except ValueError as e:
            print(f"Setup required: {e}")
            print("\nTo setup Supabase:")
            print("1. Create project at supabase.com")
            print("2. Run SQL schema in schema.sql")
            print("3. Set environment variables:")
            print("   export SUPABASE_URL=https://xxx.supabase.co")
            print("   export SUPABASE_ANON_KEY=yyy")
            print("   export NEBULA_DB=supabase")
