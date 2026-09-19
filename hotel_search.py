"""Модели, моковые данные и локальный поиск отелей для Zari Travel.

Каталог: ровно 50 отелей = 5 направлений (Турция, Египет, ОАЭ, Таиланд,
Вьетнам) x 10 отелей. Каждый отель — отдельная строка с уникальным именем,
ценой и набором номеров. Никаких "вариантов"/копий одного отеля не создаётся:
раньше дубли появлялись из-за цикла `for variant in range(5)`, который на
каждое из 10 названий в направлении штамповал 5 почти одинаковых записей
(итого 500 строк с разницей в 10 000 ₸ и суффиксом "Collection 02").
"""

import json
import os
from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional

try:
    from openai import OpenAI
except ImportError:  # AI-агент (run_tour_agent) не обязателен для работы API
    OpenAI = None  # type: ignore[assignment]

from pydantic import BaseModel, Field, field_validator, model_validator

from hotel_database import initialize_database, reset_database, search_database


class Amenity(str, Enum):
    """Строгий список удобств, поддерживаемых поиском."""

    PRIVATE_BEACH = "свой пляж"
    SANDY_BEACH = "песчаный пляж"
    FIRST_LINE = "первая линия"
    WIFI = "wifi"
    WATERPARK = "аквапарк"
    KIDS_CLUB = "детский клуб"
    ALL_INCLUSIVE = "все включено"


class MealType(str, Enum):
    """Доступные варианты питания."""

    AI = "AI - Все включено"
    UAI = "UAI - Ультра все включено"
    FB = "FB - Полный пансион"
    BB = "BB - Завтраки"


COUNTRIES: List[str] = [
    "Турция", "Египет", "ОАЭ", "Таиланд", "Вьетнам", "Греция", "Испания",
    "Мальдивы", "Индонезия", "Кипр", "Италия", "Тунис", "Марокко", "Мальта",
    "Черногория", "Болгария", "Хорватия", "Сейшелы", "Маврикий", "Бали",
]


class HotelSearchRequest(BaseModel):
    """Параметры, которые приходят от формы поиска или AI-агента."""

    city_from: str = Field(min_length=2, description="Город вылета")
    date_start: str = Field(description="Дата вылета в формате YYYY-MM-DD")
    budget_kzt: int = Field(gt=0, description="Максимальный бюджет всего тура")
    country: Optional[str] = Field(default=None, description="Страна отдыха")
    nights: int = Field(ge=1, le=30, description="Количество ночей")
    adults: int = Field(default=2, ge=1, le=6, description="Количество взрослых")
    children: int = Field(default=0, ge=0, le=4, description="Количество детей")
    children_ages: List[int] = Field(
        default_factory=list,
        description="Возраст каждого ребенка",
    )
    stars: Optional[int] = Field(default=None, description="Минимальная звездность")
    meal_type: Optional[MealType] = Field(default=None, description="Тип питания")
    amenities: List[Amenity] = Field(
        default_factory=list,
        description="Желаемые удобства",
    )

    @field_validator("city_from", mode="before")
    @classmethod
    def normalize_city_from(cls, value: Any) -> Any:
        """Убирает пробелы по краям и приводит город к Title Case."""

        return value.strip().title() if isinstance(value, str) else value

    @field_validator("country", mode="before")
    @classmethod
    def normalize_country(cls, value: Any) -> Any:
        """Нормализует страну по каноническим именам, чтобы ОАЭ и другие страны находились корректно."""

        if not isinstance(value, str):
            return value
        text = value.strip()
        if not text:
            return None

        normalized = text.lower()
        mapping = {
            "турция": "Турция",
            "турции": "Турция",
            "египет": "Египет",
            "египте": "Египет",
            "оаэ": "ОАЭ",
            "эмираты": "ОАЭ",
            "арабские эмираты": "ОАЭ",
            "дубай": "ОАЭ",
            "uae": "ОАЭ",
            "united arab emirates": "ОАЭ",
            "таиланд": "Таиланд",
            "таиланде": "Таиланд",
            "вьетнам": "Вьетнам",
            "вьетнаме": "Вьетнам",
            "греция": "Греция",
            "испания": "Испания",
            "мальдивы": "Мальдивы",
            "индонезия": "Индонезия",
            "кипр": "Кипр",
            "италия": "Италия",
            "тунис": "Тунис",
            "марокко": "Марокко",
            "мальта": "Мальта",
            "черногория": "Черногория",
            "болгария": "Болгария",
            "хорватия": "Хорватия",
            "сейшелы": "Сейшелы",
            "маврикий": "Маврикий",
            "бали": "Бали",
        }
        return mapping.get(normalized, text)

    @field_validator("date_start")
    @classmethod
    def validate_date_start(cls, value: str) -> str:
        """Проверяет, что дата существует и записана как YYYY-MM-DD."""

        try:
            date.fromisoformat(value)
        except ValueError as error:
            raise ValueError("Дата должна быть в формате YYYY-MM-DD") from error
        return value

    @field_validator("stars")
    @classmethod
    def validate_stars(cls, value: Optional[int]) -> Optional[int]:
        """Оставляет только поддерживаемые категории звездности."""

        if value is not None and value not in {3, 4, 5}:
            raise ValueError("Звездность должна быть 3, 4 или 5")
        return value

    @field_validator("children_ages")
    @classmethod
    def validate_children_ages(cls, value: List[int]) -> List[int]:
        """Проверяет реалистичный возраст детей для семейного поиска."""

        if any(age < 0 or age > 17 for age in value):
            raise ValueError("Возраст ребенка должен быть от 0 до 17 лет")
        return value

    @model_validator(mode="after")
    def validate_family(self) -> "HotelSearchRequest":
        """Синхронизирует число детей со списком их возрастов."""

        if len(self.children_ages) != self.children:
            raise ValueError("Укажите возраст каждого ребенка")
        return self


