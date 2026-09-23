"""Conversational luxury travel concierge backed by Google Gemini API / OpenRouter."""

from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from typing import Any

try:
    from openai import AsyncOpenAI
except ImportError:  # pragma: no cover
    AsyncOpenAI = None  # type: ignore[assignment]

from hotel_search import (
    Amenity,
    HotelRecommendation,
    HotelSearchRequest,
    MealType,
    USD_TO_KZT,
    mock_search_tourvisor_api,
)

GREETING_MESSAGE = (
    "Welcome to VoyageAI! I am your autonomous travel concierge. "
    "Where would you like to travel, for how many nights, and what is your target budget and party size?"
)

SYSTEM_PROMPT = """
You are VoyageAI, an elite multilingual autonomous AI travel concierge for international travelers.
LANGUAGE RULE: Detect the language of the user's message. If the user writes in Russian, reply in Russian. If in English, reply in English. Always keep JSON keys and slot values in English/canonical format regardless of reply language.

Your objective is to extract vacation parameters and converse in a refined, hospitable tone.
Respond STRICTLY in valid JSON without markdown code fences or backticks:
{
    "slots": {
        "destination": "Country or resort name or null",
        "nights": integer or null,
        "adults": integer or null,
        "budget_kzt": integer or null,
        "city_from": "Departure city or null",
        "date_start": "YYYY-MM-DD or null"
    },
    "status": "INCOMPLETE" or "COMPLETE",
    "reply": "Polite response in the SAME language as the user's message (EN or RU)"
}
If destination, departure date (date_start), nights, adults count, and budget are identified, set status to "COMPLETE".
If the user mentions travelling alone / solo / ya odin / я один, set adults to 1.
If budget is in USD, multiply by 500 to store budget_kzt (e.g., $2000 = 1000000).
"""

# Supported destination guardrail
VALID_DESTINATIONS = {
    "Turkey", "UAE", "Thailand", "Egypt", "Vietnam", "Maldives", "Indonesia", "Georgia", "Sri Lanka", "Spain"
}

# Configure API Client: prioritize Google Gemini API, fallback to OpenRouter
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")

if GEMINI_API_KEY and AsyncOpenAI:
    client = AsyncOpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=GEMINI_API_KEY,
    )
    ACTIVE_MODELS = [
        os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        "gemini-1.5-flash",
    ]
elif OPENROUTER_API_KEY and AsyncOpenAI:
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
    ACTIVE_MODELS = [
        "meta-llama/llama-3.1-8b-instruct:free",
        "google/gemini-2.0-flash-lite-001",
        "mistralai/mistral-7b-instruct:free",
    ]
else:
    client = None
    ACTIVE_MODELS = []


class OpenRouterAPIError(RuntimeError):
    """External LLM provider exception wrapper."""


SEASONAL_PROMPTS_EN = [
    "Solo luxury trip to Dubai from Astana departing Oct 20 for 5 nights: 1 adult, $2,500 budget",
    "Family holiday in Antalya from Astana departing Oct 14 for 7 nights: 2 adults, 1 child (age 6), $2,800 budget",
    "Phuket vacation from Almaty departing Nov 10 for 8 nights: 2 adults, $2,200 budget",
    "Romantic Maldives overwater villa from Almaty departing Nov 5 for 7 nights, all-inclusive, $5,500 budget",
]

SEASONAL_PROMPTS_RU = [
    "Соло-поездка в Дубай из Астаны с 20 октября на 5 ночей, 1 взрослый, бюджет $2 500",
    "Семейный отдых в Анталье из Астаны с 14 октября на 7 ночей: 2 взрослых, 1 ребёнок (6 лет), бюджет $2 800",
    "Отдых на Пхукете из Алматы с 10 ноября на 8 ночей: 2 взрослых, бюджет 1 800 000 ₸",
    "Отдых на Мальдивах из Алматы с 5 ноября на 7 ночей: вилла на воде, всё включено, бюджет $5 500",
]


def build_seasonal_prompts(is_russian: bool = False) -> list[str]:
    return SEASONAL_PROMPTS_RU if is_russian else SEASONAL_PROMPTS_EN


CITY_FORMS: dict[str, list[str]] = {
    "Astana": [
        "astana", "астана", "астаны", "астане", "астану", "астаной", "nqz",
        "нур-султан", "нурсултан", "нур султан", "nur-sultan",
    ],
    "Almaty": [
        "almaty", "алматы", "алмате", "алмату", "алма-ата", "алмаата", "алмааты", "ala",
    ],
    "Shymkent": [
        "shymkent", "шымкент", "шымкента", "шымкенте", "шымкенту", "cit",
    ],
}

CITY_ALIASES: dict[str, str] = {}
for _canonical, _forms in CITY_FORMS.items():
    for _form in _forms:
        CITY_ALIASES[_form.lower()] = _canonical


