from __future__ import annotations

"""
Nebula-Writer Spatial Mapping System
Handles geographical relationships, mapping, and location-based intelligence for world-building
"""

import json
import math
import sqlite3
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List, Optional

from nebula_writer.codex import CodexDatabase
from nebula_writer.postgres_db import PostgresDB


@dataclass
class MapPoint:
    """Represents a point on the map with coordinates"""

    id: Optional[str] = None
    name: str = ""
    x: float = 0.0  # longitude or x-coordinate
    y: float = 0.0  # latitude or y-coordinate
    z: Optional[float] = None  # altitude or z-coordinate (optional)
    entity_id: Optional[str] = None  # links to entities table
    description: str = ""
    user_id: Optional[str] = None  # for RLS

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "MapPoint":
        return cls(**data)


@dataclass
class MapRoute:
    """Represents a route between two points"""

    id: Optional[str] = None
    start_point_id: str = ""
    end_point_id: str = ""
    distance: float = 0.0  # in arbitrary units (could be miles, km, etc.)
    travel_time: str = ""  # e.g., "2 days", "3 hours"
    terrain_type: str = ""  # e.g., "mountain", "forest", "road"
    difficulty: str = "moderate"  # easy, moderate, hard, extreme
    is_bidirectional: bool = True
    description: str = ""
    user_id: Optional[str] = None  # for RLS

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SpatialRegion:
    """Represents an area/zone on the map"""

    id: Optional[str] = None
    name: str = ""
    description: str = ""
    center_x: Optional[float] = None
    center_y: Optional[float] = None
    radius: Optional[float] = None
    points_json: str = ""
    region_type: str = "circular"
    user_id: Optional[str] = None  # for RLS

    def to_dict(self) -> Dict:
        return asdict(self)


