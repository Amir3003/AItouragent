"""SQLite storage for VoyageAI: Autonomous Travel Concierge catalog."""

import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable, List


DATABASE_PATH = Path(__file__).resolve().parent / "zari_travel.db"


CREATE_HOTELS_TABLE = """
CREATE TABLE IF NOT EXISTS hotels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hotel_id TEXT NOT NULL UNIQUE,
    hotel_name TEXT NOT NULL,
    country TEXT NOT NULL,
    country_city TEXT NOT NULL,
    image_url TEXT NOT NULL,
    gallery_images_json TEXT NOT NULL DEFAULT '[]',
    stars INTEGER NOT NULL CHECK (stars BETWEEN 3 AND 5),
    meal_type TEXT NOT NULL,
    package_price_kzt INTEGER NOT NULL CHECK (package_price_kzt > 0),
    rating REAL NOT NULL CHECK (rating BETWEEN 0 AND 5),
    reviews_count INTEGER NOT NULL DEFAULT 0,
    seats_flight TEXT NOT NULL,
    seats_hotel TEXT NOT NULL,
    amenities_json TEXT NOT NULL,
    pros_json TEXT NOT NULL,
    cons_json TEXT NOT NULL,
    departure_cities_json TEXT NOT NULL,
    max_guests INTEGER NOT NULL,
    summary TEXT NOT NULL,
    room_options_json TEXT NOT NULL DEFAULT '[]'
)
"""

CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_hotels_country ON hotels(country)",
    "CREATE INDEX IF NOT EXISTS idx_hotels_price ON hotels(package_price_kzt)",
]


def _connection() -> sqlite3.Connection:
    """Opens SQLite connection with row factory for column-name access."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def reset_database() -> None:
    """Removes local DB file to ensure clean database rebuild."""
    if not DATABASE_PATH.exists():
        return
    try:
        DATABASE_PATH.unlink()
    except PermissionError:
        # On Windows, keep existing file and let SQL tables recreate
        return


def initialize_database(hotels: Iterable[Any]) -> None:
    """Creates tables and populates with verified VoyageAI catalog."""
    hotels = list(hotels)
    with _connection() as connection:
        connection.execute(CREATE_HOTELS_TABLE)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                data TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        for statement in CREATE_INDEXES:
            connection.execute(statement)
        connection.execute("DELETE FROM hotels")
        connection.executemany(
            """
            INSERT INTO hotels (
                hotel_id, hotel_name, country, country_city, image_url, gallery_images_json,
                stars, meal_type, package_price_kzt, rating, reviews_count,
                seats_flight, seats_hotel, amenities_json, pros_json, cons_json,
                departure_cities_json, max_guests, summary, room_options_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    hotel.id,
                    hotel.hotel_name,
                    hotel.country,
                    hotel.country_city,
                    hotel.image_url,
                    json.dumps(getattr(hotel, "gallery_images", [hotel.image_url]), ensure_ascii=False),
                    hotel.stars,
                    hotel.meal_type.value if hasattr(hotel.meal_type, "value") else str(hotel.meal_type),
                    hotel.package_price_kzt,
                    hotel.rating,
                    hotel.reviews_count,
                    hotel.seats_flight,
                    hotel.seats_hotel,
                    json.dumps([item.value if hasattr(item, "value") else str(item) for item in hotel.amenities], ensure_ascii=False),
                    json.dumps(hotel.pros, ensure_ascii=False),
                    json.dumps(hotel.cons, ensure_ascii=False),
                    json.dumps(hotel.departure_cities, ensure_ascii=False),
                    hotel.max_guests,
                    hotel.summary,
                    json.dumps(
                        [room.model_dump(mode="json") if hasattr(room, "model_dump") else room for room in hotel.room_options],
                        ensure_ascii=False,
                    ),
                )
                for hotel in hotels
            ],
        )


def count_hotels() -> int:
    """Returns total number of properties in the catalog."""
    with _connection() as connection:
        return connection.execute("SELECT COUNT(*) FROM hotels").fetchone()[0]


def countries_counts() -> dict[str, int]:
    """Returns distribution of properties across destinations."""
    with _connection() as connection:
        rows = connection.execute(
            "SELECT country, COUNT(*) as count FROM hotels GROUP BY country ORDER BY country"
        ).fetchall()
    return {row["country"]: row["count"] for row in rows}


def search_database(request: Any) -> List[sqlite3.Row]:
    """Filters catalog via SQL according to travel parameters."""
    conditions = [
        "(EXISTS (SELECT 1 FROM json_each(h.departure_cities_json) WHERE LOWER(value) = LOWER(?)) OR ? = '' OR ? IS NULL)",
        "ROUND(h.package_price_kzt * ? / 7.0) <= ?",
        "? <= h.max_guests",
    ]
    city = request.city_from or ""
    parameters: list[Any] = [
        city,
        city,
        city,
        request.nights,
        request.budget_kzt,
        request.adults + request.children,
    ]

    if request.country:
        conditions.append("(LOWER(h.country) = LOWER(?) OR LOWER(h.country_city) LIKE LOWER(?))")
        parameters.append(request.country)
        parameters.append(f"%{request.country}%")
    if request.stars is not None:
        conditions.append("h.stars >= ?")
        parameters.append(request.stars)
    if request.meal_type is not None:
        meal_val = request.meal_type.value if hasattr(request.meal_type, "value") else str(request.meal_type)
        conditions.append("h.meal_type = ?")
        parameters.append(meal_val)
    for amenity in request.amenities:
        amenity_val = amenity.value if hasattr(amenity, "value") else str(amenity)
        conditions.append(
            "EXISTS (SELECT 1 FROM json_each(h.amenities_json) WHERE LOWER(value) = LOWER(?))"
        )
        parameters.append(amenity_val)

    query = f"""
        SELECT h.*, ROUND(h.package_price_kzt * ? / 7.0) AS total_price_kzt
        FROM hotels h
        WHERE {' AND '.join(conditions)}
        ORDER BY h.rating DESC, total_price_kzt ASC
    """
    parameters.insert(0, request.nights)
    with _connection() as connection:
        return connection.execute(query, parameters).fetchall()