COUNTRY_FORMS: dict[str, list[str]] = {
    "Turkey": [
        "turkey", "turkiye", "турция", "турции", "турцию", "турцией", "турецкий", "турецкие",
        "antalya", "анталья", "анталье", "анталью", "анталии", "анталию", "антальи", "антальей", "анталийский",
        "belek", "белек", "белеке", "белека", "белеком",
        "kemer", "кемер", "кемере", "кемера", "кемером",
        "side", "сиде",
        "bodrum", "бодрум", "бодруме", "бодрума", "бодрумом",
        "marmaris", "мармарис", "мармарисе", "мармариса",
        "alanya", "аланья", "аланье", "аланью", "алании", "аланию",
        "istanbul", "стамбул", "стамбуле", "стамбула", "стамбулом",
    ],
    "UAE": [
        "uae", "emirates", "united arab emirates",
        "оаэ", "эмираты", "эмиратах", "эмиратов", "эмиратам", "эмиратами",
        "dubai", "дубай", "дубае", "дубая", "дубаи", "дубаем", "дубаях", "дубайский",
        "abu dhabi", "абу-даби", "абу даби",
        "sharjah", "шарджа", "шардже", "шарджи", "шарджу",
        "ras al khaimah", "рас-эль-хайм", "рас аль хайм",
    ],
    "Thailand": [
        "thailand", "thai", "таиланд", "таиланде", "таиланда", "таиланду", "таиландом", "тайский",
        "тайланд", "тайланде", "тайланда", "тайланду", "тайландом", "тай",
        "phuket", "пхукет", "пхукете", "пхукета", "пхукетом", "пхукетский",
        "pattaya", "паттайя", "паттайе", "паттайю", "паттайи",
        "samui", "самуи", "самуй",
        "bangkok", "бангкок", "бангкоке", "бангкока",
        "krabi", "краби",
    ],
    "Maldives": [
        "maldives", "maldive", "male",
        "мальдивы", "мальдивах", "мальдивам", "мальдив", "мальдивами", "мале", "мальдивский", "мальдивские",
    ],
    "Egypt": [
        "egypt", "египет", "египте", "египта", "египтом", "египетский", "египетские",
        "sharm", "sharm el sheikh", "шарм", "шарм-эль-шейх", "шарм эль шейх", "шарме", "шарма",
        "hurghada", "хургада", "хургаде", "хургаду", "хургады", "хургадой",
    ],
    "Vietnam": [
        "vietnam", "вьетнам", "вьетнаме", "вьетнама", "вьетнамом", "вьетнамский",
        "da nang", "danang", "дананг", "дананге", "дананга",
        "phu quoc", "фукуок", "фукуоке", "фукуока",
        "nha trang", "нячанг", "нячанге", "нячанга",
    ],
    "Georgia": [
        "georgia", "грузия", "грузии", "грузию", "грузией", "грузинский",
        "batumi", "батуми",
        "tbilisi", "тбилиси",
        "kobuleti", "кобулети",
    ],
    "Sri Lanka": [
        "sri lanka", "шри-ланка", "шри ланка", "шри-ланке", "шри ланке", "шри-ланку", "шри ланку",
        "шриланка", "шриланке", "шри-ланки", "шри ланки", "шри-ланкой",
        "colombo", "коломбо",
        "bentota", "бентота", "бентоте",
        "galle", "галле",
    ],
    "Indonesia": [
        "indonesia", "индонезия", "индонезии", "индонезию", "индонезией", "индонезийский",
        "bali", "бали", "балийский",
        "denpasar", "денпасар",
        "ubud", "убуд", "убуде",
    ],
    "Spain": [
        "spain", "испания", "испании", "испанию", "испанией", "испанский",
        "barcelona", "барселона", "барселоне", "барселону", "барселоны",
        "mallorca", "majorca", "майорка", "майорке", "мальорка", "мальорке",
        "madrid", "мадрид", "мадриде", "мадрида",
    ],
}

COUNTRY_ALIASES: dict[str, str] = {}
for _canonical, _forms in COUNTRY_FORMS.items():
    for _form in _forms:
        COUNTRY_ALIASES[_form.lower()] = _canonical

MEAL_ALIASES = {
    "all inclusive": "AI - All Inclusive", "все включено": "AI - All Inclusive", "ai": "AI - All Inclusive",
    "ultra all inclusive": "UAI - Ultra All Inclusive", "ультра все включено": "UAI - Ultra All Inclusive", "uai": "UAI - Ultra All Inclusive",
    "full board": "FB - Full Board", "полный пансион": "FB - Full Board", "fb": "FB - Full Board",
    "breakfast": "BB - Bed & Breakfast", "bed and breakfast": "BB - Bed & Breakfast", "завтраки": "BB - Bed & Breakfast", "bb": "BB - Bed & Breakfast",
}


def _normalize_text(value: Any) -> str:
    return str(value).strip().lower() if value is not None else ""


def _normalize_country(value: Any) -> str | None:
    text = _normalize_text(value)
    if not text:
        return None
    for k in sorted(COUNTRY_ALIASES.keys(), key=len, reverse=True):
        if k in text:
            return COUNTRY_ALIASES[k]
    return text.title()


RU_MONTH_MAP = {
    "январ": 1, "янв": 1,
    "феврал": 2, "фев": 2,
    "март": 3, "мар": 3,
    "апрел": 4, "апр": 4,
    "май": 5, "мая": 5, "мае": 5,
    "июн": 6,
    "июл": 7,
    "август": 8, "авг": 8,
    "сентябр": 9, "сент": 9, "сен": 9,
    "октябр": 10, "окт": 10,
    "ноябр": 11, "нояб": 11, "ноя": 11,
    "декабр": 12, "дек": 12,
}