class SpatialMapper:
    """Handles spatial relationships and mapping for world-building"""

    def __init__(self, db: CodexDatabase | PostgresDB, user_id: str = None):
        self.db = db
        self.user_id = user_id
        self._init_spatial_tables()

    def _get_connection(self):
        """Get database connection - works with both SQLite and PostgreSQL"""
        if isinstance(self.db, PostgresDB):
            return self.db._get_conn()
        else:
            conn = sqlite3.connect(self.db.db_path)
            conn.row_factory = sqlite3.Row
            return conn

    def _release_connection(self, conn):
        """Release connection back to pool (for PostgreSQL) or close (SQLite)"""
        if isinstance(self.db, PostgresDB):
            self.db._put_conn(conn)
        else:
            conn.close()

    def _execute(self, conn, cursor, sql: str, params: tuple = ()):
        """Execute SQL with appropriate placeholder style for the database"""
        if isinstance(self.db, PostgresDB):
            # Convert ? to %s for PostgreSQL
            sql = sql.replace("?", "%s")
        cursor.execute(sql, params)

    def _init_spatial_tables(self):
        """Initialize spatial mapping tables in the database (SQLite only - Supabase has existing tables)"""
        if isinstance(self.db, PostgresDB):
            # Supabase tables already exist with RLS policies - don't try to create them
            return

        conn = self._get_connection()
        cursor = conn.cursor()

        # Map Points Table (for geographic locations)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS map_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id INTEGER,
                name TEXT NOT NULL,
                x REAL NOT NULL,
                y REAL NOT NULL,
                z REAL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE SET NULL
            )
        """)

        # Map Routes Table (for paths between locations)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS map_routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_point_id INTEGER,
                end_point_id INTEGER,
                distance REAL,
                travel_time TEXT,
                terrain_type TEXT,
                difficulty TEXT DEFAULT 'moderate',
                is_bidirectional INTEGER DEFAULT 1,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (start_point_id) REFERENCES map_points(id) ON DELETE CASCADE,
                FOREIGN KEY (end_point_id) REFERENCES map_points(id) ON DELETE CASCADE
            )
        """)

        # Spatial Regions Table (for areas/zones)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS spatial_regions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                center_x REAL,
                center_y REAL,
                radius REAL,
                points_json TEXT,
                region_type TEXT DEFAULT 'circular',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    # ============ MAP POINTS ============

    def add_map_point(
        self, name: str, x: float, y: float, z: float = None, entity_id: int = None, description: str = ""
    ) -> str:
        """Add a point to the spatial map"""
        conn = self._get_connection()
        cursor = conn.cursor()
        point_id = str(uuid.uuid4())

        if isinstance(self.db, PostgresDB):
            cursor.execute(
                """
                INSERT INTO map_points (id, entity_id, name, x, y, z, description, user_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                RETURNING id
                """,
                (point_id, entity_id, name, x, y, z, description, self.user_id),
            )
            point_id = cursor.fetchone()['id']
        else:
            cursor.execute(
                """
                INSERT INTO map_points (id, entity_id, name, x, y, z, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (point_id, entity_id, name, x, y, z, description),
            )
        conn.commit()
        self._release_connection(conn)
        return point_id

    def get_map_point(self, point_id: str) -> Optional[Dict]:
        """Get a map point by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        if isinstance(self.db, PostgresDB):
            cursor.execute("SELECT * FROM map_points WHERE id = %s", (point_id,))
        else:
            cursor.execute("SELECT * FROM map_points WHERE id = ?", (point_id,))
        row = cursor.fetchone()
        self._release_connection(conn)
        return dict(row) if row else None

    def get_map_points_for_entity(self, entity_id: str) -> List[Dict]:
        """Get all map points associated with an entity"""
        conn = self._get_connection()
        cursor = conn.cursor()
        if isinstance(self.db, PostgresDB):
            cursor.execute("SELECT * FROM map_points WHERE entity_id = %s ORDER BY name", (entity_id,))
        else:
            cursor.execute("SELECT * FROM map_points WHERE entity_id = ? ORDER BY name", (entity_id,))
        rows = cursor.fetchall()
        self._release_connection(conn)
        return [dict(row) for row in rows]

    def update_map_point(self, point_id: str, **kwargs) -> bool:
        """Update a map point"""
        allowed = ["name", "x", "y", "z", "description"]
        conn = self._get_connection()
        cursor = conn.cursor()

        # Build SET clause
        set_clauses = []
        values = []
        for key, value in kwargs.items():
            if key in allowed:
                if isinstance(self.db, PostgresDB):
                    set_clauses.append(f"{key} = %s")
                else:
                    set_clauses.append(f"{key} = ?")
                values.append(value)

        if not set_clauses:
            self._release_connection(conn)
            return False

        values.append(point_id)
        placeholder = "%s" if isinstance(self.db, PostgresDB) else "?"
        query = f"UPDATE map_points SET {', '.join(set_clauses)} WHERE id = {placeholder}"

        cursor.execute(query, values)
        conn.commit()
        updated = cursor.rowcount > 0
        self._release_connection(conn)
        return updated

    def delete_map_point(self, point_id: str) -> bool:
        """Delete a map point"""
        conn = self._get_connection()
        cursor = conn.cursor()
        placeholder = "%s" if isinstance(self.db, PostgresDB) else "?"
        cursor.execute(f"DELETE FROM map_points WHERE id = {placeholder}", (point_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        self._release_connection(conn)
        return deleted

    # ============ MAP ROUTES ============

    def add_map_route(
        self,
        start_point_id: str,
        end_point_id: str,
        distance: float = None,
        travel_time: str = "",
        terrain_type: str = "",
        difficulty: str = "moderate",
        is_bidirectional: bool = True,
        description: str = "",
    ) -> str:
        """Add a route between two map points"""
        conn = self._get_connection()
        cursor = conn.cursor()
        route_id = str(uuid.uuid4())

        if isinstance(self.db, PostgresDB):
            cursor.execute(
                """
                INSERT INTO map_routes
                (id, start_point_id, end_point_id, distance, travel_time, terrain_type,
                 difficulty, is_bidirectional, description, user_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                RETURNING id
                """,
                (
                    route_id,
                    start_point_id,
                    end_point_id,
                    distance,
                    travel_time,
                    terrain_type,
                    difficulty,
                    is_bidirectional,
                    description,
                    self.user_id,
                ),
            )
            route_id = cursor.fetchone()[0]
        else:
            cursor.execute(
                """
                INSERT INTO map_routes
                (id, start_point_id, end_point_id, distance, travel_time, terrain_type,
                 difficulty, is_bidirectional, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    route_id,
                    start_point_id,
                    end_point_id,
                    distance,
                    travel_time,
                    terrain_type,
                    difficulty,
                    1 if is_bidirectional else 0,
                    description,
                ),
            )
        conn.commit()
        self._release_connection(conn)
        return route_id

    def get_map_routes(self, point_id: str = None) -> List[Dict]:
        """Get map routes, optionally filtered by a point"""
        conn = self._get_connection()
        cursor = conn.cursor()
        if point_id:
            if isinstance(self.db, PostgresDB):
                cursor.execute(
                    """
                    SELECT * FROM map_routes
                    WHERE start_point_id = %s OR end_point_id = %s
                    """,
                    (point_id, point_id),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM map_routes
                    WHERE start_point_id = ? OR end_point_id = ?
                    """,
                    (point_id, point_id),
                )
        else:
            cursor.execute("SELECT * FROM map_routes ORDER BY created_at DESC")

        rows = cursor.fetchall()
        self._release_connection(conn)
        return [dict(row) for row in rows]

    # ============ SPATIAL QUERIES ============

    def calculate_distance(self, point1: MapPoint, point2: MapPoint) -> float:
        """Calculate distance between two points (Euclidean)"""
        return math.sqrt(
            (point2.x - point1.x) ** 2 + (point2.y - point1.y) ** 2 + ((point2.z or 0) - (point1.z or 0)) ** 2
        )

    def find_nearby_points(self, x: float, y: float, radius: float, limit: int = 10) -> List[Dict]:
        """Find points within a radius of given coordinates"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if isinstance(self.db, PostgresDB):
            cursor.execute(
                """
                SELECT * FROM map_points
                WHERE sqrt(power(x - %s, 2) + power(y - %s, 2)) <= %s
                ORDER BY sqrt(power(x - %s, 2) + power(y - %s, 2))
                LIMIT %s
                """,
                (x, y, radius, x, y, limit),
            )
        else:
            cursor.execute(
                """
                SELECT * FROM map_points
                WHERE sqrt((x - ?) * (x - ?) + (y - ?) * (y - ?)) <= ?
                ORDER BY sqrt((x - ?) * (x - ?) + (y - ?) * (y - ?))
                LIMIT ?
                """,
                (x, x, y, y, radius, x, x, y, y, limit),
            )

        rows = cursor.fetchall()
        self._release_connection(conn)
        return [dict(row) for row in rows]

    # ============ SPATIAL REGIONS ============

    def add_spatial_region(
        self,
        name: str,
        center_x: float,
        center_y: float,
        radius: float,
        points: List[str] = None,
        region_type: str = "circular",
        description: str = "",
    ) -> str:
        """Add a spatial region (area/zone)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        region_id = str(uuid.uuid4())
        points_json = json.dumps(points or [])

        if isinstance(self.db, PostgresDB):
            cursor.execute(
                """
                INSERT INTO spatial_regions (id, name, description, center_x, center_y, radius, points_json, region_type, user_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                RETURNING id
                """,
                (region_id, name, description, center_x, center_y, radius, points_json, region_type, self.user_id),
            )
            region_id = cursor.fetchone()[0]
        else:
            cursor.execute(
                """
                INSERT INTO spatial_regions (id, name, description, center_x, center_y, radius, points_json, region_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (region_id, name, description, center_x, center_y, radius, points_json, region_type),
            )
        conn.commit()
        self._release_connection(conn)
        return region_id

    def get_spatial_regions(self) -> List[Dict]:
        """Get all spatial regions"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM spatial_regions ORDER BY created_at DESC")
        rows = cursor.fetchall()
        self._release_connection(conn)
        return [dict(row) for row in rows]


def create_spatial_mapper(db: CodexDatabase | PostgresDB, user_id: str = "default") -> SpatialMapper:
    """Factory function to create a SpatialMapper instance"""
    return SpatialMapper(db, user_id)