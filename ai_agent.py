"""Conversational travel extraction backed by OpenRouter / OpenAI SDK."""

from __future__ import annotations

import json
import re
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency
    OpenAI = None  # type: ignore[assignment]

from hotel_search import (
    Amenity,
    HotelRecommendation,
    HotelSearchRequest,
    MealType,
    mock_search_tourvisor_api,
)


OPENROUTER_API_KEY = "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"
OPENROUTER_MODEL = "meta-llama/llama-3.1-8b-instruct:free"
FREE_MODELS = [
    "meta-llama/llama-3.1-8b-instruct:free",
    "google/gemini-2.0-flash-lite-001",
    "mistralai/mistral-7b-instruct:free",
]
OPENROUTER_HEADERS = {
    "HTTP-Referer": "http://localhost:8000",
    "X-Title": "Zari Travel AI",
}
GREETING_MESSAGE = "Привет! Я ваш ИИ-турагент Zari Travel. Расскажите, куда хотите поехать, на сколько ночей и какой у вас бюджет?"
SYSTEM_PROMPT = """
Ты — вежливый ИИ-турагент Zari Travel. Извлекай параметры тура и отвечай на русском.
Возвращай valid JSON без markdown и без лишнего текста:
{
    "slots": {
        "destination": "Страна/город или null",
        "nights": число или null,
        "adults": число или null,
        "budget_kzt": число или null
    },
    "status": "INCOMPLETE" или "COMPLETE",
    "reply": "Твой вопрос или сообщение пользователю"
}
Если собраны страна/направление, ночи, взрослые и бюджет — status = "COMPLETE".
"""

client = (
    OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        default_headers=OPENROUTER_HEADERS,
    )
    if OpenAI is not None
    else None
)


class OpenRouterAPIError(RuntimeError):
    """OpenRouter request failed and must be reported without a server error."""


SEASONAL_PROMPTS = {
    "winter": [
        "Семейный тур в Египет из Астаны с 2026-12-20 на 7 ночей: 2 взрослых, ребенок 4 года, первая линия, до 1 400 000 ₸",
        "Отдых в ОАЭ из Алматы с 2026-12-20 на 7 ночей: 2 взрослых, ребенок 6 лет, 5 звезд, до 2 200 000 ₸",
        "Пляжный отдых в Таиланде из Алматы с 2027-01-15 на 8 ночей: 2 взрослых, дети 3 и 7 лет, до 1 800 000 ₸",
        "Ультра все включено в Египте из Астаны с 2026-12-20 на 7 ночей: 2 взрослых, до 1 500 000 ₸",
    ],
    "spring": [
        "Семейный тур в Турцию из Астаны с 2027-04-15 на 7 ночей: 2 взрослых, ребенок 5 лет, до 1 200 000 ₸",
        "Отдых во Вьетнаме из Алматы с 2027-04-15 на 10 ночей: 2 взрослых, ребенок 2 года, до 1 700 000 ₸",
        "Пляжный отдых в Турции из Алматы с 2027-04-15 на 7 ночей: 2 взрослых, до 1 000 000 ₸",
        "Премиум отдых в ОАЭ из Астаны с 2027-04-15 на 7 ночей: 2 взрослых, 5 звезд, до 2 000 000 ₸",
    ],
    "summer": [
        "Семейный тур в Турцию из Астаны с 2027-07-10 на 7 ночей: 2 взрослых, ребенок 4 года, первая линия, до 1 400 000 ₸",
        "Ультра все включено в Египте из Алматы с 2027-07-10 на 7 ночей: 2 взрослых, до 1 300 000 ₸",
        "Пляжный отдых во Вьетнаме из Астаны с 2027-07-10 на 10 ночей: 2 взрослых, до 1 800 000 ₸",
        "Роскошный отдых в ОАЭ из Алматы с 2027-07-10 на 7 ночей: 2 взрослых, 5 звезд, до 2 300 000 ₸",
    ],
    "autumn": [
        "Семейный тур в Таиланде из Алматы с 2026-10-10 на 7 ночей: 2 взрослых, ребенок 3 года, до 1 300 000 ₸",
        "Тихий отдых в Египте из Астаны с 2026-10-10 на 7 ночей: 2 взрослых, ребенок 4 года, до 1 200 000 ₸",
        "Премиум отдых в ОАЭ из Алматы с 2026-10-10 на 7 ночей: 2 взрослых, ребенок 8 лет, 5 звезд, до 2 000 000 ₸",
        "Отдых в Турции из Астаны с 2026-10-10 на 9 ночей: 2 взрослых, ребенок 6 лет, до 1 500 000 ₸",
    ],
}