EN_MONTH_MAP = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sept": 9, "sep": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}


def _parse_month_str(m_str: str) -> int | None:
    low = m_str.lower().strip()
    for prefix, m_num in sorted(RU_MONTH_MAP.items(), key=lambda x: len(x[0]), reverse=True):
        if low.startswith(prefix):
            return m_num
    for prefix, m_num in sorted(EN_MONTH_MAP.items(), key=lambda x: len(x[0]), reverse=True):
        if low.startswith(prefix):
            return m_num
    return None


def _extract_date(text: str) -> str | None:
    low = text.lower()
    now = datetime.now()
    default_year = max(now.year, 2026)

    # 1. ISO format: 2026-10-14
    iso_m = re.search(r"\b(20\d\d)-(0[1-9]|1[0-2])-([0-3]\d)\b", low)
    if iso_m:
        return f"{iso_m.group(1)}-{iso_m.group(2)}-{iso_m.group(3)}"

    # 2. DD.MM or DD.MM.YYYY
    dot_m = re.search(r"(?:^|[^\d])(\d{1,2})[./](\d{1,2})(?:[./](\d{2,4}))?(?:[^\d]|$)", low)
    if dot_m:
        day = int(dot_m.group(1))
        month = int(dot_m.group(2))
        yr_raw = dot_m.group(3)
        if 1 <= day <= 31 and 1 <= month <= 12:
            if yr_raw:
                year = int(yr_raw) if len(yr_raw) == 4 else 2000 + int(yr_raw)
            else:
                year = default_year
            return f"{year:04d}-{month:02d}-{day:02d}"

    # 3. RU/EN: day + month name, e.g. '14 октября', '14 окт', '14th October'
    dm_m = re.search(r"(?:^|[^\wа-яёА-ЯЁ])(\d{1,2})\s*(?:-?го|-?ое|st|nd|rd|th)?\s+(?:of\s+)?([а-яёa-z]+)(?:\s+(\d{4}))?", low)
    if dm_m:
        day = int(dm_m.group(1))
        m_num = _parse_month_str(dm_m.group(2))
        if m_num and 1 <= day <= 31:
            year = int(dm_m.group(3)) if dm_m.group(3) else default_year
            return f"{year:04d}-{m_num:02d}-{day:02d}"

    # 4. EN: month name + day, e.g. 'Oct 14', 'October 14th', 'departing Oct 14'
    md_m = re.search(r"\b([a-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?(?:\s+(\d{4}))?", low)
    if md_m:
        m_num = _parse_month_str(md_m.group(1))
        day = int(md_m.group(2))
        if m_num and 1 <= day <= 31:
            year = int(md_m.group(3)) if md_m.group(3) else default_year
            return f"{year:04d}-{m_num:02d}-{day:02d}"

    # 5. Month only: 'в октябре', 'на ноябрь', 'in October'
    mon_only_m = re.search(r"(?:в|во|на|in)\s+([а-яёa-z]+)\b", low)
    if mon_only_m:
        m_num = _parse_month_str(mon_only_m.group(1))
        if m_num:
            return f"{default_year:04d}-{m_num:02d}-15"

    # 6. Relative / flexible keywords
    if re.search(r"\b(завтра|tomorrow)\b", low):
        return (now + timedelta(days=1)).strftime("%Y-%m-%d")
    if re.search(r"\b(послезавтра)\b", low):
        return (now + timedelta(days=2)).strftime("%Y-%m-%d")
    if re.search(r"\b(через\s+неделю|на\s+следующей\s+неделе|next\s+week)\b", low):
        return (now + timedelta(days=7)).strftime("%Y-%m-%d")
    if re.search(r"\b(ближайш\w*|любы\w*\s+дат\w*|гибк\w*\s+дат\w*|без\s+разниц\w*|не\s+важно|как\s+можно\s+скорее|любая\s+дата|flexible\s+dates?|flexible|any\s+dates?|asap|upcoming)\b", low):
        return (now + timedelta(days=21)).strftime("%Y-%m-%d")

    return None


def _normalize_date(raw: str | None) -> str | None:
    if not raw:
        return None
    text = str(raw).strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return text
    if re.fullmatch(r"\d{2}\.\d{2}\.\d{4}", text):
        day, month, year = text.split(".")
        return f"{year}-{month}-{day}"
    return _extract_date(text)


def _extract_city(text: str) -> str | None:
    low = text.lower()
    # Check "из <города>" / "from <city>" first
    m = re.search(r"(?:из|from|вылет\s+из|вылетом\s+из)\s+([а-яa-z\-]+)", low)
    if m:
        target = m.group(1).strip()
        for alias in sorted(CITY_ALIASES.keys(), key=len, reverse=True):
            if alias == target or alias in target:
                return CITY_ALIASES[alias]
    for alias in sorted(CITY_ALIASES.keys(), key=len, reverse=True):
        if re.search(rf"(?:^|[^\wа-яёА-ЯЁ]){re.escape(alias)}(?:[^\wа-яёА-ЯЁ]|$)", low):
            return CITY_ALIASES[alias]
    return None


def _extract_country(text: str) -> str | None:
    low = text.lower()
    for alias in sorted(COUNTRY_ALIASES.keys(), key=len, reverse=True):
        if re.search(rf"(?:^|[^\wа-яёА-ЯЁ]){re.escape(alias)}(?:[^\wа-яёА-ЯЁ]|$)", low):
            return COUNTRY_ALIASES[alias]
    return None