class RoomOption(BaseModel):
    """Номер, который можно выбрать внутри карточки отеля."""

    id: str
    name: str
    images: List[str] = Field(min_length=5, max_length=5)
    description: str
    sqm: int = Field(ge=10, le=500)
    capacity: str
    amenities_included: List[str] = Field(default_factory=list)
    amenities_excluded: List[str] = Field(default_factory=list)
    vip_privileges: List[str] = Field(default_factory=list)
    price_delta_kzt: int = Field(ge=0)
    availability: str


class HotelRecommendation(BaseModel):
    """Расширенная карточка отеля для API и фронтенда."""

    id: str
    hotel_name: str
    country_city: str
    image_url: str
    stars: int = Field(ge=3, le=5)
    meal_type: str
    price_per_night_kzt: int = Field(gt=0)
    total_price_kzt: int = Field(gt=0)
    rating: float = Field(ge=0, le=5)
    reviews_count: int = Field(ge=0)
    seats_flight: str
    seats_hotel: str
    pros: List[str] = Field(min_length=3, max_length=3)
    cons: List[str] = Field(min_length=1, max_length=2)
    matched_amenities: List[Amenity] = Field(default_factory=list)
    match_score: int = Field(default=0, ge=0, le=100)
    highlight_badge: str = Field(default="⭐ Высший рейтинг")
    summary: str
    room_options: List[RoomOption] = Field(min_length=5, max_length=5)


class MockHotel(BaseModel):
    """Внутренняя запись моковой базы с данными для фильтрации."""

    id: str
    hotel_name: str
    country: str
    country_city: str
    image_url: str
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
    room_options: List[RoomOption] = Field(min_length=5, max_length=5)


# Пул фотографий обложек отелей (Unsplash). Индексация по глобальному индексу
# отеля (0..49) гарантирует, что внутри одной страны (блок из 10 отелей)
# фотографии не повторяются, т.к. размер пула больше размера блока.
_HOTEL_IMAGE_POOL = [
    "photo-1564501049412-61c2a3083791", "photo-1540541338287-41700207dee6",
    "photo-1571896349842-33c89424de2d", "photo-1518684079-3c830dcef090",
    "photo-1539367628448-4bc5c9d171c8", "photo-1571003123894-1f0594d2b5d9",
    "photo-1560347876-aeef00ee58a1", "photo-1571902943202-507ec2618e8f",
    "photo-1445019980597-93fa8acb246c", "photo-1602002418082-a4443e081dd1",
    "photo-1602343168117-bb8ffe3e2e9f", "photo-1602343168109-cbc70a2e5c81",
    "photo-1520250497591-112f2f40a3f4", "photo-1610641818989-c2051b5e2cfd",
    "photo-1590073242678-70ee3fc28f8e", "photo-1584132967334-10e028bd69f7",
    "photo-1615880484746-a134be9a6ecf", "photo-1544551763-46a013bb70d5",
    "photo-1611601322175-ddd1343ea788", "photo-1573052905904-34ad8c27f0cc",
    "photo-1559599238-308793637427", "photo-1551882547-ff40c63fe5fa",
    "photo-1602391833977-358a52198938", "photo-1611892440504-42a792e24d32",
    "photo-1582719508461-905c673771fd",
]

# Пул фотографий интерьеров номеров (Unsplash).
_ROOM_IMAGE_POOL = [
    "photo-1611892440504-42a792e24d32", "photo-1590490360182-c33d57733427",
    "photo-1587985064135-0366536eab42", "photo-1566665797739-1674de7a421a",
    "photo-1595576508898-0ad5c879a061", "photo-1582719478250-c89cae4dc85b",
    "photo-1591088398332-8a7791972843", "photo-1566073771259-6a8506099945",
    "photo-1548574505-5e239809ee19", "photo-1601565415267-3feb3b8b9c6e",
    "photo-1600585154340-be6161a56a0c", "photo-1616046229478-9901c5536a45",
    "photo-1618773928121-c32242e63f39", "photo-1631049307264-da0dc9b7fc00",
    "photo-1560185893-a55cbc8c57e8", "photo-1560185127-6ed189bf02f4",
    "photo-1595526114035-0d45ed16cfbf", "photo-1584132967334-10e028bd69f7",
    "photo-1571003123894-1f0594d2b5d9", "photo-1560448204-603b3fc33ddc",
]


def _unsplash(photo_id: str) -> str:
    """Собирает ссылку на HD-версию фото Unsplash с фиксированными размерами."""

    return f"https://images.unsplash.com/{photo_id}?auto=format&fit=crop&w=1200&h=800&q=80"


def _hotel_cover(global_index: int) -> str:
    return _unsplash(_HOTEL_IMAGE_POOL[global_index % len(_HOTEL_IMAGE_POOL)])


def _room_gallery(global_index: int, tier_index: int) -> List[str]:
    """Подбирает 5 разных фото для конкретного номера конкретного отеля."""

    start = (global_index * 3 + tier_index * 2) % len(_ROOM_IMAGE_POOL)
    return [
        _unsplash(_ROOM_IMAGE_POOL[(start + step) % len(_ROOM_IMAGE_POOL)])
        for step in range(5)
    ]


_PROS_POOL = [
    "Отель в шаговой доступности от моря",
    "Собственная охраняемая пляжная линия",
    "Насыщенная анимационная программа для детей",
    "Высокий уровень русскоязычного персонала",
    "Современный SPA и бассейн с подогревом",
    "Стабильно высокие оценки гостей за чистоту номеров",
    "Удобная логистика трансфера от аэропорта",
    "Разнообразное меню и качественная кухня",
    "Развитая инфраструктура для активного отдыха",
    "Тихая приватная территория без лишнего шума",
]

_CONS_POOL = [
    "Доплата за номера с видом на море",
    "В высокий сезон территория может быть многолюдной",
    "Часть ресторанов отеля работает по предварительной записи",
    "Расстояние до центра города увеличивает время трансфера",
    "Ранний выезд из номера в день отлета",
    "Быстрый Wi-Fi доступен только в лобби и у бассейна",
]