CITY_ALIASES = {
    "астаны": "Астана",
    "астана": "Астана",
    "алматы": "Алматы",
    "шымкента": "Шымкент",
    "караганды": "Караганда",
    "актау": "Актау",
    "павлодара": "Павлодар",
    "алмате": "Алматы",
    "астане": "Астана",
}

CITY_NAMES = {
    "астана", "алматы", "шымкент", "нур-султан", "караганда", "актау", "урал", "павлодар",
    "сочи", "москва", "санкт-петербург", "казань", "уфа", "ереван", "минск",
}

COUNTRY_ALIASES = {
    "турция": "Турция",
    "турции": "Турция",
    "египет": "Египет",
    "египте": "Египет",
    "оаэ": "ОАЭ",
    "дубай": "ОАЭ",
    "пхукет": "Таиланд",
    "эмираты": "ОАЭ",
    "арабские эмираты": "ОАЭ",
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

MEAL_ALIASES = {
    "all inclusive": "AI - Все включено",
    "ai": "AI - Все включено",
    "ультра все включено": "UAI - Ультра все включено",
    "uai": "UAI - Ультра все включено",
    "полный пансион": "FB - Полный пансион",
    "fb": "FB - Полный пансион",
    "завтраки": "BB - Завтраки",
    "bb": "BB - Завтраки",
    "завтрак": "BB - Завтраки",
    "breakfast": "BB - Завтраки",
}

AMENITY_ALIASES = {
    "wifi": "wifi",
    "wi-fi": "wifi",
    "включено": "все включено",
    "все включено": "все включено",
    "аквапарк": "аквапарк",
    "детский клуб": "детский клуб",
    "детский": "детский клуб",
    "песчаный пляж": "песчаный пляж",
    "свой пляж": "свой пляж",
    "пляж": "свой пляж",
    "первая линия": "первая линия",
    "первой линией": "первая линия",
    "first line": "первая линия",
    "beachfront": "первая линия",
    "waterpark": "аквапарк",
    "kids club": "детский клуб",
}

NUMBER_WORDS = {
    "ноль": 0, "один": 1, "одна": 1, "одного": 1, "два": 2, "двое": 2, "двух": 2,
    "три": 3, "трое": 3, "четыре": 4, "пять": 5, "шесть": 6, "семь": 7,
    "восемь": 8, "девять": 9, "десять": 10, "одиннадцать": 11, "двенадцать": 12,
    "тринадцать": 13, "четырнадцать": 14, "пятнадцать": 15, "шестнадцать": 16,
    "семнадцать": 17, "восемнадцать": 18, "девятнадцать": 19, "двадцать": 20,
}


def _season_name() -> str:
    month = datetime.now().month
    if month in (12, 1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    return "autumn"


def build_seasonal_prompts() -> list[str]:
    return SEASONAL_PROMPTS.get(_season_name(), SEASONAL_PROMPTS["summer"])[:4]


def _normalize_text(value: Any) -> str:
    return str(value).strip().lower() if value is not None else ""


def _normalize_country(value: Any) -> str | None:
    text = _normalize_text(value)
    if not text:
        return None
    normalized = COUNTRY_ALIASES.get(text, text)
    return normalized if normalized in set(COUNTRY_ALIASES.values()) else text.title()


def _normalize_amenity(value: Any) -> str:
    text = _normalize_text(value)
    if not text:
        return ""
    return AMENITY_ALIASES.get(text, text)


def _normalize_date(raw: str | None) -> str | None:
    if not raw:
        return None
    text = raw.strip()
    if not text:
        return None
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return text
    if re.fullmatch(r"\d{2}\.\d{2}\.\d{4}", text):
        day, month, year = text.split(".")
        return f"{year}-{month}-{day}"

    month_map = {
        "января": "01", "февраля": "02", "марта": "03", "апреля": "04", "мая": "05",
        "июня": "06", "июля": "07", "августа": "08", "сентября": "09", "октября": "10",
        "ноября": "11", "декабря": "12",
    }
    match = re.search(r"(\d{1,2})\s*(?:\.|\s+)?([а-я]+)\s*(\d{4})", text, flags=re.IGNORECASE)
    if match:
        day, month_name, year = match.groups()
        month = month_map.get(month_name.lower(), month_name)
        if month.isdigit() and len(month) == 1:
            month = f"0{month}"
        return f"{year}-{month}-{day.zfill(2)}"
    try:
        return datetime.strptime(text, "%d %B %Y").strftime("%Y-%m-%d")
    except ValueError:
        return None


def _extract_numeric_value(text: str) -> int | None:
    for word, number in NUMBER_WORDS.items():
        if re.search(rf"\b{word}\b", text):
            return number
    match = re.search(r"\b(\d+)\b", text)
    if match:
        return int(match.group(1))
    return None


def _extract_city(text: str) -> str | None:
    text_l = text.lower()
    for alias, canonical in CITY_ALIASES.items():
        if re.search(rf"\b{re.escape(alias)}\b", text_l):
            return canonical
    for city in sorted(CITY_NAMES, key=len, reverse=True):
        if city in text_l:
            return city.title().replace("-", "-")
    return None


def _extract_country(text: str) -> str | None:
    for alias, canonical in COUNTRY_ALIASES.items():
        if alias in text.lower():
            return canonical
    return None


def _extract_budget(text: str) -> int | None:
    matches = re.findall(r"(?:до|не\s*более|budget|бюджет)[^\d]*(\d[\d\s\u00A0]*)\s*(?:т|тенге|kzt|₸)", text, flags=re.IGNORECASE)
    if not matches:
        matches = re.findall(r"(\d[\d\s\u00A0]*)\s*(?:т|тенге|kzt|₸)", text, flags=re.IGNORECASE)
    if not matches:
        plain_numbers = re.findall(r"\b\d[\d\s\u00A0]{5,}\b", text)
        for candidate in plain_numbers:
            value = candidate.replace(" ", "").replace("\u00A0", "")
            if value.isdigit() and int(value) >= 100000:
                return int(value)
        return None
    value = matches[0].replace(" ", "").replace("\u00A0", "")
    try:
        return int(float(value))
    except ValueError:
        return None


def _extract_nights(text: str) -> int | None:
    match = re.search(r"(\d+|один|два|три|четыре|пять|шесть|семь|восемь|девять|десять)\s*(?:ноч(?:ей|ь)|night|nights)", text, flags=re.IGNORECASE)
    if not match:
        return None
    token = match.group(1).lower()
    if token.isdigit():
        return int(token)
    return NUMBER_WORDS.get(token)


def _extract_adults(text: str) -> int | None:
    if re.search(r"\bдвоих\b", text, flags=re.IGNORECASE):
        return 2
    match = re.search(r"(\d+|один|двое|два|три|четыре|пять|шесть)\s*(?:взросл(?:ых|ый)?|adult|adults)", text, flags=re.IGNORECASE)
    if not match:
        return None
    token = match.group(1).lower()
    if token.isdigit():
        return int(token)
    if token in {"двое", "двоих"}:
        return 2
    return NUMBER_WORDS.get(token)


def _extract_children(text: str) -> int | None:
    match = re.search(r"(?:\b(\d+|один|два|двое|три|четыре|пять|шесть)\s*(?:дет(?:ей|и)|ребен(?:ок|ка)|child|children)\b)", text, flags=re.IGNORECASE)
    if not match:
        return None
    token = match.group(1).lower()
    if token.isdigit():
        return int(token)
    return NUMBER_WORDS.get(token)


def _extract_children_ages(text: str) -> list[int] | None:
    matches = re.findall(r"\b(\d{1,2})\s*(?:лет|года|год|years|yrs|years old)\b", text, flags=re.IGNORECASE)
    if matches:
        return [int(m) for m in matches]
    return None


def _extract_meal(text: str) -> str | None:
    lowered = text.lower()
    for alias, value in MEAL_ALIASES.items():
        if alias in lowered:
            return value
    return None


def _extract_amenities(text: str) -> list[str]:
    found: list[str] = []
    lowered = text.lower()
    for alias, canonical in AMENITY_ALIASES.items():
        if alias in lowered:
            found.append(canonical)
    return list(dict.fromkeys(found))


def _extract_stars(text: str) -> int | None:
    match = re.search(r"(3|4|5)\s*(?:\*|зв(?:езд|езды|ёзд)|stars?)", text, flags=re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def _extract_date_from_text(text: str) -> str | None:
    date_match = re.search(
        r"(\d{4}-\d{2}-\d{2}|\d{2}\.\d{2}\.\d{4}|\d{1,2}\s+(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря))",
        text,
        flags=re.IGNORECASE,
    )
    if not date_match:
        return None
    return _normalize_date(date_match.group(1))


def _fallback_extract(text: str) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    city = _extract_city(text)
    if city:
        parsed["city_from"] = city
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
    if children:
        parsed["children"] = children
    ages = _extract_children_ages(text)
    if ages:
        parsed["children_ages"] = ages
    if ages and "children" not in parsed:
        parsed["children"] = len(ages)
    meal = _extract_meal(text)
    if meal:
        parsed["meal_type"] = meal
    amenities = _extract_amenities(text)
    if amenities:
        parsed["amenities"] = amenities
    stars = _extract_stars(text)
    if stars:
        parsed["stars"] = stars
    date_value = _extract_date_from_text(text)
    if date_value:
        parsed["date_start"] = date_value
    return parsed


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
        if key in {"children_ages", "amenities"} and isinstance(value, list):
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


def clean_json_response(raw_text: str) -> dict[str, Any]:
    """Extract JSON from plain text or a markdown code block."""
    text = (raw_text or "").strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE | re.DOTALL).strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    return json.loads(text)


def local_fallback_parser(user_message: str) -> dict[str, Any]:
    """Extract the basic search slots when all external models are unavailable."""
    parsed = _fallback_extract(user_message.lower())
    slots = {
        "destination": parsed.get("country"),
        "nights": parsed.get("nights"),
        "adults": parsed.get("adults"),
        "budget_kzt": parsed.get("budget_kzt"),
    }
    complete = all(slots.values())
    return {
        "slots": slots,
        "status": "COMPLETE" if complete else "INCOMPLETE",
        "reply": "Отлично! Ищу лучшие варианты..." if complete else "Принято! Уточните направление или бюджет.",
        "country": slots["destination"],
        "nights": slots["nights"],
        "adults": slots["adults"],
        "budget_kzt": slots["budget_kzt"],
        **parsed,
    }


def _llm_extract(message: str, history: list[dict[str, Any]] | None = None) -> dict[str, Any]:
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
        for model in FREE_MODELS:
            try:
                print(f"[AI Agent] Trying model: {model}", flush=True)
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.1,
                    timeout=8,
                )
                raw_text = response.choices[0].message.content or ""
                parsed = clean_json_response(raw_text)
                return _coerce_llm_payload(parsed)
            except Exception as error:
                print(f"[AI Agent] Model {model} failed: {error}", flush=True)

    print("[AI Agent] All AI models failed. Using local fallback parser.", flush=True)
    return local_fallback_parser(message)


@dataclass
class TravelAgentContext:
    city_from: str | None = None
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
        required = ["country", "budget_kzt", "nights", "adults"]
        missing: list[str] = []
        for name in required:
            if getattr(self, name) is None:
                missing.append(name)
        if self.children and len(self.children_ages) != self.children:
            missing.append("children_ages")
        return missing

    def to_search_request(self) -> HotelSearchRequest:
        meal_value = self.meal_type
        normalized_meal = None
        if meal_value:
            for item in MealType:
                if item.value.lower() == str(meal_value).lower():
                    normalized_meal = item
                    break
            if normalized_meal is None and "все включено" in str(meal_value).lower():
                normalized_meal = MealType.AI

        amenities: list[Amenity] = []
        for item in self.amenities:
            candidate = _normalize_amenity(item)
            for enum_value in Amenity:
                if enum_value.value == candidate:
                    amenities.append(enum_value)
                    break

        return HotelSearchRequest(
            city_from=self.city_from or "Астана",
            date_start=self.date_start or "2026-10-10",
            budget_kzt=self.budget_kzt or 1500000,
            country=self.country,
            nights=self.nights or 7,
            adults=self.adults or 2,
            children=self.children,
            children_ages=self.children_ages,
            stars=self.stars,
            meal_type=normalized_meal,
            amenities=amenities,
        )


@dataclass
class TravelAgentSession:
    context: TravelAgentContext = field(default_factory=TravelAgentContext)

    def handle_message(self, message: str, history: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        parsed = self._parse_message(message, history)
        self._merge(parsed)

        missing = self.context.missing_fields()
        if missing:
            return {
                "reply": self._build_question(missing),
                "state": "INCOMPLETE",
                "status": "INCOMPLETE",
                "missing_fields": missing,
                "results": [],
                "prompts": build_seasonal_prompts(),
                "slots": self.context.dict,
            }

        request = self.context.to_search_request()
        recommendations = curate_top_five(mock_search_tourvisor_api(request), request)
        return {
            "reply": self._build_summary(request, recommendations),
            "state": "COMPLETE",
            "status": "COMPLETE",
            "missing_fields": [],
            "results": [item.model_dump(mode="json") for item in recommendations],
            "prompts": build_seasonal_prompts(),
            "slots": self.context.dict,
        }

    def _merge(self, updates: dict[str, Any]) -> None:
        for key, value in updates.items():
            if value is None:
                continue
            if key == "children_ages":
                self.context.children_ages = list(value)
            elif key == "amenities":
                merged = list(dict.fromkeys(_normalize_amenity(item) for item in value if item))
                self.context.amenities = [item for item in merged if item]
            elif key == "country":
                self.context.country = _normalize_country(value)
            else:
                setattr(self.context, key, value)

    def _parse_message(self, message: str, history: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        text = (message or "").strip()
        if not text:
            return {}

        llm_parsed = _llm_extract(text, history)
        fallback_parsed = _fallback_extract(text)
        merged: dict[str, Any] = {}

        for key in [
            "city_from", "date_start", "nights", "budget_kzt", "country", "adults",
            "children", "children_ages", "stars", "meal_type", "amenities",
        ]:
            if key in llm_parsed and llm_parsed[key] not in (None, "", [], {}):
                merged[key] = llm_parsed[key]
            elif key in fallback_parsed and fallback_parsed[key] not in (None, "", [], {}):
                merged[key] = fallback_parsed[key]

        if "meal_type" in merged and isinstance(merged["meal_type"], str):
            merged["meal_type"] = _normalize_meal_value(merged["meal_type"])

        return merged

    def _build_question(self, missing: list[str]) -> str:
        if "city_from" in missing:
            return "Сначала уточню маршрут: откуда у вас вылет? Например: «Вылет из Астаны» или «Из Алматы»."
        if "date_start" in missing:
            return "Когда планируете вылет и на сколько ночей? Напишите дату или пример: «с 12 октября на 7 ночей»."
        if "budget_kzt" in missing:
            return "Какой бюджет на весь тур в тенге? Например: «до 1 500 000 ₸ для семьи»."
        if "nights" in missing:
            return "На сколько ночей планируете поездку?"
        if "adults" in missing:
            return "Сколько взрослых летит в поездку?"
        if "children_ages" in missing:
            return "Уточните точный возраст каждого ребенка, чтобы я подобрал корректный номер и условия проживания."
        return "Небольшое уточнение: напишите, пожалуйста, бюджет, даты и состав семьи, чтобы я мог подобрать точные варианты."

    def _build_summary(self, request: HotelSearchRequest, recommendations: list[HotelRecommendation]) -> str:
        if not recommendations:
            return "По этим параметрам я не нашел подходящих вариантов. Давайте слегка расширим бюджет, даты или выберем другой курорт."
        best = recommendations[0]
        return (
            f"Подобрал для вас Top 5 вариантов. Лучший матч — {best.hotel_name} "
            f"({best.match_score}% совпадения): {best.summary} "
            f"Семья {request.adults + request.children} человек, бюджет до {request.budget_kzt:,} ₸ — это хороший баланс цены, пляжа и удобств."
        )


def _normalize_meal_value(value: str | MealType | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    lowered = text.lower()
    for alias, canonical in MEAL_ALIASES.items():
        if lowered == alias or lowered == canonical.lower():
            return canonical
    for candidate in MealType:
        if candidate.value.lower() == lowered:
            return candidate.value
    return text


BADGES = [
    "🔥 Горящее предложение",
    "⭐️ Высший рейтинг",
    "🌊 Ближайший к морю",
    "💰 Лучшая цена",
    "👑 Премиум выбор",
]


def curate_top_five(
    recommendations: list[HotelRecommendation],
    request: HotelSearchRequest,
) -> list[HotelRecommendation]:
    if len(recommendations) < 5:
        relaxed = request.model_copy(update={
            "country": None,
            "stars": None,
            "meal_type": None,
            "amenities": [],
            "budget_kzt": max(request.budget_kzt, 2_500_000),
        })
        candidates = mock_search_tourvisor_api(relaxed)
        known = {item.id for item in recommendations}
        recommendations.extend(item for item in candidates if item.id not in known)

    if len(recommendations) < 5:
        return recommendations

    ranked = sorted(recommendations, key=lambda item: (-item.match_score, -item.rating, item.total_price_kzt))
    selected = [ranked[0]]
    rules = [
        lambda item: item.total_price_kzt == min(candidate.total_price_kzt for candidate in ranked),
        lambda item: "первая линия" in [amenity.value for amenity in item.matched_amenities],
        lambda item: item.rating == max(candidate.rating for candidate in ranked),
        lambda item: item.stars == 5 and any(room.vip_privileges for room in item.room_options),
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


def process_chat_message(
    session_id: str,
    message: str,
    history: list[dict[str, Any]] | None = None,
    sessions: dict[str, TravelAgentSession] | None = None,
) -> dict[str, Any]:
    print("[AI Agent] Using OpenRouter API key: sk-or-v1-f664...", flush=True)

    if sessions is None:
        sessions = {}
    session = sessions.setdefault(session_id, TravelAgentSession())

    if not message or not message.strip():
        return {
            "reply": GREETING_MESSAGE,
            "state": "INCOMPLETE",
            "status": "INCOMPLETE",
            "missing_fields": session.context.missing_fields(),
            "results": [],
            "prompts": build_seasonal_prompts(),
            "slots": _empty_slots(),
        }

    if _is_greeting(message):
        return {
            "reply": GREETING_MESSAGE,
            "state": "INCOMPLETE",
            "status": "INCOMPLETE",
            "missing_fields": session.context.missing_fields(),
            "results": [],
            "prompts": build_seasonal_prompts(),
            "slots": _empty_slots() if not session.context.country else session.context.dict,
        }

    try:
        return session.handle_message(message, history=history)
    except OpenRouterAPIError:
        return {
            "reply": "Сейчас не удалось связаться с AI-сервисом. Попробуйте отправить запрос ещё раз через несколько секунд.",
            "state": "INCOMPLETE",
            "status": "INCOMPLETE",
            "missing_fields": session.context.missing_fields(),
            "results": [],
            "prompts": build_seasonal_prompts(),
            "slots": session.context.dict,
            "error": "openrouter_unavailable",
        }


def _is_greeting(message: str) -> bool:
    normalized = re.sub(r"[^а-яёa-z\s]", "", message.lower()).strip()
    return normalized in {"привет", "здравствуйте", "здравствуй", "добрый день", "доброе утро", "добрый вечер", "hi", "hello"}


def _empty_slots() -> dict[str, Any]:
    return {
        "city_from": None,
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