def _extract_budget(text: str) -> int | None:
    # 1. USD: $2 800, $2800, 2800$, 2800 usd, 2800 долларов, 2.8k $
    usd_m = re.search(r"\$\s*(\d[\d\s,]*\.?\d*)|(\d[\d\s,]*\.?\d*)\s*(?:\$|usd|dollars?|долларов?|долл?|bucks?)", text, flags=re.IGNORECASE)
    if usd_m:
        raw = usd_m.group(1) or usd_m.group(2)
        if raw:
            clean = raw.replace(" ", "").replace(",", "")
            try:
                val = float(clean)
                if val > 0:
                    return int(val * USD_TO_KZT)
            except ValueError:
                pass

    # 2. Millions: 2 млн, 2.5 млн тенге, 2 000 000 тенге
    mln_m = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:млн|миллион(?:а|ов)?)\s*(?:тенге|т|₸|kzt)?", text, flags=re.IGNORECASE)
    if mln_m:
        clean = mln_m.group(1).replace(",", ".")
        try:
            return int(float(clean) * 1_000_000)
        except ValueError:
            pass

    # 3. KZT: 2 000 000 ₸, 1500000 тенге
    kzt_m = re.search(r"(\d[\d\s,]{4,})\s*(?:₸|kzt|т|тенге)", text, flags=re.IGNORECASE)
    if kzt_m:
        clean = kzt_m.group(1).replace(" ", "").replace(",", "")
        try:
            return int(clean)
        except ValueError:
            pass

    # 4. "бюджет 2 000 000" / "до 1 500 000"
    pre_m = re.search(r"(?:до|бюджет|под\s+ключ)[^\d]*(\d[\d\s,]{4,})", text, flags=re.IGNORECASE)
    if pre_m:
        clean = pre_m.group(1).replace(" ", "").replace(",", "")
        try:
            val = int(clean)
            if val >= 50000:
                return val
        except ValueError:
            pass

    # 5. Plain large number >= 100_000
    for cand in re.findall(r"\b\d[\d\s]{5,}\b", text):
        clean = cand.replace(" ", "")
        if clean.isdigit() and int(clean) >= 100000:
            return int(clean)

    return None


def _extract_nights(text: str) -> int | None:
    match = re.search(r"(\d+)\s*(?:nights?|days?|ноч(?:ей|ь|и|а)?|дней|дня)", text, flags=re.IGNORECASE)
    if match:
        return int(match.group(1))
    word_map = {"one": 1, "two": 2, "three": 3, "seven": 7, "eight": 8, "ten": 10, "семь": 7, "восемь": 8, "десять": 10}
    for w, n in word_map.items():
        if re.search(rf"\b{w}\s+(?:nights?|ноч)", text, flags=re.IGNORECASE):
            return n
    return None


def _is_solo(text: str) -> bool:
    """Detect solo traveler intent in both EN and RU."""
    low = text.lower()
    # Russian solo indicators
    if re.search(
        r"(\bсоло\b|соло[\s\-]поездк"
        r"|\bодин\b(?!\s*(?:отел|ноч|день|раз|звезд|рейс))"
        r"|\bодна\b(?!\s*(?:звезд|ноч|кроват))"
        r"|\bя\s+один\b|\bя\s+одна\b"
        r"|\bеду\s+один|\bлечу\s+один|\bпоеду\s+один"
        r"|\bодин\s+взросл|\bодного\s+взросл"
        r"|\bдля\s+одного|\bна\s+одного"
        r"|\b1\s*взросл)",
        low,
    ):
        return True
    # English solo indicators
    if re.search(
        r"\b(solo[\s\-]?trip|solo[\s\-]?travel|traveling\s+alone|travelling\s+alone"
        r"|i\s+am\s+alone|just\s+me|for\s+1\s+person|for\s+one\s+person"
        r"|single\s+traveler|solo)\b",
        low,
    ):
        return True
    return False


def _extract_adults(text: str) -> int | None:
    if _is_solo(text):
        return 1
    low = text.lower()
    # Couple / Two adults
    if re.search(r"\b(couple|for\s+two|two\s+adults|2\s+adults|двоих|мы\s+вдвоем|для\s+двоих|вдвоем|вдвоём|пара|паре)\b", low):
        return 2
    match = re.search(r"(\d+)\s*(?:adults?|guests?|persons?|people|взросл(?:ых|ый|ая|ого)?)", low)
    if match:
        return int(match.group(1))
    if re.search(r"\b(семь[яеейю]|family)\b", low):
        return 2
    return None


def _extract_children(text: str) -> int | None:
    low = text.lower()
    match = re.search(r"(\d+)\s*(?:children|kids?|child|дет(?:ей|и|ям)|реб[её]н(?:ок|ка|ком))", low)
    if match:
        return int(match.group(1))
    if re.search(r"\b(?:с|1)\s+реб[её]нком\b", low):
        return 1
    if re.search(r"\b(?:с|2)\s+детьми\b", low):
        return 2
    return None


