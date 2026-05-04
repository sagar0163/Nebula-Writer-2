"""
Nebula-Writer Spatial Mapping System
Handles geographical relationships, mapping, and location-based intelligence for world-building
"""

import json
import math
import sqlite3
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

from nebula_writer.codex import CodexDatabase


@dataclass
class MapPoint:
    """Represents a point on the map with coordinates"""

    name: str
    x: float  # longitude or x-coordinate
    y: float  # latitude or y-coordinate
    z: Optional[float] = None  # altitude or z-coordinate (optional)
    entity_id: Optional[int] = None  # links to entities table
    description: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "MapPoint":
        return cls(**data)


@dataclass
class MapRoute:
    """Represents a route between two points"""

    id: Optional[int] = None
    start_point: str = ""
    end_point: str = ""
    distance: float = 0.0  # in arbitrary units (could be miles, km, etc.)
    travel_time: str = ""  # e.g., "2 days", "3 hours"
    terrain_type: str = ""  # e.g., "mountain", "forest", "road"
    difficulty: str = "moderate"  # easy, moderate, hard, extreme
    is_bidirectional: bool = True
    description: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


class SpatialMapper:
    """Handles spatial relationships and mapping for world-building"""

    def __init__(self, db: CodexDatabase):
        self.db = db
        self._init_spatial_tables()

    def _init_spatial_tables(self):
        """Initialize spatial mapping tables in the database"""
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

    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ============ MAP POINTS ============

    def add_map_point(
        self, name: str, x: float, y: float, z: float = None, entity_id: int = None, description: str = ""
    ) -> int:
        """Add a point to the spatial map"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO map_points (entity_id, name, x, y, z, description)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (entity_id, name, x, y, z, description),
        )
        point_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return point_id

    def get_map_point(self, point_id: int) -> Optional[Dict]:
        """Get a map point by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM map_points WHERE id = ?", (point_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_map_points_for_entity(self, entity_id: int) -> List[Dict]:
        """Get all map points associated with an entity"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM map_points WHERE entity_id = ? ORDER BY name", (entity_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def update_map_point(self, point_id: int, **kwargs) -> bool:
        """Update a map point"""
        allowed = ["name", "x", "y", "z", "description"]
        conn = self._get_connection()
        cursor = conn.cursor()

        # Build SET clause
        set_clauses = []
        values = []
        for key, value in kwargs.items():
            if key in allowed:
                set_clauses.append(f"{key} = ?")
                values.append(value)

        if not set_clauses:
            conn.close()
            return False

        values.append(point_id)
        query = f"UPDATE map_points SET {', '.join(set_clauses)} WHERE id = ?"

        cursor.execute(query, values)
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        return updated

    def delete_map_point(self, point_id: int) -> bool:
        """Delete a map point"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM map_points WHERE id = ?", (point_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted

    # ============ MAP ROUTES ============

    def add_map_route(
        self,
        start_point_id: int,
        end_point_id: int,
        distance: float = None,
        travel_time: str = "",
        terrain_type: str = "",
        difficulty: str = "moderate",
        is_bidirectional: bool = True,
        description: str = "",
    ) -> int:
        """Add a route between two map points"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO map_routes
            (start_point_id, end_point_id, distance, travel_time, terrain_type,
             difficulty, is_bidirectional, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
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
        route_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return route_id

    def get_map_routes(self, point_id: int = None) -> List[Dict]:
        """Get map routes, optionally filtered by a point"""
        conn = self._get_connection()
        cursor = conn.cursor()
        if point_id:
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
        conn.close()
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
        # Simple bounding box first for efficiency, then precise distance
        cursor.execute(
            """
            SELECT * FROM map_points
            WHERE x BETWEEN ? AND ? AND y BETWEEN ? AND ?
            """,
            (x - radius, x + radius, y - radius, y + radius),
        )
        rows = cursor.fetchall()
        conn.close()

        # Filter by actual distance
        nearby = []
        for row in rows:
            point = MapPoint(
                name=row["name"],
                x=row["x"],
                y=row["y"],
                z=row["z"],
                entity_id=row["entity_id"],
                description=row["description"],
            )
            distance = self.calculate_distance(MapPoint("temp", x, y, 0), point)
            if distance <= radius:
                nearby.append(dict(row))

        # Sort by distance and limit
        nearby.sort(
            key=lambda p: self.calculate_distance(
                MapPoint("temp", x, y, 0), MapPoint(p["name"], p["x"], p["y"], p["z"])
            )
        )
        return nearby[:limit]

    def get_location_distance(self, entity_id1: int, entity_id2: int) -> Optional[float]:
        """Get distance between two locations (by entity ID)"""
        points1 = self.get_map_points_for_entity(entity_id1)
        points2 = self.get_map_points_for_entity(entity_id2)

        if not points1 or not points2:
            return None

        # Use first point for each entity (could be enhanced to use closest points)
        point1 = MapPoint(name=points1[0]["name"], x=points1[0]["x"], y=points1[0]["y"], z=points1[0]["z"])
        point2 = MapPoint(name=points2[0]["name"], x=points2[0]["x"], y=points2[0]["y"], z=points2[0]["z"])

        return self.calculate_distance(point1, point2)

    # ============ SPATIAL REGIONS ============

    def add_spatial_region(
        self,
        name: str,
        description: str = "",
        center_x: float = None,
        center_y: float = None,
        radius: float = None,
        points_json: str = None,
        region_type: str = "circular",
    ) -> int:
        """Add a spatial region (area/zone)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO spatial_regions
            (name, description, center_x, center_y, radius, points_json, region_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, description, center_x, center_y, radius, points_json, region_type),
        )
        region_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return region_id

    def point_in_region(self, x: float, y: float, region_id: int) -> bool:
        """Check if a point is within a spatial region"""
        region = self.get_spatial_region(region_id)
        if not region:
            return False

        if region["region_type"] == "circular" and region["center_x"] is not None and region["center_y"] is not None:
            # Circular region
            distance = math.sqrt((x - region["center_x"]) ** 2 + (y - region["center_y"]) ** 2)
            return distance <= (region["radius"] or 0)
        elif region["region_type"] == "polygonal" and region["points_json"]:
            # Polygonal region (simplified - would need proper point-in-polygon algorithm)
            try:
                points = json.loads(region["points_json"])
                # Simple bounding box check for now
                xs = [p["x"] for p in points]
                ys = [p["y"] for p in points]
                return (min(xs) <= x <= max(xs)) and (min(ys) <= y <= max(ys))
            except:
                return False
        return False

    def get_spatial_region(self, region_id: int) -> Optional[Dict]:
        """Get a spatial region by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM spatial_regions WHERE id = ?", (region_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    # ============ INTEGRATION WITH ENTITIES ============

    def link_entity_to_map_point(self, entity_id: int, map_point_id: int) -> bool:
        """Link an entity to a map point (updates the map point's entity_id)"""
        return self.update_map_point(map_point_id, entity_id=entity_id)

    def get_entity_location(self, entity_id: int) -> Optional[Dict]:
        """Get the map location of an entity"""
        points = self.get_map_points_for_entity(entity_id)
        return points[0] if points else None

    def suggest_travel_time(self, distance: float, terrain_type: str = "") -> str:
        """Suggest travel time based on distance and terrain"""
        # Base speed: 5 units/hour on flat terrain
        base_speed = 5.0  # units per hour

        terrain_modifiers = {
            "road": 1.2,
            "plain": 1.0,
            "forest": 0.7,
            "mountain": 0.4,
            "swamp": 0.3,
            "desert": 0.8,
            "ocean": 0.5,  # assuming sailing
        }

        modifier = terrain_modifiers.get(terrain_type, 1.0)
        speed = base_speed * modifier

        if speed <= 0:
            return "Unknown"

        hours = distance / speed

        if hours < 1:
            return f"{int(hours * 60)} minutes"
        elif hours < 24:
            return f"{hours:.1f} hours"
        else:
            days = hours / 24
            return f"{days:.1f} days"


def create_spatial_mapper(db: CodexDatabase) -> SpatialMapper:
    """Factory function to create a spatial mapper"""
    return SpatialMapper(db)