# Шаблон линейки номеров: (название, описание, вмещает взрослых, доля от
# базовой цены тура, добавляется ли в описание "+ ребенок"/"+ дети").
_ROOM_TIER_TEMPLATE = [
    ("Standard Garden View", "Уютный номер с видом на сад", 2, 0.0, False),
    ("Superior Sea View", "Светлый номер с видом на море", 3, 0.08, True),
    ("Family Room", "Просторный номер для семейного отдыха", 4, 0.18, True),
    ("Junior Suite", "Отдельная зона отдыха и панорамный вид", 3, 0.32, True),
    ("Presidential Suite", "Премиальный люкс с отдельной гостиной", 4, 0.55, True),
]


def _round_to_thousand(value: float) -> int:
    return int(round(value / 1000.0)) * 1000


def _build_room_options(global_index: int, base_price: int, stars: int) -> List[RoomOption]:
    """Строит линейку из 5 категорий номеров, масштабированную под цену отеля."""

    rooms: List[RoomOption] = []
    for tier_index, (name, description, capacity, price_share, has_kids) in enumerate(_ROOM_TIER_TEMPLATE):
        is_top_tier = tier_index == len(_ROOM_TIER_TEMPLATE) - 1
        sqm = 32 + tier_index * 16 + (8 if stars == 5 else 0)
        capacity_text = f"До {capacity} взрослых" + (
            " + 2 детей" if has_kids and capacity >= 4 else " + 1 ребенок" if has_kids else ""
        )
        included = ["Кондиционер", "Мини-бар", "Сейф", "Wi-Fi"]
        if tier_index >= 1:
            included += ["Балкон или терраса"]
        if tier_index == 1:
            included += ["Вид на море"]
        if tier_index >= 2:
            included += ["Кофемашина Nespresso"]
        if tier_index >= 3:
            included += ["Халаты и тапочки", "Зона отдыха"]
        if tier_index == 4 and stars == 5 and global_index % 4 == 0:
            included += ["Джакузи"]
        excluded = []
        if tier_index == 0:
            excluded = ["Балкон или терраса", "Вид на море"]
        elif tier_index == 3:
            excluded = ["Личный бассейн"]
        vip_privileges = (
            ["Индивидуальный трансфер на автомобиле", "Доступ в VIP-лаундж", "Ранний заезд / поздний выезд", "Личный батлер"]
            if is_top_tier
            else []
        )
        rooms.append(
            RoomOption(
                id=f"{global_index + 1:03d}-room-{tier_index + 1}",
                name=name,
                images=_room_gallery(global_index, tier_index),
                description=description,
                sqm=sqm,
                capacity=capacity_text,
                amenities_included=included,
                amenities_excluded=excluded,
                vip_privileges=vip_privileges,
                price_delta_kzt=_round_to_thousand(base_price * price_share),
                availability=(
                    "Нет мест" if (global_index + tier_index) % 9 == 0 else "Есть места"
                ),
            )
        )
    return rooms


# ---------------------------------------------------------------------------
# Каталог: 5 направлений x 10 именованных отелей = 50 уникальных записей.
# Формат кортежа: (название, звёзды, базовая цена тура за 7 ночей в KZT,
# тип питания, доп. удобства сверх набора по умолчанию для направления).
# ---------------------------------------------------------------------------