def _extract_children_ages(text: str) -> list[int] | None:
    # Parenthesized age e.g. "(6 лет)", "(возраст 6)", "(6)"
    par_matches = re.findall(r"\(\s*(?:возраст\s*)?(\d{1,2})\s*(?:лет|года|год)?\s*\)", text, flags=re.IGNORECASE)
    if par_matches:
        return [int(m) for m in par_matches]
    matches = re.findall(r"\b(\d{1,2})\s*(?:years?\s+old|yrs?|лет|года|год)\b", text, flags=re.IGNORECASE)
    if matches:
        return [int(m) for m in matches]
    return None


def _fallback_extract(text: str) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    city = _extract_city(text)
    if city:
        parsed["city_from"] = city
    date_start = _extract_date(text)
    if date_start:
        parsed["date_start"] = date_start
    country = _extract_country(text)
    if country:
        parsed["country"] = country
    budget = _extract_budget(text)
    if budget:
        parsed["budget_kzt"] = budget
    nights = _extract_nights(text)
    if nights:
        parsed["nights"] = nights
    adults = _extract_adults(text)
    if adults:
        parsed["adults"] = adults
    children = _extract_children(text)
    if children is not None:
        parsed["children"] = children
    ages = _extract_children_ages(text)
    if ages:
        parsed["children_ages"] = ages
        if "children" not in parsed or parsed["children"] == 0:
            parsed["children"] = len(ages)
    return parsed



def clean_json_response(raw_text: str) -> dict[str, Any]:
    text = (raw_text or "").strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE | re.DOTALL).strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    return json.loads(text)


def _coerce_llm_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    slots = payload.get("slots")
    if isinstance(slots, dict):
        payload = {**payload, **slots}
        if payload.get("destination") and not payload.get("country"):
            payload["country"] = payload["destination"]
    compiled: dict[str, Any] = {}
    for key, value in payload.items():
        if key == "children_ages" and isinstance(value, list):
            compiled[key] = value
        elif key in {"budget_kzt", "nights", "adults", "children", "stars"}:
            try:
                compiled[key] = int(value)
            except (TypeError, ValueError):
                continue
        elif key in {"city_from", "country", "date_start", "meal_type"} and value not in (None, ""):
            compiled[key] = str(value)
        elif key == "status":
            compiled[key] = str(value)
    return compiled


async def _llm_extract(message: str, history: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    conversation: list[dict[str, str]] = []
    if history:
        for item in history:
            if isinstance(item, dict):
                role = str(item.get("role") or "user")
                content = str(item.get("content") or "")
                if content:
                    conversation.append({"role": role, "content": content})
    conversation.append({"role": "user", "content": message})

    if client is not None:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, *conversation]
        for model_name in ACTIVE_MODELS:
            try:
                response = await client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=0.1,
                    timeout=10,
                )
                raw_text = response.choices[0].message.content or ""
                parsed = clean_json_response(raw_text)
                return _coerce_llm_payload(parsed)
            except Exception:
                continue

    # Local deterministic fallback parser
    fallback = _fallback_extract(message)
    slots = {
        "destination": fallback.get("country"),
        "date_start": fallback.get("date_start"),
        "nights": fallback.get("nights"),
        "adults": fallback.get("adults"),
        "budget_kzt": fallback.get("budget_kzt"),
    }
    complete = all(slots.values())
    return {
        "slots": slots,
        "status": "COMPLETE" if complete else "INCOMPLETE",
        "reply": "Analyzing travel criteria and searching bespoke packages..." if complete else "Understood. Please clarify your destination, dates or budget.",
        "country": slots["destination"],
        "date_start": slots["date_start"],
        "nights": slots["nights"],
        "adults": slots["adults"],
        "budget_kzt": slots["budget_kzt"],
        **fallback,
    }


@dataclass
class TravelAgentContext:
    city_from: str = "Astana"
    date_start: str | None = None
    nights: int | None = None
    budget_kzt: int | None = None
    country: str | None = None
    adults: int | None = None
    children: int = 0
    children_ages: list[int] = field(default_factory=list)
    stars: int | None = None
    meal_type: str | None = None
    amenities: list[str] = field(default_factory=list)

    @property
    def dict(self) -> dict[str, Any]:
        return asdict(self)

    def missing_fields(self) -> list[str]:
        # Required parameters before curating top recommendations
        required = ["country", "date_start", "nights", "adults", "budget_kzt"]
        missing: list[str] = []
        for name in required:
            if getattr(self, name) is None:
                missing.append(name)
        if self.children and len(self.children_ages) != self.children:
            missing.append("children_ages")
        return missing

    def to_search_request(self) -> HotelSearchRequest:
        meal_obj = None
        if self.meal_type:
            for m in MealType:
                if m.value.lower() == str(self.meal_type).lower():
                    meal_obj = m
                    break

        default_date = (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d")

        return HotelSearchRequest(
            city_from=self.city_from or "Astana",
            date_start=self.date_start or default_date,
            budget_kzt=self.budget_kzt or 1500000,
            country=self.country,
            nights=self.nights or 7,
            adults=self.adults if self.adults is not None else 2,
            children=self.children,
            children_ages=self.children_ages,
            stars=self.stars,
            meal_type=meal_obj,
            amenities=[],
        )


def _format_date_en(d_str: str | None) -> str:
    if not d_str:
        return ""
    try:
        return datetime.strptime(d_str.strip(), "%Y-%m-%d").strftime("%b %d")
    except Exception:
        return str(d_str)


def _format_date_ru(d_str: str | None) -> str:
    if not d_str:
        return ""
    try:
        dt = datetime.strptime(d_str.strip(), "%Y-%m-%d")
        months = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]
        return f"{dt.day} {months[dt.month - 1]}"
    except Exception:
        return str(d_str)


