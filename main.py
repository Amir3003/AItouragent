"""FastAPI-сервер и API для демонстрационного поиска Zari Travel."""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from ai_agent import TravelAgentSession, build_seasonal_prompts, curate_top_five, process_chat_message
from hotel_search import (
    Amenity,
    COUNTRIES,
    HotelRecommendation,
    HotelSearchRequest,
    MealType,
    mock_search_tourvisor_api,
)
from hotel_database import count_hotels, countries_counts


app = FastAPI(title="Zari Travel API", version="1.0.0")
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
FRONTEND_FILE = STATIC_DIR / "index.html"
AGENT_SESSIONS: dict[str, TravelAgentSession] = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

# Отдаём картинки/иконки/будущие ассеты напрямую из /static, если они там появятся.
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Возвращает аккуратные подсказки вместо технических ошибок Pydantic."""

    field_messages = {
        "city_from": "Укажите город вылета минимум из 2 символов.",
        "date_start": "Укажите дату в формате YYYY-MM-DD.",
        "budget_kzt": "Укажите реальный бюджет больше 0 тенге.",
        "country": "Выберите страну из списка.",
        "nights": "Количество ночей должно быть от 1 до 30.",
        "adults": "Количество взрослых должно быть от 1 до 6.",
        "children": "Количество детей должно быть от 0 до 4.",
        "children_ages": "Укажите возраст каждого ребенка от 0 до 17 лет.",
        "stars": "Минимальная звездность может быть только 3, 4 или 5.",
        "meal_type": "Выберите доступный тип питания.",
        "amenities": "Выберите удобства из списка.",
    }
    errors: list[dict[str, str]] = []
    for error in exc.errors():
        field = str(error["loc"][-1])
        if field == "body":
            errors.append({
                "field": "children_ages",
                "message": "Количество возрастов детей должно совпадать с числом детей.",
            })
            continue
        errors.append({
            "field": field,
            "message": field_messages.get(field, "Проверьте это поле."),
        })
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Проверьте параметры поиска.",
            "errors": errors,
        },
    )


@app.get("/")
def frontend() -> FileResponse:
    """Отдает демонстрационный интерфейс поиска отелей."""

    return FileResponse(FRONTEND_FILE)


@app.get("/health")
def health_check() -> dict[str, object]:
    """Техническая проверка, что API и БД работают и без дублей."""

    return {
        "status": "ok",
        "message": "Zari Travel API is running",
        "hotels_total": count_hotels(),
        "hotels_by_country": countries_counts(),
    }


@app.get("/api/v1/meta")
def search_meta() -> dict[str, object]:
    """Отдает фронтенду списки для выпадающих фильтров (страны/питание/удобства)."""

    return {
        "countries": COUNTRIES,
        "meal_types": [{"value": meal.value, "label": meal.value} for meal in MealType],
        "amenities": [{"value": amenity.value, "label": amenity.value} for amenity in Amenity if amenity != Amenity.ALL_INCLUSIVE],
        "star_options": [3, 4, 5],
        "hotels_total": count_hotels(),
    }


@app.post("/api/v1/search", response_model=list[HotelRecommendation])
def search_hotels(request: HotelSearchRequest) -> list[HotelRecommendation]:
    """Валидирует запрос и возвращает подходящие моковые отели."""

    return curate_top_five(mock_search_tourvisor_api(request), request)


@app.post("/api/agent/chat")
async def agent_chat(request: Request) -> dict[str, object]:
    """Чат-эндпоинт с LLM-экстракцией и безопасным fallback для реальных пользовательских сообщений."""

    try:
        try:
            payload = await request.json()
        except Exception:
            payload = {}

        if not isinstance(payload, dict):
            payload = {}

        message = str(payload.get("message", "") or "").strip()
        session_id = str(payload.get("session_id") or "default")
        history = payload.get("history") if isinstance(payload.get("history"), list) else []

        result = process_chat_message(
            session_id=session_id,
            message=message,
            history=history,
            sessions=AGENT_SESSIONS,
        )
        return result
    except Exception:
        return {
            "reply": "Не удалось обработать запрос. Попробуйте ещё раз короче или уточните бюджет, даты и состав семьи.",
            "state": "INCOMPLETE",
            "status": "INCOMPLETE",
            "missing_fields": ["city_from", "date_start", "budget_kzt"],
            "results": [],
            "prompts": build_seasonal_prompts(),
            "slots": {},
        }