_DESTINATIONS: List[Dict[str, Any]] = [
    {
        "country": "Турция",
        "resort": "Белек / Анталия",
        "default_meal": MealType.AI,
        "base_amenities": [Amenity.WIFI, Amenity.SANDY_BEACH, Amenity.FIRST_LINE, Amenity.ALL_INCLUSIVE],
        "hotels": [
            ("Rixos Premium Belek", 5, 950000, None, [Amenity.PRIVATE_BEACH, Amenity.WATERPARK, Amenity.KIDS_CLUB]),
            ("Maxx Royal Belek Golf Resort", 5, 1450000, None, [Amenity.PRIVATE_BEACH]),
            ("Regnum Carya Golf & Spa", 5, 1680000, None, [Amenity.PRIVATE_BEACH]),
            ("Delphin Imperial Lara", 5, 890000, None, [Amenity.WATERPARK, Amenity.KIDS_CLUB]),
            ("Titanic Mardan Palace", 5, 1120000, None, [Amenity.PRIVATE_BEACH, Amenity.KIDS_CLUB]),
            ("Voyage Belek Golf & Spa", 5, 870000, None, [Amenity.WATERPARK]),
            ("Gloria Serenity Resort", 5, 990000, None, [Amenity.KIDS_CLUB]),
            ("Barut Hemera", 4, 720000, MealType.UAI, []),
            ("Ela Excellence Resort", 5, 1240000, None, [Amenity.PRIVATE_BEACH, Amenity.WATERPARK]),
            ("Kaya Palazzo Golf Resort", 5, 1050000, None, [Amenity.KIDS_CLUB]),
        ],
    },
    {
        "country": "Египет",
        "resort": "Шарм-эль-Шейх",
        "default_meal": MealType.AI,
        "base_amenities": [Amenity.WIFI, Amenity.SANDY_BEACH, Amenity.FIRST_LINE, Amenity.ALL_INCLUSIVE],
        "hotels": [
            ("Rixos Premium Seagate", 5, 980000, None, [Amenity.PRIVATE_BEACH, Amenity.WATERPARK]),
            ("Baron Palms Resort", 5, 870000, None, [Amenity.PRIVATE_BEACH]),
            ("Steigenberger Al Dau Beach", 5, 790000, MealType.UAI, [Amenity.KIDS_CLUB]),
            ("Savoy Sharm El Sheikh", 5, 1020000, None, [Amenity.PRIVATE_BEACH, Amenity.KIDS_CLUB]),
            ("Coral Sea Sensatori", 5, 860000, None, [Amenity.WATERPARK, Amenity.KIDS_CLUB]),
            ("Rixos Sharm El Sheikh", 5, 1150000, None, [Amenity.PRIVATE_BEACH, Amenity.WATERPARK]),
            ("Jaz Mirabel Beach", 4, 680000, MealType.FB, [Amenity.KIDS_CLUB]),
            ("Pickalbatros Aqua Blu", 4, 650000, MealType.FB, [Amenity.WATERPARK]),
            ("Sunrise Arabian Beach", 5, 910000, None, [Amenity.PRIVATE_BEACH]),
            ("Cleopatra Luxury Resort", 5, 940000, None, [Amenity.KIDS_CLUB]),
        ],
    },
    {
        "country": "ОАЭ",
        "resort": "Дубай",
        "default_meal": MealType.BB,
        "base_amenities": [Amenity.WIFI, Amenity.SANDY_BEACH],
        "hotels": [
            ("Atlantis The Palm", 5, 1980000, None, [Amenity.FIRST_LINE, Amenity.WATERPARK, Amenity.KIDS_CLUB]),
            ("Jumeirah Beach Hotel", 5, 1620000, None, [Amenity.FIRST_LINE, Amenity.WATERPARK]),
            ("One&Only Royal Mirage", 5, 2150000, None, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE]),
            ("Address Beach Resort", 5, 1780000, None, [Amenity.FIRST_LINE, Amenity.KIDS_CLUB]),
            ("Anantara The Palm Dubai", 5, 1890000, None, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE]),
            ("Five Palm Jumeirah", 5, 1540000, None, [Amenity.FIRST_LINE]),
            ("Rixos Premium Dubai JBR", 5, 1380000, MealType.AI, [Amenity.FIRST_LINE, Amenity.ALL_INCLUSIVE]),
            ("Kempinski Mall of the Emirates", 5, 1290000, None, []),
            ("The Ritz-Carlton Dubai, JBR", 5, 1720000, None, [Amenity.FIRST_LINE, Amenity.KIDS_CLUB]),
            ("Radisson Blu Dubai Deira Creek", 4, 990000, None, []),
        ],
    },
    {
        "country": "Таиланд",
        "resort": "Пхукет",
        "default_meal": MealType.BB,
        "base_amenities": [Amenity.WIFI, Amenity.SANDY_BEACH],
        "hotels": [
            ("Katathani Phuket Beach Resort", 5, 980000, None, [Amenity.FIRST_LINE, Amenity.KIDS_CLUB]),
            ("Centara Grand Beach Resort Phuket", 5, 890000, MealType.AI, [Amenity.FIRST_LINE, Amenity.WATERPARK, Amenity.ALL_INCLUSIVE]),
            ("Angsana Laguna Phuket", 5, 940000, None, [Amenity.WATERPARK, Amenity.KIDS_CLUB]),
            ("The Slate Phuket", 5, 1050000, None, []),
            ("Amari Phuket", 4, 780000, None, [Amenity.KIDS_CLUB]),
            ("Novotel Phuket Vintage Park", 4, 720000, None, []),
            ("Pullman Phuket Arcadia", 5, 860000, MealType.AI, [Amenity.FIRST_LINE, Amenity.ALL_INCLUSIVE]),
            ("Banyan Tree Phuket", 5, 1780000, None, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE]),
            ("Anantara Mai Khao Phuket", 5, 1620000, None, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE]),
            ("Patong Beach Hotel", 4, 690000, None, []),
        ],
    },
    {
        "country": "Вьетнам",
        "resort": "Дананг",
        "default_meal": MealType.BB,
        "base_amenities": [Amenity.WIFI, Amenity.SANDY_BEACH],
        "hotels": [
            ("InterContinental Danang Sun Peninsula", 5, 1950000, None, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE]),
            ("Furama Resort Danang", 5, 890000, None, [Amenity.FIRST_LINE, Amenity.KIDS_CLUB]),
            ("Vinpearl Resort & Spa Danang", 5, 780000, MealType.AI, [Amenity.WATERPARK, Amenity.KIDS_CLUB, Amenity.ALL_INCLUSIVE]),
            ("Premier Village Danang Resort", 5, 1050000, None, [Amenity.FIRST_LINE, Amenity.KIDS_CLUB]),
            ("Naman Retreat Danang", 5, 980000, None, [Amenity.FIRST_LINE]),
            ("Hyatt Regency Danang", 5, 1120000, None, [Amenity.FIRST_LINE, Amenity.WATERPARK]),
            ("TIA Wellness Resort", 5, 1380000, None, [Amenity.PRIVATE_BEACH]),
            ("Fusion Maia Danang", 5, 1240000, None, [Amenity.PRIVATE_BEACH, Amenity.FIRST_LINE]),
            ("Melia Danang Beach Resort", 5, 870000, None, [Amenity.FIRST_LINE, Amenity.KIDS_CLUB]),
            ("Danang Golden Bay", 4, 690000, None, []),
        ],
    },
    {
        "country": "Греция",
        "resort": "Халкидики",
        "default_meal": MealType.BB,
        "base_amenities": [Amenity.WIFI, Amenity.SANDY_BEACH],
        "hotels": [
            ("Asteras Resort", 5, 880000, None, [Amenity.FIRST_LINE, Amenity.KIDS_CLUB]),
            ("Poseidon Blue", 4, 760000, MealType.AI, [Amenity.WATERPARK]),
            ("Coral Bay Villas", 5, 920000, None, [Amenity.PRIVATE_BEACH]),
            ("Porto Carras", 5, 1360000, None, [Amenity.PRIVATE_BEACH]),
            ("Elysian Resort", 5, 1250000, None, [Amenity.KIDS_CLUB]),
            ("Nafplia View", 4, 700000, None, []),
            ("Aegean Sun", 5, 980000, None, [Amenity.WATERPARK]),
            ("Dionysos Bay", 5, 1040000, None, [Amenity.FIRST_LINE]),
            ("Mykonos Coast", 5, 1420000, None, [Amenity.PRIVATE_BEACH]),
            ("Sandy Pearl", 4, 740000, MealType.FB, []),
        ],
    },
    {
        "country": "Испания",
        "resort": "Марбелья",
        "default_meal": MealType.AI,
        "base_amenities": [Amenity.WIFI, Amenity.SANDY_BEACH, Amenity.ALL_INCLUSIVE],
        "hotels": [
            ("Gran Hotel Miramar", 5, 1480000, None, [Amenity.FIRST_LINE]),
            ("Puente Romano", 5, 1920000, None, [Amenity.PRIVATE_BEACH]),
            ("Marbella Club Hotel", 5, 1860000, None, [Amenity.FIRST_LINE]),
            ("Don Carlos", 5, 1690000, None, [Amenity.WATERPARK]),
            ("Nobu Hotel Marbella", 5, 1750000, None, [Amenity.FIRST_LINE]),
            ("Hotel Villa Padierna", 5, 1840000, None, [Amenity.KIDS_CLUB]),
            ("Hotel Villa Padierna", 5, 1640000, None, [Amenity.FIRST_LINE]),
            ("Club Hotel Riu", 4, 980000, None, [Amenity.KIDS_CLUB]),
            ("Mare Azul", 4, 910000, MealType.AI, []),
            ("Costa del Sol Resort", 4, 860000, None, []),
        ],
    },
    {
        "country": "Мальдивы",
        "resort": "Маале",
        "default_meal": MealType.AI,
        "base_amenities": [Amenity.WIFI, Amenity.PRIVATE_BEACH, Amenity.ALL_INCLUSIVE],
        "hotels": [
            ("Soneva Fushi", 5, 2320000, None, [Amenity.PRIVATE_BEACH]),
            ("The Westin Maldives", 5, 2140000, None, [Amenity.PRIVATE_BEACH]),
            ("Barceló Whale", 4, 1680000, None, [Amenity.FIRST_LINE]),
            ("Jumeirah Olhahali", 5, 2230000, None, [Amenity.PRIVATE_BEACH]),
            ("Lily Beach Resort", 5, 1880000, None, [Amenity.WATERPARK]),
            ("Reethi Beach Resort", 4, 1560000, None, [Amenity.KIDS_CLUB]),
            ("Adaaran Club Rannalhi", 4, 1420000, None, [Amenity.PRIVATE_BEACH]),
            ("Kaani Palm Beach", 4, 1320000, None, [Amenity.SANDY_BEACH]),
            ("Lhaviyani Island", 5, 2080000, None, [Amenity.PRIVATE_BEACH]),
            ("Cocoa Island", 5, 1980000, None, [Amenity.PRIVATE_BEACH]),
        ],
    },
    {
        "country": "Индонезия",
        "resort": "Бали",
        "default_meal": MealType.BB,
        "base_amenities": [Amenity.WIFI, Amenity.SANDY_BEACH],
        "hotels": [
            ("The Ungasan Bali", 5, 1540000, None, [Amenity.PRIVATE_BEACH]),
            ("Ritz-Carlton Bali", 5, 1460000, None, [Amenity.FIRST_LINE]),
            ("W Bali Seminyak", 5, 1380000, None, [Amenity.KIDS_CLUB]),
            ("Ayana Resort Bali", 5, 1650000, None, [Amenity.PRIVATE_BEACH]),
            ("Grand Hyatt Bali", 5, 1420000, None, [Amenity.WATERPARK]),
            ("Seminyak Beach Hotel", 4, 875000, None, []),
            ("Bali Mandira Beach Resort", 5, 1120000, None, [Amenity.FIRST_LINE]),
            ("Bali Nusa Dua Hotel", 4, 840000, MealType.AI, [Amenity.WATERPARK]),
            ("Padma Resort Bali", 5, 1200000, None, [Amenity.PRIVATE_BEACH]),
            ("Uluwatu Cliff Resort", 4, 980000, None, []),
        ],
    },
    {
        "country": "Кипр",
        "resort": "Пафос",
        "default_meal": MealType.AI,
        "base_amenities": [Amenity.WIFI, Amenity.SANDY_BEACH, Amenity.ALL_INCLUSIVE],
        "hotels": [
            ("Amathus Beach Hotel", 5, 950000, None, [Amenity.FIRST_LINE]),
            ("Almyra", 5, 1010000, None, [Amenity.PRIVATE_BEACH]),
            ("Elysium", 4, 790000, None, []),
            ("Anassa", 5, 1540000, None, [Amenity.PRIVATE_BEACH]),
            ("Amathus Beach Resort", 5, 1120000, None, [Amenity.KIDS_CLUB]),
            ("The Royal Resort", 5, 1180000, None, [Amenity.WATERPARK]),
            ("Potideon Beach", 4, 780000, None, []),
            ("Amathus Village", 4, 720000, None, []),
            ("Paphos Luna", 4, 760000, None, [Amenity.KIDS_CLUB]),
            ("Elysium Hills", 4, 830000, None, [Amenity.FIRST_LINE]),
        ],
    },
    {
        "country": "Италия",
        "resort": "Сицилия",
        "default_meal": MealType.BB,
        "base_amenities": [Amenity.WIFI, Amenity.SANDY_BEACH],
        "hotels": [
            ("Villa Carlotta", 5, 1720000, None, [Amenity.PRIVATE_BEACH]),
            ("San Domenico Palace", 5, 1880000, None, [Amenity.FIRST_LINE]),
            ("Le Cale di Sicilia", 4, 990000, None, []),
            ("Villa Igiea", 5, 1760000, None, [Amenity.PRIVATE_BEACH]),
            ("Mazzaró Resort", 5, 1540000, None, [Amenity.KIDS_CLUB]),
            ("The Prince Hotel", 4, 860000, None, []),
            ("Sicily Coast Resort", 4, 910000, None, [Amenity.WATERPARK]),
            ("Tindari Beach Villa", 4, 820000, None, []),
            ("Hotel Villa Cerami", 4, 760000, MealType.AI, [Amenity.ALL_INCLUSIVE]),
            ("Lido del Sole", 4, 790000, None, []),
        ],
    },
    {
        "country": "Тунис",
        "resort": "Хаммамет",
        "default_meal": MealType.AI,
        "base_amenities": [Amenity.WIFI, Amenity.SANDY_BEACH, Amenity.ALL_INCLUSIVE],
        "hotels": [
            ("El Mouradi", 4, 680000, None, [Amenity.FIRST_LINE]),
            ("Sousse Resort", 5, 810000, None, [Amenity.WATERPARK]),
            ("Hammamet Palace", 4, 750000, None, [Amenity.KIDS_CLUB]),
            ("Le Royal", 4, 740000, None, [Amenity.PRIVATE_BEACH]),
            ("Palm Beach", 4, 700000, None, []),
            ("Hammamet Bay", 4, 720000, None, [Amenity.FIRST_LINE]),
            ("Yasmine Beach", 4, 690000, None, [Amenity.KIDS_CLUB]),
            ("Seahorse", 4, 660000, None, [Amenity.WATERPARK]),
            ("Majestic", 5, 900000, None, [Amenity.PRIVATE_BEACH]),
            ("Blue Bay", 4, 670000, None, []),
        ],
    },
    {
        "country": "Марокко",
        "resort": "Агадир",
        "default_meal": MealType.BB,
        "base_amenities": [Amenity.WIFI, Amenity.SANDY_BEACH],
        "hotels": [
            ("Club Hotel", 4, 670000, None, [Amenity.FIRST_LINE]),
            ("Aga Palace", 5, 870000, None, [Amenity.PRIVATE_BEACH]),
            ("Marina Beach", 4, 720000, None, [Amenity.KIDS_CLUB]),
            ("Riad Sunset", 4, 640000, None, []),
            ("Atlantic View", 4, 710000, None, [Amenity.FIRST_LINE]),
            ("Marrakech Horizon", 5, 930000, None, [Amenity.WATERPARK]),
            ("Breeze Bay", 4, 700000, None, []),
            ("Afar Hotel", 4, 640000, None, [Amenity.PRIVATE_BEACH]),
            ("Mirage Resort", 5, 790000, None, [Amenity.KIDS_CLUB]),
            ("Medina Coast", 4, 680000, None, []),
        ],
    },
    {
        "country": "Мальта",
        "resort": "Слима",
        "default_meal": MealType.BB,
        "base_amenities": [Amenity.WIFI, Amenity.SANDY_BEACH],
        "hotels": [
            ("The Palace", 5, 1180000, None, [Amenity.FIRST_LINE]),
            ("The Westin Dragonara", 5, 1270000, None, [Amenity.PRIVATE_BEACH]),
            ("The Palace Malta", 4, 980000, None, [Amenity.KIDS_CLUB]),
            ("Xara Palace", 5, 1160000, None, [Amenity.FIRST_LINE]),
            ("Corinthia St. George", 5, 1360000, None, [Amenity.KIDS_CLUB]),
            ("Maltese Bay", 4, 850000, None, []),
            ("The Xara Palace", 5, 1210000, None, [Amenity.PRIVATE_BEACH]),
            ("Seabreeze Hotel", 4, 880000, None, []),
            ("Mazzo Hotel", 4, 820000, None, [Amenity.FIRST_LINE]),
            ("Sliema Horizon", 4, 760000, None, []),
        ],
    },
    {
        "country": "Черногория",
        "resort": "Будва",
        "default_meal": MealType.AI,
        "base_amenities": [Amenity.WIFI, Amenity.SANDY_BEACH, Amenity.ALL_INCLUSIVE],
        "hotels": [
            ("Montenegro Bay", 4, 820000, None, [Amenity.FIRST_LINE]),
            ("Boka Blue", 4, 910000, None, [Amenity.PRIVATE_BEACH]),
            ("Asteras Beach", 4, 790000, None, [Amenity.KIDS_CLUB]),
            ("Petrovac View", 4, 760000, None, []),
            ("Blue Pearl", 4, 770000, None, [Amenity.FIRST_LINE]),
            ("Golden Coast", 4, 800000, None, [Amenity.WATERPARK]),
            ("Adriatic Sun", 4, 760000, None, []),
            ("Velvet Resort", 5, 950000, None, [Amenity.PRIVATE_BEACH]),
            ("Bayview Hotel", 4, 720000, None, []),
            ("Harbor Pearl", 4, 710000, None, [Amenity.KIDS_CLUB]),
        ],
    },
    {
        "country": "Болгария",
        "resort": "Созопол",
        "default_meal": MealType.AI,
        "base_amenities": [Amenity.WIFI, Amenity.SANDY_BEACH, Amenity.ALL_INCLUSIVE],
        "hotels": [
            ("Black Sea Pearl", 4, 680000, None, [Amenity.FIRST_LINE]),
            ("Sunny Coast", 4, 720000, None, [Amenity.WATERPARK]),
            ("Seaside Palace", 5, 910000, None, [Amenity.PRIVATE_BEACH]),
            ("Coastline Hotel", 4, 690000, None, []),
            ("Azure Bay", 4, 700000, None, [Amenity.KIDS_CLUB]),
            ("Golden Shore", 4, 710000, None, [Amenity.FIRST_LINE]),
            ("Sea Vista", 4, 660000, None, []),
            ("Breeze Resort", 4, 680000, None, [Amenity.WATERPARK]),
            ("Crown Beach", 4, 790000, None, [Amenity.PRIVATE_BEACH]),
            ("Balkan Horizon", 5, 880000, None, [Amenity.KIDS_CLUB]),
        ],
    },
    {
        "country": "Хорватия",
        "resort": "Дубровник",
        "default_meal": MealType.BB,
        "base_amenities": [Amenity.WIFI, Amenity.SANDY_BEACH],
        "hotels": [
            ("Adriatic Rise", 5, 1320000, None, [Amenity.PRIVATE_BEACH]),
            ("Blue Horizon", 4, 990000, None, [Amenity.FIRST_LINE]),
            ("Croatia Coast", 4, 910000, None, []),
            ("Coral View", 5, 1200000, None, [Amenity.WATERPARK]),
            ("Luna Bay", 4, 880000, None, [Amenity.KIDS_CLUB]),
            ("Harbor Light", 4, 860000, None, [Amenity.FIRST_LINE]),
            ("Seaside Nova", 4, 850000, None, []),
            ("Island Dream", 5, 1160000, None, [Amenity.PRIVATE_BEACH]),
            ("Bay Palace", 5, 1240000, None, [Amenity.KIDS_CLUB]),
            ("Coastal Pearl", 4, 900000, None, []),
        ],
    },
    {
        "country": "Сейшелы",
        "resort": "Маэ",
        "default_meal": MealType.AI,
        "base_amenities": [Amenity.WIFI, Amenity.PRIVATE_BEACH, Amenity.ALL_INCLUSIVE],
        "hotels": [
            ("Seychelles Coast", 5, 2160000, None, [Amenity.PRIVATE_BEACH]),
            ("Paradise Cove", 5, 2080000, None, [Amenity.KIDS_CLUB]),
            ("Blue Lagoon", 5, 2000000, None, [Amenity.FIRST_LINE]),
            ("Island Escape", 5, 2140000, None, [Amenity.WATERPARK]),
            ("Coral Sky", 5, 2060000, None, [Amenity.PRIVATE_BEACH]),
            ("Ocean Pearl", 4, 1760000, None, [Amenity.KIDS_CLUB]),
            ("Morne Sea", 4, 1660000, None, []),
            ("Seabird Resort", 5, 2180000, None, [Amenity.PRIVATE_BEACH]),
            ("Palm Horizon", 4, 1580000, None, [Amenity.FIRST_LINE]),
            ("Coco Bay", 4, 1520000, None, []),
        ],
    },
    {
        "country": "Маврикий",
        "resort": "Флориско",
        "default_meal": MealType.AI,
        "base_amenities": [Amenity.WIFI, Amenity.PRIVATE_BEACH, Amenity.ALL_INCLUSIVE],
        "hotels": [
            ("Ocean Pearl Mauritius", 5, 2100000, None, [Amenity.PRIVATE_BEACH]),
            ("Le Meridien", 5, 1980000, None, [Amenity.FIRST_LINE]),
            ("Tropical Breeze", 4, 1700000, None, [Amenity.KIDS_CLUB]),
            ("Lagoon Palace", 5, 2140000, None, [Amenity.PRIVATE_BEACH]),
            ("Azure Coast", 4, 1760000, None, [Amenity.WATERPARK]),
            ("Coral Island", 5, 1880000, None, [Amenity.PRIVATE_BEACH]),
            ("Sunset Cove", 4, 1650000, None, [Amenity.KIDS_CLUB]),
            ("Palm Lux", 5, 2020000, None, [Amenity.FIRST_LINE]),
            ("Mauritian Bungalow", 4, 1600000, None, []),
            ("Sea View Resort", 4, 1560000, None, [Amenity.FIRST_LINE]),
        ],
    },
    {
        "country": "Бали",
        "resort": "Нуса Дуа",
        "default_meal": MealType.BB,
        "base_amenities": [Amenity.WIFI, Amenity.SANDY_BEACH],
        "hotels": [
            ("Bali Aura", 5, 1240000, None, [Amenity.PRIVATE_BEACH]),
            ("Nusa Dua Cove", 5, 1180000, None, [Amenity.KIDS_CLUB]),
            ("Ayu Beach", 4, 980000, None, []),
            ("Serenity Bay", 5, 1290000, None, [Amenity.FIRST_LINE]),
            ("Bali Sea View", 5, 1350000, None, [Amenity.PRIVATE_BEACH]),
            ("Sunset Villas", 4, 940000, None, []),
            ("Bali Horizon", 4, 890000, None, [Amenity.WATERPARK]),
            ("Nusa Garden", 4, 860000, None, [Amenity.KIDS_CLUB]),
            ("Tropical Cove", 5, 1260000, None, [Amenity.PRIVATE_BEACH]),
            ("Azure Bali", 4, 910000, None, []),
        ],
    },
]