@dataclass
class TravelAgentSession:
    session_id: str = "default"
    context: TravelAgentContext = field(default_factory=TravelAgentContext)

    async def handle_message(
        self,
        message: str,
        history: list[dict[str, Any]] | None = None,
        lang: str | None = None,
    ) -> dict[str, Any]:
        parsed = await self._parse_message(message, history)
        self._merge(parsed)

        # If solo detected in this message, hard-set adults=1, children=0
        if _is_solo(message) and self.context.adults is None:
            self.context.adults = 1
            self.context.children = 0
            self.context.children_ages = []

        # Instant search rule: if country, nights, budget are present and adults is None -> default adults = 2
        if self.context.country and self.context.nights and self.context.budget_kzt and self.context.adults is None:
            self.context.adults = 2

        # If children count is set but ages are missing, default ages to 7
        if self.context.children > 0 and len(self.context.children_ages) != self.context.children:
            needed = self.context.children - len(self.context.children_ages)
            self.context.children_ages.extend([7] * needed)

        # Detect reply language: explicit lang flag has priority, otherwise script detection
        if lang in ("ru", "en"):
            is_russian = (lang == "ru")
        else:
            is_russian = bool(re.search(r'[а-яёА-ЯЁ]', message))

        # Destination guardrail: refuse unsupported routes immediately
        if self.context.country and self.context.country not in VALID_DESTINATIONS:
            unsupported = self.context.country
            self.context.country = None  # reset so user can try again
            if is_russian:
                refusal = (
                    f"К сожалению, VoyageAI пока не поддерживает прямые рейсы в «{unsupported}» из Казахстана. "
                    f"Мы работаем с проверенными маршрутами в: Турцию, ОАЭ, Таиланд, Египет, Вьетнам, Мальдивы, Бали (Индонезия), Грузию, Шри-Ланку и Испанию. "
                    f"Пожалуйста, выберите одно из этих направлений."
                )
            else:
                refusal = (
                    f"VoyageAI currently operates verified direct flight routes from Kazakhstan (NQZ/ALA) to: "
                    f"Turkey, UAE, Thailand, Egypt, Vietnam, Maldives, Bali (Indonesia), Georgia, Sri Lanka, and Spain. "
                    f"«{unsupported}» is not yet in our verified network. Please choose one of our supported destinations for guaranteed real-time rates."
                )
            return {
                "reply": refusal,
                "state": "INCOMPLETE",
                "status": "INCOMPLETE",
                "missing_fields": ["country"],
                "results": [],
                "prompts": build_seasonal_prompts(is_russian=is_russian),
                "slots": self.context.dict,
            }

        missing = self.context.missing_fields()
        if missing:
            return {
                "reply": self._build_question(missing, is_russian=is_russian),
                "state": "INCOMPLETE",
                "status": "INCOMPLETE",
                "missing_fields": missing,
                "results": [],
                "prompts": build_seasonal_prompts(is_russian=is_russian),
                "slots": self.context.dict,
            }

        request = self.context.to_search_request()
        recommendations = curate_top_five(mock_search_tourvisor_api(request), request)
        return {
            "reply": self._build_summary(request, recommendations, is_russian=is_russian),
            "state": "COMPLETE",
            "status": "COMPLETE",
            "missing_fields": [],
            "results": [item.model_dump(mode="json") for item in recommendations],
            "prompts": build_seasonal_prompts(is_russian=is_russian),
            "slots": self.context.dict,
            "flight": recommendations[0].flight.model_dump(mode="json") if recommendations and recommendations[0].flight else None,
        }


    def _merge(self, updates: dict[str, Any]) -> None:
        for key, value in updates.items():
            if value is None:
                continue
            if key == "children_ages":
                self.context.children_ages = list(value)
            elif key == "country":
                self.context.country = _normalize_country(value)
            elif key == "adults":
                self.context.adults = int(value)
            elif key == "budget_kzt":
                self.context.budget_kzt = int(value)
            elif key == "nights":
                self.context.nights = int(value)
            elif key == "date_start":
                norm_d = _normalize_date(str(value)) or _extract_date(str(value))
                if norm_d:
                    self.context.date_start = norm_d
            else:
                if hasattr(self.context, key):
                    setattr(self.context, key, value)

    async def _parse_message(self, message: str, history: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        text = (message or "").strip()
        if not text:
            return {}

        llm_parsed = await _llm_extract(text, history)
        fallback_parsed = _fallback_extract(text)
        merged: dict[str, Any] = {}

        for key in ["city_from", "date_start", "nights", "budget_kzt", "country", "adults", "children", "children_ages", "stars", "meal_type"]:
            if key in llm_parsed and llm_parsed[key] not in (None, "", [], {}):
                merged[key] = llm_parsed[key]
            elif key in fallback_parsed and fallback_parsed[key] not in (None, "", [], {}):
                merged[key] = fallback_parsed[key]

        return merged

    def _build_question(self, missing: list[str], *, is_russian: bool = False) -> str:
        if is_russian:
            if "country" in missing:
                return "Куда желаете полететь? Например: Турция, ОАЭ, Таиланд, Мальдивы, Вьетнам или Египет."
            if "date_start" in missing:
                return "Уточните, пожалуйста, на какую дату или месяц планируете вылет? (например: 14 октября или «ближайшие даты»)."
            if "nights" in missing:
                return "На сколько ночей планируете поездку? (например, 7 или 10 ночей)."
            if "adults" in missing:
                return "Сколько человек едет? (например: «я один», «двое взрослых», «семья с 1 ребёнком»)."
            if "children_ages" in missing:
                return "Укажите, пожалуйста, возраст каждого ребёнка, который поедет с вами."
            if "budget_kzt" in missing:
                return "Уточните, пожалуйста, ваш ориентировочный бюджет (в тенге или долларах, например $3 000 или 1 500 000 ₸)."
            return "Уточните направление, дату вылета, длительность и бюджет — подготовим персональный маршрут."
        else:
            if "country" in missing:
                return "Which destination would you like to explore? (e.g. Turkey, UAE, Thailand, Maldives, or Spain)."
            if "date_start" in missing:
                return "When are you planning to depart? (e.g., October 14, next month, or 'flexible dates')."
            if "nights" in missing:
                return "How many nights are you planning for your stay? (e.g. 7 nights or 10 nights)."
            if "adults" in missing:
                return "How many guests will be traveling? (e.g., 'solo / 1 adult', 'couple / 2 adults', or 'family with 1 child')."
            if "children_ages" in missing:
                return "Could you please specify the age of each child traveling with you?"
            if "budget_kzt" in missing:
                return "What is your target budget for the complete vacation package (in USD or KZT, e.g. $3,000 or 1,500,000 ₸)?"
            return "Please specify your target destination, departure date, duration, and budget to prepare your custom itinerary."

    def _build_summary(self, request: HotelSearchRequest, recommendations: list[HotelRecommendation], *, is_russian: bool = False) -> str:
        if not recommendations:
            if is_russian:
                return "По указанным критериям вариантов не найдено. Попробуйте немного увеличить бюджет или выбрать другое направление."
            return "No matching options found within these exact filters. Let's expand your budget slightly or select another destination."

        best = recommendations[0]
        passengers = request.adults + request.children
        budget_usd = round(request.budget_kzt / USD_TO_KZT)

        if is_russian:
            city_ru = {
                "Turkey": "Анталье", "UAE": "Дубае", "Thailand": "Пхукете",
                "Maldives": "Мальдивах", "Egypt": "Шарм-эль-Шейхе", "Vietnam": "Дананге",
                "Georgia": "Батуми", "Sri Lanka": "Шри-Ланке", "Indonesia": "Бали", "Spain": "Барселоне",
            }.get(request.country, request.country or "выбранном направлении")
            origin_ru = {"Astana": "Астаны", "Almaty": "Алматы", "Shymkent": "Шымкента"}.get(request.city_from, request.city_from)

            if passengers == 1:
                party_ru = "для вашей соло-поездки"
            elif request.children > 0:
                party_ru = "для вашей семьи"
            else:
                party_ru = "для вашей поездки"

            airline_str = f"с прямым перелетом {best.flight.airline} ({best.flight.departure_airport} ➔ {best.flight.arrival_airport})" if best.flight else "с прямым перелетом"
            dep_date_str = _format_date_ru(best.flight.departure_date if best.flight else request.date_start)

            return (
                f"Подобрал {party_ru} лучшие варианты в {city_ru} {airline_str} из {origin_ru} (вылет {dep_date_str}, {request.nights} ночей). "
                f"Топ-рекомендация — {best.hotel_name} ({best.stars}★, рейтинг {best.rating}/5). "
                f"Все 5 пакетов ниже включают проживание, выбранное питание и перелет в обе стороны."
            )
        else:
            city_en = {
                "Turkey": "Antalya", "UAE": "Dubai", "Thailand": "Phuket",
                "Maldives": "the Maldives", "Egypt": "Sharm El Sheikh", "Vietnam": "Da Nang",
                "Georgia": "Batumi", "Sri Lanka": "Sri Lanka", "Indonesia": "Bali", "Spain": "Barcelona",
            }.get(request.country, request.country or "your chosen destination")

            if passengers == 1:
                party_en = "for your solo trip"
            elif request.children > 0:
                party_en = "for your family holiday"
            else:
                party_en = "for your journey"

            if best.flight:
                airline_en = f"with direct {best.flight.airline} flights ({best.flight.departure_airport} → {best.flight.arrival_airport}"
            else:
                airline_en = "with direct roundtrip flights ("

            dep_date_en = _format_date_en(best.flight.departure_date if best.flight else request.date_start)
            dep_str = f", departing {dep_date_en}, {request.nights} nights)" if dep_date_en else f", {request.nights} nights)"

            return (
                f"Curated the best options {party_en} to {city_en} {airline_en}{dep_str}. "
                f"Top recommendation — {best.hotel_name} ({best.stars}★, rating {best.rating}/5). "
                f"All 5 packages below include accommodation, selected meal plan, and roundtrip flights."
            )



BADGES = [
    "🔥 Top Recommended",
    "⭐️ Highest Rating",
    "🌊 Beachfront Sanctuary",
    "💰 Best Value Package",
    "🌟 Ultra Luxury Retreat",
]


def curate_top_five(
    recommendations: list[HotelRecommendation],
    request: HotelSearchRequest,
) -> list[HotelRecommendation]:
    """Curates top 5 distinct properties ensuring country consistency."""
    if len(recommendations) < 5:
        known = {item.id for item in recommendations}
        # First relax budget & star rating but strictly keep destination country
        relaxed_same_country = request.model_copy(update={
            "stars": None,
            "meal_type": None,
            "budget_kzt": max(request.budget_kzt, 4_000_000),
        })
        same_country_candidates = mock_search_tourvisor_api(relaxed_same_country)
        for item in same_country_candidates:
            if item.id not in known:
                recommendations.append(item)
                known.add(item.id)

    if len(recommendations) < 5:
        # Fallback to worldwide luxury properties with reduced match score
        relaxed_global = request.model_copy(update={
            "country": None,
            "stars": None,
            "meal_type": None,
            "budget_kzt": max(request.budget_kzt, 4_000_000),
        })
        known = {item.id for item in recommendations}
        global_candidates = mock_search_tourvisor_api(relaxed_global)
        for item in global_candidates:
            if item.id not in known:
                item.match_score = 75
                recommendations.append(item)
                known.add(item.id)

    if len(recommendations) < 5:
        return recommendations

    ranked = sorted(recommendations, key=lambda item: (-item.match_score, -item.rating, item.total_price_kzt))
    selected = [ranked[0]]
    rules = [
        lambda item: item.total_price_kzt == min(c.total_price_kzt for c in ranked),
        lambda item: any("beach" in a.value.lower() or "first line" in a.value.lower() for a in item.matched_amenities),
        lambda item: item.rating == max(c.rating for c in ranked),
        lambda item: item.stars == 5 and any(r.vip_privileges for r in item.room_options),
    ]
    for rule in rules:
        choice = next((item for item in ranked if item not in selected and rule(item)), None)
        if choice:
            selected.append(choice)

    for item in ranked:
        if len(selected) == 5:
            break
        if item not in selected:
            selected.append(item)

    for item, badge in zip(selected, BADGES):
        item.highlight_badge = badge

    return selected[:5]


async def process_chat_message(
    session_id: str,
    message: str,
    history: list[dict[str, Any]] | None = None,
    sessions: dict[str, TravelAgentSession] | None = None,
    lang: str | None = None,
) -> dict[str, Any]:
    """Processes conversational messages and persists context across turns."""
    if sessions is None:
        sessions = {}
    session = sessions.setdefault(session_id, TravelAgentSession(session_id=session_id))

    is_russian = (lang == "ru") if lang in ("ru", "en") else bool(re.search(r'[а-яёА-ЯЁ]', message or ""))

    if not message or not message.strip():
        greeting = (
            "Здравствуйте! Я ваш автономный AI-консьерж VoyageAI. "
            "Куда бы вы хотели отправиться, на сколько ночей, какой состав гостей и бюджет?"
            if is_russian else GREETING_MESSAGE
        )
        return {
            "reply": greeting,
            "state": "INCOMPLETE",
            "status": "INCOMPLETE",
            "missing_fields": session.context.missing_fields(),
            "results": [],
            "prompts": build_seasonal_prompts(is_russian=is_russian),
            "slots": _empty_slots(),
        }

    if _is_greeting(message):
        greeting = (
            "Здравствуйте! Я ваш персональный AI-консьерж VoyageAI. "
            "Уточните направление, дату вылета, состав гостей и ориентировочный бюджет."
            if is_russian else GREETING_MESSAGE
        )
        return {
            "reply": greeting,
            "state": "INCOMPLETE",
            "status": "INCOMPLETE",
            "missing_fields": session.context.missing_fields(),
            "results": [],
            "prompts": build_seasonal_prompts(is_russian=is_russian),
            "slots": _empty_slots() if not session.context.country else session.context.dict,
        }

    try:
        return await session.handle_message(message, history=history, lang=lang)
    except OpenRouterAPIError:
        error_msg = (
            "В данный момент VoyageAI обновляет поисковые шлюзы. Пожалуйста, повторите запрос через несколько секунд."
            if is_russian
            else "VoyageAI is currently refreshing connection. Please resend your message in a few moments."
        )
        return {
            "reply": error_msg,
            "state": "INCOMPLETE",
            "status": "INCOMPLETE",
            "missing_fields": session.context.missing_fields(),
            "results": [],
            "prompts": build_seasonal_prompts(is_russian=is_russian),
            "slots": session.context.dict,
            "error": "service_unavailable",
        }


def _is_greeting(message: str) -> bool:
    normalized = re.sub(r"[^a-zа-яё\s]", "", message.lower()).strip()
    return normalized in {
        "hi", "hello", "hey", "good morning", "good evening", "greetings",
        "привет", "здравствуйте", "здравствуй", "добрый день", "доброе утро", "салам",
    }


def _empty_slots() -> dict[str, Any]:
    return {
        "city_from": "Astana",
        "country": None,
        "date_start": None,
        "nights": None,
        "budget_kzt": None,
        "adults": None,
        "children": None,
        "children_ages": None,
        "stars": None,
        "meal_type": None,
        "amenities": None,
    }