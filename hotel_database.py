"""SQLite-хранилище каталога отелей Zari Travel.

Важно: initialize_database() всегда полностью пересобирает таблицу из
переданных Python-моделей (DROP + INSERT). Раньше здесь была ветка,
которая при непустой таблице лишь обновляла room_options_json у совпавших
по имени строк и ничего не делала с остальными полями — из-за этого старые
записи (в том числе дубли-"варианты") накапливались в zari_travel.db и не
исчезали даже после исправления генератора данных в hotel_search.py.
Полный пересбор при каждом старте устраняет этот класс багов: код и файл
БД больше не могут расходиться.
"""

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
    """Открывает SQLite-соединение с доступом к строкам по именам полей."""

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def reset_database() -> None:
    """Удаляет локальный файл БД, чтобы гарантировать чистый пересбор."""

    if not DATABASE_PATH.exists():
        return

    try:
        DATABASE_PATH.unlink()
    except PermissionError:
        # В Windows процесс может держать БД открытой во время повторного старта
        # dev-сервера. В таком случае безопаснее не падать, а оставить текущую
        # БД и повторно инициализировать таблицу на уровне SQL ниже.
        return


def initialize_database(hotels: Iterable[Any]) -> None:
    """Создает таблицу и полностью заполняет ее каталогом из Python-моделей."""

    hotels = list(hotels)
    with _connection() as connection:
        connection.execute(CREATE_HOTELS_TABLE)
        for statement in CREATE_INDEXES:
            connection.execute(statement)
        connection.execute("DELETE FROM hotels")
        connection.executemany(
            """
            INSERT INTO hotels (
                hotel_id, hotel_name, country, country_city, image_url, stars,
                meal_type, package_price_kzt, rating, reviews_count,
                seats_flight, seats_hotel, amenities_json, pros_json, cons_json,
                departure_cities_json, max_guests, summary, room_options_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    hotel.id,
                    hotel.hotel_name,
                    hotel.country,
                    hotel.country_city,
                    hotel.image_url,
                    hotel.stars,
                    hotel.meal_type.value,
                    hotel.package_price_kzt,
                    hotel.rating,
                    hotel.reviews_count,
                    hotel.seats_flight,
                    hotel.seats_hotel,
                    json.dumps([item.value for item in hotel.amenities], ensure_ascii=False),
                    json.dumps(hotel.pros, ensure_ascii=False),
                    json.dumps(hotel.cons, ensure_ascii=False),
                    json.dumps(hotel.departure_cities, ensure_ascii=False),
                    hotel.max_guests,
                    hotel.summary,
                    json.dumps(
                        [room.model_dump(mode="json") for room in hotel.room_options],
                        ensure_ascii=False,
                    ),
                )
                for hotel in hotels
            ],
        )


def count_hotels() -> int:
    """Возвращает количество записей в каталоге."""

    with _connection() as connection:
        return connection.execute("SELECT COUNT(*) FROM hotels").fetchone()[0]


def countries_counts() -> dict[str, int]:
    """Возвращает распределение отелей по странам (для проверки на дубли)."""

    with _connection() as connection:
        rows = connection.execute(
            "SELECT country, COUNT(*) count FROM hotels GROUP BY country ORDER BY country"
        ).fetchall()
    return {row["country"]: row["count"] for row in rows}


def search_database(request: Any) -> List[sqlite3.Row]:
    """Фильтрует каталог SQL-запросом по параметрам пользователя."""

    conditions = [
        "EXISTS (SELECT 1 FROM json_each(h.departure_cities_json) WHERE value = ?)",
        "ROUND(h.package_price_kzt * ? / 7.0) <= ?",
        "? <= h.max_guests",
    ]
    parameters: list[Any] = [
        request.city_from,
        request.nights,
        request.budget_kzt,
        request.adults + request.children,
    ]

    if request.country:
        conditions.append("h.country = ?")
        parameters.append(request.country)
    if request.stars is not None:
        conditions.append("h.stars >= ?")
        parameters.append(request.stars)
    if request.meal_type is not None:
        conditions.append("h.meal_type = ?")
        parameters.append(request.meal_type.value)
    for amenity in request.amenities:
        conditions.append(
            "EXISTS (SELECT 1 FROM json_each(h.amenities_json) WHERE value = ?)"
        )
        parameters.append(amenity.value)

    query = f"""
        SELECT h.*, ROUND(h.package_price_kzt * ? / 7.0) AS total_price_kzt
        FROM hotels h
        WHERE {' AND '.join(conditions)}
        ORDER BY h.rating DESC, total_price_kzt ASC
    """
    parameters.insert(0, request.nights)
    with _connection() as connection:
        return connection.execute(query, parameters).fetchall()