def _make_hotel_specs() -> List[Dict[str, Any]]:
    """Строит ровно 50 уникальных отелей (без дублей-"вариантов")."""

    specs: List[Dict[str, Any]] = []
    global_index = 0
    for destination in _DESTINATIONS:
        country = destination["country"]
        resort = destination["resort"]
        default_meal: MealType = destination["default_meal"]
        base_amenities: List[Amenity] = destination["base_amenities"]

        for hotel_index, (name, stars, base_price, meal_override, extra_amenities) in enumerate(destination["hotels"]):
            meal_type = meal_override or default_meal
            amenities = list(dict.fromkeys(base_amenities + extra_amenities))
            if meal_type in {MealType.AI, MealType.UAI} and Amenity.ALL_INCLUSIVE not in amenities:
                amenities.append(Amenity.ALL_INCLUSIVE)

            pros = [
                _PROS_POOL[global_index % len(_PROS_POOL)],
                _PROS_POOL[(global_index + 3) % len(_PROS_POOL)],
                _PROS_POOL[(global_index + 6) % len(_PROS_POOL)],
            ]
            cons = [_CONS_POOL[global_index % len(_CONS_POOL)]]
            if hotel_index % 2 == 0:
                cons.append(_CONS_POOL[(global_index + 2) % len(_CONS_POOL)])

            specs.append({
                "id": f"htl-{global_index + 1:03d}",
                "hotel_name": name,
                "country": country,
                "country_city": f"{country}, {resort}",
                "image_url": _hotel_cover(global_index),
                "stars": stars,
                "meal_type": meal_type,
                "package_price_kzt": base_price,
                "rating": round(4.4 + (global_index % 6) / 10, 1),
                "reviews_count": 540 + global_index * 27 + (hotel_index * 11),
                "seats_flight": (
                    "Мало мест" if global_index % 11 == 0
                    else "Под запрос" if global_index % 13 == 0
                    else "Есть места"
                ),
                "seats_hotel": "Под запрос" if global_index % 7 == 0 else "Мгновенное подтверждение",
                "amenities": amenities,
                "pros": pros,
                "cons": cons,
                "departure_cities": ["Астана", "Алматы", "Шымкент"],
                "max_guests": 8 if stars == 5 and hotel_index % 3 == 0 else 6,
                "summary": (
                    f"{name} — экспертная подборка Zari Travel для отдыха в регионе {resort}: "
                    f"{stars}★, {meal_type.value.split(' - ')[-1].lower()}, надёжный туроператор."
                ),
                "room_options": _build_room_options(global_index, base_price, stars),
            })
            global_index += 1
    return specs


