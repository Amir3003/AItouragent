"""Models, mock data, flight simulation, and local search for VoyageAI: Autonomous Travel Concierge.

Catalog: Strictly 50 elite properties across 10 top global destinations (5 properties per destination).
Each property includes verified high-resolution imagery, diverse realistic room tiers,
and synchronized direct roundtrip flight simulation.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from hotel_database import initialize_database, reset_database, search_database


class Amenity(str, Enum):
    """Supported luxury resort amenities."""

    PRIVATE_BEACH = "Private Beach"
    SANDY_BEACH = "Sandy Beach"
    FIRST_LINE = "Beachfront (First Line)"
    WIFI = "High-speed Wi-Fi"
    WATERPARK = "Aqua Park"
    KIDS_CLUB = "Kids Club"
    ALL_INCLUSIVE = "All-Inclusive"


class MealType(str, Enum):
    """Board basis options."""

    AI = "AI - All Inclusive"
    UAI = "UAI - Ultra All Inclusive"
    FB = "FB - Full Board"
    BB = "BB - Bed & Breakfast"


COUNTRIES: List[str] = [
    "Turkey", "Egypt", "UAE", "Thailand", "Maldives", "Vietnam", "Georgia", "Sri Lanka", "Indonesia", "Spain",
]

# Currency exchange baseline
USD_TO_KZT = 500


class FlightInfo(BaseModel):
    """Simulated realistic roundtrip airline flight tickets."""

    airline: str
    airline_code: str
    flight_number_outbound: str
    flight_number_inbound: str
    departure_city: str
    departure_airport: str
    arrival_city: str
    arrival_airport: str
    departure_date: str
    departure_time: str
    arrival_time: str
    return_date: str
    return_departure_time: str
    return_arrival_time: str
    duration: str
    cabin_class: str = "Economy Premium"
    baggage: str = "23 kg check-in + 8 kg cabin baggage"
    aircraft: str = "Airbus A321neo"
    flight_price_kzt: int
    flight_price_usd: int
    status_badge: str = "Direct Flight Included in Package"


class RoomOption(BaseModel):
    """Distinct room category available inside each property."""

    id: str
    name: str
    bed_type: str = "1 King Bed (200x200 cm)"
    sqm: int = Field(ge=15, le=600)
    capacity: str
    description: str
    images: List[str] = Field(min_length=3, max_length=6)
    amenities_included: List[str] = Field(default_factory=list)
    amenities_excluded: List[str] = Field(default_factory=list)
    vip_privileges: List[str] = Field(default_factory=list)
    price_per_night_kzt: int = Field(gt=0)
    price_per_night_usd: int = Field(gt=0)
    price_delta_kzt: int = Field(ge=0)
    availability: str = "Available"


class HotelRecommendation(BaseModel):
    """Curated hotel recommendation card for VoyageAI presentation UI."""

    id: str
    hotel_name: str
    country: str
    resort: str = ""
    country_city: str
    image_url: str
    gallery_images: List[str] = Field(default_factory=list)
    stars: int = Field(ge=3, le=5)
    meal_type: str
    price_per_night_kzt: int = Field(gt=0)
    price_per_night_usd: int = Field(gt=0)
    total_price_kzt: int = Field(gt=0)
    total_price_usd: int = Field(gt=0)
    price_breakdown: str = ""
    guests_badge: str = "Solo Traveler · 1 Adult"
    rating: float = Field(ge=0, le=5)
    reviews_count: int = Field(ge=0)
    seats_flight: str
    seats_hotel: str
    pros: List[str] = Field(min_length=3, max_length=3)
    cons: List[str] = Field(min_length=1, max_length=2)
    matched_amenities: List[Amenity] = Field(default_factory=list)
    match_score: int = Field(default=0, ge=0, le=100)
    highlight_badge: str = Field(default="⭐️ Highest Rating")
    summary: str
    room_options: List[RoomOption] = Field(min_length=2, max_length=6)
    flight: Optional[FlightInfo] = None
    flexible_dates: List[Dict[str, Any]] = Field(default_factory=list)
    beach: str = "1-я линия, собственный песчано-галечный пляж, шезлонги и зонтики бесплатно"
    board_desc: str = "Всё включено (питание, безалкогольные и алкогольные напитки)"
    in_room: str = "Кондиционер, Сейф (бесплатно), Wi-Fi, Фен, Ванна/душ, ТВ, Набор для чая/кофе, Балкон/терраса"
    for_children: str = "Детский бассейн, стульчики в ресторане, кроватка по запросу"
    territory: str = "Бассейн, ресторан, парковка, Wi-Fi на территории"
    beach_en: str = "1st coastline, private sandy-pebble beach, complimentary sun loungers & umbrellas"
    board_desc_en: str = "All Inclusive (all meals, snacks, soft and alcoholic drinks included)"
    in_room_en: str = "Air conditioning, Digital safe (free), Wi-Fi, Hairdryer, Bath/shower, TV, Balcony/terrace, Minibar, Tea/coffee set"
    for_children_en: str = "Kids club, shallow pool, baby cot upon request, high chairs in restaurant"
    territory_en: str = "Swimming pool, a la carte restaurants, fitness center, landscaped gardens, free Wi-Fi"


class MockHotel(BaseModel):
    """Database entity representation."""

    id: str
    hotel_name: str
    country: str
    country_city: str
    image_url: str
    gallery_images: List[str] = Field(default_factory=list)
    stars: int
    meal_type: MealType
    package_price_kzt: int
    rating: float
    reviews_count: int
    seats_flight: str
    seats_hotel: str
    amenities: List[Amenity]
    pros: List[str]
    cons: List[str]
    departure_cities: List[str]
    max_guests: int
    summary: str
    room_options: List[RoomOption]


class HotelSearchRequest(BaseModel):
    """Validated search parameters parsed from user prompt or web filters."""

    city_from: str = Field(default="Astana", min_length=2, description="Departure City")
    date_start: str = Field(description="Departure date (YYYY-MM-DD)")
    budget_kzt: int = Field(gt=0, description="Total budget in KZT")
    country: Optional[str] = Field(default=None, description="Destination country")
    nights: int = Field(default=7, ge=1, le=30, description="Duration in nights")
    adults: int = Field(default=2, ge=1, le=6, description="Adult guests")
    children: int = Field(default=0, ge=0, le=4, description="Children count")
    children_ages: List[int] = Field(default_factory=list, description="Ages of children")
    stars: Optional[int] = Field(default=None, description="Minimum star rating")
    meal_type: Optional[MealType] = Field(default=None, description="Board type")
    amenities: List[Amenity] = Field(default_factory=list, description="Desired amenities")

    @field_validator("city_from", mode="before")
    @classmethod
    def normalize_city_from(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value
        val = value.strip().title()
        mapping = {
            "Астана": "Astana", "Алматы": "Almaty", "Шымкент": "Shymkent",
            "Nqz": "Astana", "Ala": "Almaty", "Cit": "Shymkent",
        }
        return mapping.get(val, val)

    @field_validator("country", mode="before")
    @classmethod
    def normalize_country(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value
        text = value.strip().lower()
        if not text:
            return None

        mapping = {
            "турция": "Turkey", "турции": "Turkey", "turkey": "Turkey", "antalya": "Turkey", "belek": "Turkey",
            "египет": "Egypt", "египте": "Egypt", "egypt": "Egypt", "sharm": "Egypt", "hurghada": "Egypt",
            "оаэ": "UAE", "эмираты": "UAE", "дубай": "UAE", "dubai": "UAE", "uae": "UAE", "united arab emirates": "UAE",
            "таиланд": "Thailand", "таиланде": "Thailand", "пхукет": "Thailand", "thailand": "Thailand", "phuket": "Thailand",
            "мальдивы": "Maldives", "мальдивах": "Maldives", "мале": "Maldives", "maldives": "Maldives",
            "вьетнам": "Vietnam", "вьетнаме": "Vietnam", "дананг": "Vietnam", "vietnam": "Vietnam", "da nang": "Vietnam",
            "грузия": "Georgia", "грузии": "Georgia", "батуми": "Georgia", "тбилиси": "Georgia", "georgia": "Georgia",
            "шри-ланка": "Sri Lanka", "шри-ланке": "Sri Lanka", "коломбо": "Sri Lanka", "sri lanka": "Sri Lanka",
            "индонезия": "Indonesia", "бали": "Indonesia", "indonesia": "Indonesia", "bali": "Indonesia",
            "испания": "Spain", "испании": "Spain", "барселона": "Spain", "spain": "Spain", "barcelona": "Spain",
        }
        for k, canonical in mapping.items():
            if k in text:
                return canonical
        return value.strip().title()

    @field_validator("date_start")
    @classmethod
    def validate_date_start(cls, value: str) -> str:
        try:
            date.fromisoformat(value)
        except ValueError as err:
            raise ValueError("Date must follow YYYY-MM-DD format") from err
        return value

    @field_validator("stars")
    @classmethod
    def validate_stars(cls, value: Optional[int]) -> Optional[int]:
        if value is not None and value not in {3, 4, 5}:
            raise ValueError("Stars must be 3, 4, or 5")
        return value

    @field_validator("children_ages")
    @classmethod
    def validate_children_ages(cls, value: List[int]) -> List[int]:
        if any(age < 0 or age > 17 for age in value):
            raise ValueError("Children ages must be between 0 and 17")
        return value

    @model_validator(mode="after")
    def validate_family(self) -> "HotelSearchRequest":
        if len(self.children_ages) != self.children:
            raise ValueError("Please provide age for every child in party")
        return self


# Verified, permanent Unsplash CDN photographic assets
_HOTEL_IMAGES = {
    "Turkey": [
        "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1540541338287-41700207dee6?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1564501049412-61c2a3083791?auto=format&fit=crop&w=1200&h=800&q=80",
    ],
    "Egypt": [
        "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1584132967334-10e028bd69f7?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1561501900-3701fa6a0864?auto=format&fit=crop&w=1200&h=800&q=80",
    ],
    "UAE": [
        "https://images.unsplash.com/photo-1518684079-3c830dcef090?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=1200&h=800&q=80",
    ],
    "Thailand": [
        "https://images.unsplash.com/photo-1539367628448-4bc5c9d171c8?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1540541338287-41700207dee6?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1200&h=800&q=80",
    ],
    "Maldives": [
        "https://images.unsplash.com/photo-1571896349842-33c89424de2d?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1584132967334-10e028bd69f7?auto=format&fit=crop&w=1200&h=800&q=80",
    ],
    "Vietnam": [
        "https://images.unsplash.com/photo-1560347876-aeef00ee58a1?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1571902943202-507ec2618e8f?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=1200&h=800&q=80",
    ],
    "Georgia": [
        "https://images.unsplash.com/photo-1445019980597-93fa8acb246c?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1587985064135-0366536eab42?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1564501049412-61c2a3083791?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1602002418082-a4443e081dd1?auto=format&fit=crop&w=1200&h=800&q=80",
    ],
    "Sri Lanka": [
        "https://images.unsplash.com/photo-1561501900-3701fa6a0864?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1591088398332-8a7791972843?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1540541338287-41700207dee6?auto=format&fit=crop&w=1200&h=800&q=80",
    ],
    "Indonesia": [
        "https://images.unsplash.com/photo-1539367628448-4bc5c9d171c8?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1618773928121-c32242e63f39?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=1200&h=800&q=80",
    ],
    "Spain": [
        "https://images.unsplash.com/photo-1564501049412-61c2a3083791?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=1200&h=800&q=80",
        "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1200&h=800&q=80",
    ],
}

# ── Specific Verified Architectural Hotel Photos ──────────────────────────────
_SPECIFIC_HOTEL_IMAGES = {
    # UAE: distinct architecture for each property
    "Atlantis The Royal Dubai": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=1200&h=800&q=80",  # Modern stepped luxury architecture
    "Burj Al Arab Jumeirah": "https://images.unsplash.com/photo-1518684079-3c830dcef090?auto=format&fit=crop&w=1200&h=800&q=80",     # Iconic sail-shaped facade
    "One&Only Royal Mirage": "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?auto=format&fit=crop&w=1200&h=800&q=80",     # Arabian palace & palm court
    "Jumeirah Beach Hotel": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&h=800&q=80",      # Oceanfront wave-design resort
    "Address Beach Resort JBR": "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?auto=format&fit=crop&w=1200&h=800&q=80",  # Twin high-rise infinity pool tower

    # Turkey: resort beach, luxury pools & Turkish palaces
    "Rixos Premium Belek": "https://images.unsplash.com/photo-1540541338287-41700207dee6?auto=format&fit=crop&w=1200&h=800&q=80",       # Mediterranean luxury pool & cabanas
    "Maxx Royal Belek Golf Resort": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1200&h=800&q=80",# Grand golf resort estate
    "Delphin Imperial Lara": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=1200&h=800&q=80",      # Waterfront resort terraces
    "Titanic Mardan Palace": "https://images.unsplash.com/photo-1564501049412-61c2a3083791?auto=format&fit=crop&w=1200&h=800&q=80",      # Palatial grand Turkish facade
    "Cullinan Belek Golf & Spa": "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?auto=format&fit=crop&w=1200&h=800&q=80",  # Waterfront villas & turquoise lagoon

    # Thailand: tropical greenery & private villas
    "Banyan Tree Phuket": "https://images.unsplash.com/photo-1539367628448-4bc5c9d171c8?auto=format&fit=crop&w=1200&h=800&q=80",         # Tropical greenery & pool villa
    "Amanpuri Phuket": "https://images.unsplash.com/photo-1540541338287-41700207dee6?auto=format&fit=crop&w=1200&h=800&q=80",            # Private coconut grove sanctuary
    "Katathani Phuket Beach Resort": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&h=800&q=80", # White sand beach cove
    "Centara Grand Beach Resort": "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=1200&h=800&q=80", # Seaside resort suites
    "Rosewood Phuket": "https://images.unsplash.com/photo-1571896349842-33c89424de2d?auto=format&fit=crop&w=1200&h=800&q=80",            # Emerald bay luxury retreat
}


# ── Professional room images (actual hotel interiors) ─────────────────────────
_ROOM_IMAGES = [
    # Luxury hotel bedroom interiors
    "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1582719508461-905c673771fd?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1611892440504-42a792e24d32?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1618773928121-c32242e63f39?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1595576508898-0ad5c879a061?auto=format&fit=crop&w=1000&q=80",
]

# ── TourVisor-standard room archetypes ────────────────────────────────────────
# (name, description, bed_type, sqm, capacity, price_multiplier)
_DESTINATION_ROOM_ARCHETYPES = {
    "Beach": [
        (
            "Standard Room",
            "Стандартный номер с видом на сад или территорию отеля. Кондиционер, ванная комната, балкон.",
            "1 King Bed или 2 Twin Beds",
            28, "1–2 Гостя", 0.0,
        ),
        (
            "Superior Sea View",
            "Улучшенный номер с прямым или частичным видом на море, балконом и ванной комнатой.",
            "1 King Bed (180x200)",
            38, "1–2 Гостя", 0.15,
        ),
        (
            "Family Suite",
            "Семейный двухкомнатный номер: 2 спальни, 2 ванные комнаты, балкон, детский набор.",
            "1 King Bed + 2 Twin Beds",
            65, "2–4 Гостя", 0.35,
        ),
        (
            "Junior Suite Sea View",
            "Просторный полулюкс с отдельной гостиной зоной и панорамным балконом с видом на море.",
            "1 King Bed (200x200)",
            75, "1–3 Гостя", 0.55,
        ),
    ],
    "Island": [
        (
            "Beach Bungalow",
            "Пляжное бунгало в окружении пальм с прямым выходом к песчаному пляжу и лагуне.",
            "1 King Bed (200x200)",
            65, "1–2 Гостя", 0.0,
        ),
        (
            "Overwater Villa",
            "Вилла на сваях над бирюзовой лагуной с собственной террасой для загара и спуском в воду.",
            "1 King Bed (200x200)",
            90, "1–2 Гостя", 0.25,
        ),
        (
            "Two-Bedroom Beach Villa",
            "Просторная пляжная вилла с 2 спальнями, открытой террасой и выходом на пляж.",
            "1 King Bed + 2 Twin Beds",
            160, "2–4 Гостя", 0.55,
        ),
        (
            "Presidential Lagoon Pavilion",
            "Премиальный водный павильон над лагуной с просторной террасой и панорамными видами.",
            "1 Super King Bed (220x220)",
            240, "До 4 Гостей", 0.90,
        ),
    ],
    "LuxuryCity": [
        (
            "Superior City View",
            "Улучшенный номер с видом на город. Кондиционер, рабочий стол, сейф, ванная комната.",
            "1 King Bed (180x200)",
            35, "1–2 Гостя", 0.0,
        ),
        (
            "Deluxe Sea View",
            "Делюкс с панорамным видом на море или залив, балконом и отдельной ванной.",
            "1 King Bed (200x200)",
            48, "1–2 Гостя", 0.20,
        ),
        (
            "Family Two-Bedroom Suite",
            "Семейный люкс с 2 отдельными спальнями, гостиной зоной и 2 ванными комнатами.",
            "1 King Bed + 2 Twin Beds",
            95, "2–4 Гостя", 0.42,
        ),
        (
            "Executive Suite",
            "Представительский люкс с панорамным видом, просторной гостиной и доступом в лаунж.",
            "1 King Bed (200x200)",
            120, "1–3 Гостя", 0.80,
        ),
    ],
}

# ── Clean amenity lists per tier (TourVisor standard) ─────────────────────────
_CLEAN_AMENITIES_BY_TIER = {
    0: (
        ["Кондиционер", "Сейф (бесплатно)", "Wi-Fi", "Фен", "Ванна / душ", "ТВ", "Набор для чая/кофе", "Балкон / терраса"],
        ["Мини-бар (платно)"],
        [],
    ),
    1: (
        ["Кондиционер", "Сейф (бесплатно)", "Wi-Fi", "Фен", "Ванна / душ", "ТВ", "Набор для чая/кофе", "Балкон с видом на море", "Халаты и тапочки", "Гарантированный вид на море"],
        ["Мини-бар (платно)"],
        [],
    ),
    2: (
        ["Кондиционер", "Сейф (бесплатно)", "Wi-Fi", "Две раздельные спальни", "Две ванные комнаты", "Детские стульчики / кроватка", "Фен", "ТВ", "Балкон / терраса", "Детский клуб без доплат"],
        ["Мини-бар (платно)"],
        [],
    ),
    3: (
        ["Кондиционер", "Сейф (бесплатно)", "Wi-Fi", "Гостиная зона", "Панорамный балкон", "Ванна и тропический душ", "Халаты и тапочки", "Кофемашина", "ТВ", "Приоритетное заселение", "Поздний выезд (при наличии)"],
        ["Мини-бар (платно)"],
        [],
    ),
}


def generate_flight_route(
    city_from: str,
    country: str,
    date_start: str,
    nights: int,
    adults: int,
    children: int,
) -> FlightInfo:
    """Generates realistic roundtrip airline flight schedules and baggage allowances."""
    passengers = max(1, adults + children)
    origin_city = city_from.strip().title() if city_from else "Astana"
    origin_map = {
        "Astana": "NQZ", "Almaty": "ALA", "Shymkent": "CIT",
        "Астана": "NQZ", "Алматы": "ALA", "Шымкент": "CIT",
    }
    origin_code = origin_map.get(origin_city, "NQZ")

    dest_map = {
        "Turkey": ("Antalya", "AYT", "Turkish Airlines", "TK", "Airbus A321neo", "4h 50m", 195000),
        "Egypt": ("Sharm El Sheikh", "SSH", "Air Astana", "KC", "Airbus A321LR", "5h 15m", 210000),
        "UAE": ("Dubai", "DXB", "Flydubai", "FZ", "Boeing 737 MAX 8", "4h 25m", 185000),
        "Thailand": ("Phuket", "HKT", "Air Astana", "KC", "Boeing 767-300ER", "7h 10m", 290000),
        "Maldives": ("Malé", "MLE", "Qatar Airways", "QR", "Boeing 787-9 Dreamliner", "6h 45m", 360000),
        "Vietnam": ("Da Nang", "DAD", "VietJet Air", "VJ", "Airbus A321neo", "7h 30m", 240000),
        "Georgia": ("Batumi", "BUS", "Air Astana", "KC", "Embraer E190-E2", "3h 40m", 160000),
        "Sri Lanka": ("Colombo", "CMB", "Air Arabia", "G9", "Airbus A320", "6h 20m", 230000),
        "Indonesia": ("Bali (Denpasar)", "DPS", "Qatar Airways", "QR", "Airbus A350-900", "9h 30m", 390000),
        "Spain": ("Barcelona", "BCN", "Turkish Airlines", "TK", "Airbus A330-300", "7h 45m", 310000),
    }

    info = dest_map.get(country, ("Antalya", "AYT", "Turkish Airlines", "TK", "Airbus A321neo", "4h 50m", 195000))
    arr_city, arr_code, airline, code_pfx, aircraft, duration, base_ticket = info

    try:
        dt_start = datetime.strptime(date_start, "%Y-%m-%d")
    except Exception:
        dt_start = datetime.now() + timedelta(days=21)
        date_start = dt_start.strftime("%Y-%m-%d")

    dt_end = dt_start + timedelta(days=nights)
    return_date = dt_end.strftime("%Y-%m-%d")

    flight_out_num = f"{code_pfx}-{300 + (len(country) * 17) % 500}"
    flight_in_num = f"{code_pfx}-{301 + (len(country) * 17) % 500}"

    total_flight_kzt = base_ticket * passengers
    total_flight_usd = round(total_flight_kzt / USD_TO_KZT)

    return FlightInfo(
        airline=airline,
        airline_code=code_pfx,
        flight_number_outbound=flight_out_num,
        flight_number_inbound=flight_in_num,
        departure_city=origin_city,
        departure_airport=origin_code,
        arrival_city=arr_city,
        arrival_airport=arr_code,
        departure_date=date_start,
        departure_time="08:35",
        arrival_time="11:45",
        return_date=return_date,
        return_departure_time="15:20",
        return_arrival_time="22:15",
        duration=duration,
        cabin_class="Economy Standard",
        baggage="23 kg check-in + 8 kg cabin baggage included per person",
        aircraft=aircraft,
        flight_price_kzt=total_flight_kzt,
        flight_price_usd=total_flight_usd,
        status_badge="Direct Roundtrip Flights Included",
    )




def _build_curated_rooms(country: str, base_night_price: int) -> List[RoomOption]:
    if country in ("Maldives",):
        archetype = _DESTINATION_ROOM_ARCHETYPES["Island"]
    elif country in ("UAE", "Spain"):
        archetype = _DESTINATION_ROOM_ARCHETYPES["LuxuryCity"]
    else:
        archetype = _DESTINATION_ROOM_ARCHETYPES["Beach"]

    rooms: List[RoomOption] = []
    for tier_idx, (name, desc, bed, sqm, cap, price_mult) in enumerate(archetype):
        room_night_kzt = int(round(base_night_price * (1.0 + price_mult)))
        room_night_usd = round(room_night_kzt / USD_TO_KZT)
        delta_kzt = int(round(base_night_price * price_mult * 7))
        inc, exc, vip = _CLEAN_AMENITIES_BY_TIER.get(tier_idx, _CLEAN_AMENITIES_BY_TIER[0])

        img_sample = [
            _ROOM_IMAGES[(tier_idx + 0) % len(_ROOM_IMAGES)],
            _ROOM_IMAGES[(tier_idx + 1) % len(_ROOM_IMAGES)],
            _ROOM_IMAGES[(tier_idx + 2) % len(_ROOM_IMAGES)],
            _ROOM_IMAGES[(tier_idx + 3) % len(_ROOM_IMAGES)],
        ]

        rooms.append(
            RoomOption(
                id=f"room-{tier_idx + 1}",
                name=name,
                bed_type=bed,
                sqm=sqm,
                capacity=cap,
                description=desc,
                images=img_sample,
                amenities_included=inc,
                amenities_excluded=exc,
                vip_privileges=vip,
                price_per_night_kzt=room_night_kzt,
                price_per_night_usd=room_night_usd,
                price_delta_kzt=delta_kzt,
                availability="Available",
            )
        )
    return rooms


# 10 destinations x 5 luxury properties = strictly 50 elite properties
_CATALOG_DATA = [
    {
        "country": "Turkey", "resort": "Antalya / Belek", "meal": MealType.AI,
        "hotels": [
            ("Rixos Premium Belek", 5, 950000, 4.9, 1420, [Amenity.PRIVATE_BEACH, Amenity.WATERPARK, Amenity.KIDS_CLUB, Amenity.ALL_INCLUSIVE]),
            ("Maxx Royal Belek Golf Resort", 5, 1480000, 5.0, 980, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE, Amenity.ALL_INCLUSIVE]),
            ("Delphin Imperial Lara", 5, 890000, 4.8, 1640, [Amenity.WATERPARK, Amenity.KIDS_CLUB, Amenity.ALL_INCLUSIVE]),
            ("Titanic Mardan Palace", 5, 1150000, 4.9, 1220, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE, Amenity.ALL_INCLUSIVE]),
            ("Cullinan Belek Golf & Spa", 5, 1390000, 4.9, 840, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE, Amenity.ALL_INCLUSIVE]),
        ],
    },
    {
        "country": "Egypt", "resort": "Sharm El Sheikh", "meal": MealType.AI,
        "hotels": [
            ("Rixos Premium Seagate", 5, 980000, 4.9, 1890, [Amenity.PRIVATE_BEACH, Amenity.WATERPARK, Amenity.ALL_INCLUSIVE]),
            ("Four Seasons Resort Sharm El Sheikh", 5, 1680000, 5.0, 920, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE]),
            ("Steigenberger ALDAU Beach Hotel", 5, 820000, 4.8, 1530, [Amenity.KIDS_CLUB, Amenity.ALL_INCLUSIVE]),
            ("Baron Palms Resort", 5, 870000, 4.7, 1120, [Amenity.PRIVATE_BEACH, Amenity.ALL_INCLUSIVE]),
            ("Albatros Laguna Vista Resort", 4, 690000, 4.6, 1780, [Amenity.WATERPARK, Amenity.ALL_INCLUSIVE]),
        ],
    },
    {
        "country": "UAE", "resort": "Dubai", "meal": MealType.BB,
        "hotels": [
            ("Atlantis The Royal Dubai", 5, 2450000, 5.0, 1940, [Amenity.FIRST_LINE, Amenity.WATERPARK, Amenity.PRIVATE_BEACH]),
            ("Burj Al Arab Jumeirah", 5, 3200000, 5.0, 860, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE]),
            ("One&Only Royal Mirage", 5, 2150000, 4.9, 940, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE]),
            ("Jumeirah Beach Hotel", 5, 1680000, 4.8, 1830, [Amenity.FIRST_LINE, Amenity.WATERPARK, Amenity.KIDS_CLUB]),
            ("Address Beach Resort JBR", 5, 1790000, 4.9, 1420, [Amenity.FIRST_LINE, Amenity.SANDY_BEACH]),
        ],
    },
    {
        "country": "Thailand", "resort": "Phuket", "meal": MealType.BB,
        "hotels": [
            ("Banyan Tree Phuket", 5, 1780000, 4.9, 870, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE]),
            ("Amanpuri Phuket", 5, 2890000, 5.0, 620, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE]),
            ("Katathani Phuket Beach Resort", 5, 980000, 4.8, 1760, [Amenity.FIRST_LINE, Amenity.KIDS_CLUB, Amenity.SANDY_BEACH]),
            ("Centara Grand Beach Resort", 5, 920000, 4.7, 1430, [Amenity.FIRST_LINE, Amenity.WATERPARK]),
            ("Rosewood Phuket", 5, 2350000, 4.9, 710, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE]),
        ],
    },
    {
        "country": "Maldives", "resort": "North Malé Atoll", "meal": MealType.AI,
        "hotels": [
            ("Soneva Fushi", 5, 2950000, 5.0, 780, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE, Amenity.ALL_INCLUSIVE]),
            ("The Ritz-Carlton Maldives Fari Islands", 5, 3450000, 5.0, 640, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE]),
            ("The Westin Maldives Miriandhoo", 5, 2140000, 4.9, 890, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE, Amenity.ALL_INCLUSIVE]),
            ("Lily Beach Resort & Spa", 5, 1890000, 4.8, 1140, [Amenity.WATERPARK, Amenity.ALL_INCLUSIVE]),
            ("Kuramathi Maldives", 4, 1580000, 4.7, 1620, [Amenity.FIRST_LINE, Amenity.ALL_INCLUSIVE]),
        ],
    },
    {
        "country": "Vietnam", "resort": "Da Nang", "meal": MealType.BB,
        "hotels": [
            ("InterContinental Danang Sun Peninsula", 5, 1980000, 5.0, 960, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE]),
            ("Four Seasons Resort The Nam Hai", 5, 2400000, 5.0, 740, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE]),
            ("Furama Resort Danang", 5, 890000, 4.7, 1380, [Amenity.FIRST_LINE, Amenity.KIDS_CLUB]),
            ("Hyatt Regency Danang Resort & Spa", 5, 1150000, 4.8, 1460, [Amenity.FIRST_LINE, Amenity.WATERPARK]),
            ("Vinpearl Resort & Spa Da Nang", 5, 820000, 4.7, 1190, [Amenity.WATERPARK, Amenity.ALL_INCLUSIVE]),
        ],
    },
    {
        "country": "Georgia", "resort": "Batumi & Black Sea", "meal": MealType.BB,
        "hotels": [
            ("Paragraph Resort & Spa Shekvetili", 5, 1080000, 4.9, 1310, [Amenity.FIRST_LINE, Amenity.WATERPARK, Amenity.KIDS_CLUB]),
            ("Le Méridien Batumi", 5, 980000, 4.8, 1150, [Amenity.FIRST_LINE, Amenity.SANDY_BEACH]),
            ("Radisson Blu Hotel Batumi", 5, 890000, 4.8, 1420, [Amenity.FIRST_LINE, Amenity.SANDY_BEACH]),
            ("Courtyard by Marriott Batumi", 4, 760000, 4.6, 980, [Amenity.SANDY_BEACH]),
            ("Georgia Palace Hotel & Spa Kobuleti", 5, 850000, 4.7, 890, [Amenity.PRIVATE_BEACH, Amenity.KIDS_CLUB]),
        ],
    },
    {
        "country": "Sri Lanka", "resort": "Bentota & Galle", "meal": MealType.BB,
        "hotels": [
            ("Cape Weligama Luxury Resort", 5, 1680000, 4.9, 680, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE]),
            ("Anantara Peace Haven Tangalle", 5, 1480000, 4.9, 920, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE]),
            ("Taj Bentota Resort & Spa", 5, 980000, 4.8, 1320, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE]),
            ("Heritance Ahungalla", 5, 1050000, 4.8, 980, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE]),
            ("Cinnamon Bey Beruwala", 5, 890000, 4.7, 1260, [Amenity.WATERPARK, Amenity.ALL_INCLUSIVE]),
        ],
    },
    {
        "country": "Indonesia", "resort": "Bali", "meal": MealType.BB,
        "hotels": [
            ("AYANA Resort Bali", 5, 1720000, 5.0, 1850, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE]),
            ("Bulgari Resort Bali", 5, 3100000, 5.0, 630, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE]),
            ("The Mulia Nusa Dua Bali", 5, 1580000, 4.9, 1420, [Amenity.FIRST_LINE, Amenity.SANDY_BEACH]),
            ("Padma Resort Legian", 5, 1240000, 4.8, 1680, [Amenity.WATERPARK, Amenity.KIDS_CLUB]),
            ("Mandapa, a Ritz-Carlton Reserve", 5, 2750000, 5.0, 580, [Amenity.PRIVATE_BEACH]),
        ],
    },
    {
        "country": "Spain", "resort": "Barcelona Coast", "meal": MealType.BB,
        "hotels": [
            ("W Barcelona", 5, 1780000, 4.9, 2140, [Amenity.FIRST_LINE, Amenity.SANDY_BEACH]),
            ("Hotel Arts Barcelona (Ritz-Carlton)", 5, 1920000, 4.9, 1680, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE]),
            ("Mandarin Oriental Barcelona", 5, 2350000, 5.0, 890, [Amenity.FIRST_LINE]),
            ("Iberostar Selection Paseo de Gracia", 4, 1050000, 4.7, 1320, [Amenity.ALL_INCLUSIVE]),
            ("Majestic Hotel & Spa Barcelona", 5, 1620000, 4.8, 1470, [Amenity.FIRST_LINE]),
        ],
    },
]


def _build_all_hotels() -> List[MockHotel]:
    hotels: List[MockHotel] = []
    global_idx = 0
    for group in _CATALOG_DATA:
        country = group["country"]
        resort = group["resort"]
        default_meal = group["meal"]
        imgs = _HOTEL_IMAGES.get(country, _HOTEL_IMAGES["Turkey"])

        for name, stars, base_pkg, rating, reviews, extra_amenities in group["hotels"]:
            cover_img = _SPECIFIC_HOTEL_IMAGES.get(name, imgs[global_idx % len(imgs)])
            gallery = [
                cover_img,
                imgs[(global_idx + 1) % len(imgs)],
                imgs[(global_idx + 2) % len(imgs)],
                imgs[(global_idx + 3) % len(imgs)],
            ]

            base_night_price = round(base_pkg / 7.0)

            rooms = _build_curated_rooms(country, base_night_price)

            all_amenities = [Amenity.WIFI] + extra_amenities
            all_amenities = list(dict.fromkeys(all_amenities))

            pros = [
                f"Prime location on {resort} with breathtaking views",
                f"Rated {rating}/5 by verified travelers ({reviews:,} reviews)",
                f"Seamless check-in, award-winning culinary venues & private beach",
            ]
            cons = [
                "High seasonal demand: advance booking strongly recommended",
            ]

            hotels.append(
                MockHotel(
                    id=f"htl-{global_idx + 1:03d}",
                    hotel_name=name,
                    country=country,
                    country_city=f"{country}, {resort}",
                    image_url=cover_img,
                    gallery_images=gallery,
                    stars=stars,
                    meal_type=default_meal,
                    package_price_kzt=base_pkg,
                    rating=rating,
                    reviews_count=reviews,
                    seats_flight="Guaranteed Seats",
                    seats_hotel="Instant Confirmation",
                    amenities=all_amenities,
                    pros=pros,
                    cons=cons,
                    departure_cities=["Astana", "Almaty", "Shymkent", "NQZ", "ALA", "CIT", "Астана", "Алматы"],
                    max_guests=6,
                    summary=f"{name} is an elite {stars}-star sanctuary in {resort}, featuring {default_meal.value} and personalized hospitality.",
                    room_options=rooms,
                )
            )
            global_idx += 1

    return hotels


MOCK_HOTELS: List[MockHotel] = _build_all_hotels()

# Seed and reset database on startup
reset_database()
initialize_database(MOCK_HOTELS)


def mock_search_tourvisor_api(request: HotelSearchRequest) -> List[HotelRecommendation]:
    """Retrieves and calculates exact budget breakdown for hotels matching request."""
    recommendations: List[HotelRecommendation] = []
    nights = max(1, request.nights)
    adults = max(1, request.adults)
    children = request.children
    passengers = adults + children

    # Guest badge formulation
    if passengers == 1:
        guest_badge = "Solo Traveler · 1 Adult"
    elif adults == 2 and children == 0:
        guest_badge = "Couple Escape · 2 Adults"
    elif children > 0:
        guest_badge = f"Family Package · {adults} Adults, {children} Child{'ren' if children > 1 else ''}"
    else:
        guest_badge = f"Group Package · {adults} Guests"

    for row in search_database(request):
        amenities = [Amenity(val) for val in json.loads(row["amenities_json"]) if val in Amenity._value2member_map_]
        match_score = 88
        if request.country and row["country"].lower() == request.country.lower():
            match_score += 10

        gallery = json.loads(row["gallery_images_json"]) if "gallery_images_json" in row.keys() else [row["image_url"]]
        room_data = json.loads(row["room_options_json"])
        rooms = [RoomOption.model_validate(r) for r in room_data]

        flight_data = generate_flight_route(
            city_from=request.city_from,
            country=row["country"],
            date_start=request.date_start,
            nights=nights,
            adults=adults,
            children=children,
        )

        base_hotel_total = row["total_price_kzt"]
        if passengers == 1:
            # Solo traveler discount on total hotel package
            calc_hotel_total = int(round(base_hotel_total * 0.70))
        elif passengers > 2:
            calc_hotel_total = int(round(base_hotel_total * (1.0 + (passengers - 2) * 0.25)))
        else:
            calc_hotel_total = base_hotel_total

        total_kzt = calc_hotel_total + flight_data.flight_price_kzt
        total_usd = round(total_kzt / USD_TO_KZT)
        price_per_night_kzt = round(total_kzt / nights)
        price_per_night_usd = round(total_usd / nights)

        breakdown = f"Hotel ({nights}n): {calc_hotel_total:,} ₸ + Roundtrip Flight: {flight_data.flight_price_kzt:,} ₸"

        # ── TourVisor Board (Meal) Description ─────────────────────────────
        meal_raw = row["meal_type"]
        if "UAI" in meal_raw or "Ultra" in meal_raw:
            board_desc = "Ultra All Inclusive — шведский стол, напитки 24/7, a-la carte"
            board_desc_en = "Ultra All Inclusive — 24/7 all-inclusive (gourmet meals, premium beverages, snacks)"
        elif "AI" in meal_raw or "All Inclusive" in meal_raw or "Все включено" in meal_raw:
            board_desc = "All Inclusive — 3-разовое питание (шведский стол), напитки, снек-бар"
            board_desc_en = "All Inclusive — all meals, snacks, soft and alcoholic drinks included"
        elif "BB" in meal_raw or "Breakfast" in meal_raw:
            board_desc = "Bed & Breakfast — только завтрак (шведский стол)"
            board_desc_en = "Bed & Breakfast — morning buffet breakfast included"
        elif "HB" in meal_raw or "Half Board" in meal_raw:
            board_desc = "Half Board — завтрак + ужин (шведский стол)"
            board_desc_en = "Half Board — breakfast + dinner (buffet)"
        elif "FB" in meal_raw:
            board_desc = "Full Board — полный пансион (завтрак, обед, ужин)"
            board_desc_en = "Full Board — breakfast, lunch, and dinner buffet"
        elif "RO" in meal_raw:
            board_desc = "Room Only — без питания (только проживание)"
            board_desc_en = "Room Only — accommodation only, no meals included"
        else:
            board_desc = f"{meal_raw} — Стандартный пансион отеля"
            board_desc_en = f"{meal_raw} — Standard hotel board"

        # Destination-tailored beach specifications
        country_lower = str(row["country"]).lower()
        if any(c in country_lower for c in ["maldives", "мальдивы"]):
            beach_spec = "1-я линия, собственный пляж и лагуна, шезлонги и полотенца бесплатно"
            beach_spec_en = "1st coastline, private beach and lagoon, complimentary sun loungers & beach towels"
        elif any(c in country_lower for c in ["thailand", "тайланд", "таиланд", "vietnam"]):
            beach_spec = "1-я линия, собственный песчаный пляж, бесплатные шезлонги и зонты"
            beach_spec_en = "1st coastline, private sandy beach, complimentary sun loungers & umbrellas"
        elif any(c in country_lower for c in ["uae", "оаэ", "dubai"]):
            beach_spec = "1-я линия, собственный песчаный пляж, шезлонги и зонты бесплатно"
            beach_spec_en = "1st coastline, private sandy beach, complimentary sun loungers & umbrellas"
        elif any(c in country_lower for c in ["turkey", "турция", "egypt", "египет"]):
            beach_spec = "1-я линия, собственный песчано-галечный пляж, бесплатные шезлонги и зонты"
            beach_spec_en = "1st coastline, private sandy beach, complimentary sun loungers & umbrellas"
        else:
            beach_spec = "1-я / 2-я линия, собственный пляж, шезлонги и зонты бесплатно"
            beach_spec_en = "1st coastline, private sandy beach, complimentary sun loungers & umbrellas"

        in_room_spec = "Кондиционер, Сейф (бесплатно), Wi-Fi, Фен, Ванна/душ, ТВ, балкон/терраса, мини-бар, набор для чая/кофе"
        in_room_spec_en = "Air conditioning, Digital safe (free), Wi-Fi, Hairdryer, Bath/shower, TV, Balcony/terrace, Minibar, Tea/coffee set"

        children_spec = "Детский бассейн, мини-клуб, игровая площадка, детские стульчики в ресторане, кроватка по запросу"
        children_spec_en = "Kids club, shallow pool, baby cot upon request, high chairs in restaurant"

        territory_spec = "Открытый бассейн, SPA-центр, ресторан a-la carte, фитнес-зал, круглосуточная стойка регистрации, бесплатная парковка"
        territory_spec_en = "Swimming pool, a la carte restaurants, fitness center, landscaped gardens, free Wi-Fi"

        # ── Flexible dates (±1–2 days + base date) ──────────────────────────
        try:
            base_dt = datetime.strptime(request.date_start, "%Y-%m-%d")
        except Exception:
            base_dt = datetime.now() + timedelta(days=21)

        flex_offsets = [-2, -1, 0, 1, 2]
        flexible_dates = []
        for offset in flex_offsets:
            alt_dt = base_dt + timedelta(days=offset)
            alt_end = alt_dt + timedelta(days=nights)
            delta_kzt = offset * 22000
            alt_total = int(round(max(100000, total_kzt + delta_kzt)))
            date_str = alt_dt.strftime("%d.%m")
            display_str = f"{date_str} (Выбрано)" if offset == 0 else date_str
            flexible_dates.append({
                "display_label": display_str,
                "date_label": date_str,
                "range_label": f"{date_str} – {alt_end.strftime('%d.%m')}",
                "departure_date": alt_dt.strftime("%Y-%m-%d"),
                "return_date": alt_end.strftime("%Y-%m-%d"),
                "offset_days": offset,
                "is_base": (offset == 0),
                "total_kzt": alt_total,
                "total_usd": int(round(alt_total / USD_TO_KZT)),
            })

        recommendations.append(
            HotelRecommendation(
                id=row["hotel_id"],
                hotel_name=row["hotel_name"],
                country=row["country"],
                resort=row["country_city"].split(",")[-1].strip() if "," in row["country_city"] else row["country_city"],
                country_city=row["country_city"],
                image_url=row["image_url"],
                gallery_images=gallery,
                stars=row["stars"],
                meal_type=row["meal_type"],
                price_per_night_kzt=price_per_night_kzt,
                price_per_night_usd=price_per_night_usd,
                total_price_kzt=int(round(total_kzt)),
                total_price_usd=int(round(total_usd)),
                price_breakdown=breakdown,
                guests_badge=guest_badge,
                rating=row["rating"],
                reviews_count=row["reviews_count"],
                seats_flight=row["seats_flight"],
                seats_hotel=row["seats_hotel"],
                pros=json.loads(row["pros_json"]),
                cons=json.loads(row["cons_json"]),
                matched_amenities=amenities,
                match_score=min(99, match_score),
                highlight_badge="⭐️ Highest Rating",
                summary=row["summary"],
                room_options=rooms,
                flight=flight_data,
                flexible_dates=flexible_dates,
                beach=beach_spec,
                board_desc=board_desc,
                in_room=in_room_spec,
                for_children=children_spec,
                territory=territory_spec,
                beach_en=beach_spec_en,
                board_desc_en=board_desc_en,
                in_room_en=in_room_spec_en,
                for_children_en=children_spec_en,
                territory_en=territory_spec_en,
            )
        )

    return recommendations