MOCK_HOTELS: List[MockHotel] = [MockHotel(**spec) for spec in _make_hotel_specs()]

# База пересобирается на каждом старте приложения из актуальных Python-данных
# выше. Раньше initialize_database() при непустой таблице только обновляла
# room_options_json у совпавших по имени строк, поэтому старые 500 записей
# (включая дубли-"варианты") оставались в zari_travel.db навсегда, даже
# после того как код поправили на 50 отелей. Явный reset перед вставкой
# устраняет расхождение между кодом и БД.
reset_database()
initialize_database(MOCK_HOTELS)


def mock_search_tourvisor_api(request: HotelSearchRequest) -> List[HotelRecommendation]:
    """Ищет отели через SQLite и возвращает типизированные рекомендации."""

    recommendations: List[HotelRecommendation] = []
    requested_amenities = set(request.amenities)

    for row in search_database(request):
        amenities = [Amenity(value) for value in json.loads(row["amenities_json"])]
        match_score = 82
        if request.country and row["country"] == request.country:
            match_score += 8
        if request.stars and row["stars"] >= request.stars:
            match_score += 6
        if request.meal_type and row["meal_type"] == request.meal_type.value:
            match_score += 5
        if requested_amenities:
            overlap = len(requested_amenities & set(amenities))
            match_score += min(overlap * 6, 18)
        if row["total_price_kzt"] <= request.budget_kzt:
            match_score += 8
        else:
            match_score -= min(int((row["total_price_kzt"] - request.budget_kzt) / 50000), 18)
        match_score = max(60, min(99, match_score))

        recommendations.append(
            HotelRecommendation(
                id=row["hotel_id"],
                hotel_name=row["hotel_name"],
                country_city=row["country_city"],
                image_url=row["image_url"],
                stars=row["stars"],
                meal_type=row["meal_type"],
                price_per_night_kzt=round(row["total_price_kzt"] / request.nights),
                total_price_kzt=row["total_price_kzt"],
                rating=row["rating"],
                reviews_count=row["reviews_count"],
                seats_flight=row["seats_flight"],
                seats_hotel=row["seats_hotel"],
                pros=json.loads(row["pros_json"]),
                cons=json.loads(row["cons_json"]),
                matched_amenities=[
                    amenity for amenity in amenities
                    if not requested_amenities or amenity in requested_amenities
                ],
                match_score=match_score,
                summary=row["summary"],
                room_options=[
                    RoomOption.model_validate(room)
                    for room in json.loads(row["room_options_json"])
                ],
            )
        )

    return recommendations


def _model_json_schema(model: type[BaseModel]) -> Dict[str, Any]:
    """Возвращает JSON Schema для Pydantic 2 или Pydantic 1."""

    return model.model_json_schema() if hasattr(model, "model_json_schema") else model.schema()


def _model_validate(model: type[BaseModel], value: Any) -> BaseModel:
    """Создает модель через API текущей версии Pydantic."""

    return model.model_validate(value) if hasattr(model, "model_validate") else model.parse_obj(value)


def _model_dump(model: BaseModel) -> Dict[str, Any]:
    """Сериализует Pydantic-модель в JSON-совместимый словарь."""

    return model.model_dump(mode="json") if hasattr(model, "model_dump") else json.loads(model.json())


def _build_search_tool() -> Dict[str, Any]:
    """Описывает search_hotels для OpenAI Function Calling."""

    return {
        "type": "function",
        "function": {
            "name": "search_hotels",
            "description": "Найти отель по параметрам семейного тура.",
            "parameters": _model_json_schema(HotelSearchRequest),
        },
    }


def run_tour_agent(user_prompt: str) -> str:
    """Извлекает параметры из текста пользователя и запускает локальный поиск.

    Это дополнительная (не обязательная для основного API) возможность:
    текстовый AI-агент поверх того же mock_search_tourvisor_api. Требует
    установленный пакет `openai` и переменную окружения OPENAI_API_KEY.
    """

    if OpenAI is None:
        raise RuntimeError("Пакет 'openai' не установлен: pip install openai")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Не задан OPENAI_API_KEY.")

    client = OpenAI(api_key=api_key)
    messages: List[Dict[str, Any]] = [
        {
            "role": "system",
            "content": "Извлеки параметры семейного тура и вызови search_hotels. Если данных не хватает, задай вопрос.",
        },
        {"role": "user", "content": user_prompt},
    ]
    first_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=[_build_search_tool()],
        tool_choice="auto",
    )
    assistant_message = first_response.choices[0].message
    if not assistant_message.tool_calls:
        return assistant_message.content or "Не удалось получить ответ турагента."

    messages.append(assistant_message.model_dump(exclude_none=True))
    for tool_call in assistant_message.tool_calls:
        if tool_call.function.name != "search_hotels":
            continue
        request = _model_validate(HotelSearchRequest, json.loads(tool_call.function.arguments))
        recommendations = mock_search_tourvisor_api(request)
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps([_model_dump(item) for item in recommendations], ensure_ascii=False),
            }
        )

    final_response = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
    return final_response.choices[0].message.content or "Подходящих отелей не найдено."
