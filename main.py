"""FastAPI server and API for VoyageAI: Autonomous Travel Concierge."""

import dataclasses
import json
import sqlite3
import traceback
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from ai_agent import (
    TravelAgentContext,
    TravelAgentSession,
    build_seasonal_prompts,
    curate_top_five,
    process_chat_message,
)
from hotel_database import count_hotels, countries_counts
from hotel_search import (
    COUNTRIES,
    Amenity,
    HotelRecommendation,
    HotelSearchRequest,
    MealType,
    mock_search_tourvisor_api,
)

app = FastAPI(title="VoyageAI API", version="2.0.0")
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
FRONTEND_FILE = STATIC_DIR / "index.html"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Returns elegant user-facing prompts for validation errors."""
    field_messages = {
        "city_from": "Please specify a valid departure city (minimum 2 characters).",
        "date_start": "Please provide a valid date in YYYY-MM-DD format.",
        "budget_kzt": "Please specify a realistic travel budget greater than 0.",
        "country": "Please select a destination from our curated portfolio.",
        "nights": "Trip duration must be between 1 and 30 nights.",
        "adults": "Number of adult guests must be between 1 and 6.",
        "children": "Number of children must be between 0 and 4.",
        "children_ages": "Please indicate the age of each child (0 to 17 years).",
        "stars": "Star category must be 3, 4, or 5 stars.",
        "meal_type": "Please select a supported board type.",
        "amenities": "Please select amenities from the catalog.",
    }
    errors: list[dict[str, str]] = []
    for error in exc.errors():
        field = str(error["loc"][-1])
        if field == "body":
            errors.append({
                "field": "children_ages",
                "message": "Number of ages specified must match the number of children.",
            })
            continue
        errors.append({
            "field": field,
            "message": field_messages.get(field, "Please verify this field."),
        })
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Please review your search criteria.",
            "errors": errors,
        },
    )


@app.get("/")
def frontend() -> FileResponse:
    """Delivers the VoyageAI luxury concierge web interface."""
    return FileResponse(FRONTEND_FILE)


@app.get("/health")
def health_check() -> dict[str, object]:
    """Health check endpoint verifying DB integrity and property counts."""
    return {
        "status": "ok",
        "message": "VoyageAI Autonomous Travel Concierge is operational",
        "hotels_total": count_hotels(),
        "hotels_by_country": countries_counts(),
    }


@app.get("/api/v1/meta")
def search_meta() -> dict[str, object]:
    """Provides frontend filter options (countries, board types, amenities)."""
    return {
        "countries": COUNTRIES,
        "meal_types": [{"value": meal.value, "label": meal.value} for meal in MealType],
        "amenities": [{"value": amenity.value, "label": amenity.value} for amenity in Amenity if amenity != Amenity.ALL_INCLUSIVE],
        "star_options": [3, 4, 5],
        "hotels_total": count_hotels(),
    }


@app.post("/api/v1/search", response_model=list[HotelRecommendation])
def search_hotels(request: HotelSearchRequest) -> list[HotelRecommendation]:
    """Direct search endpoint for filtered luxury hotel packages."""
    return curate_top_five(mock_search_tourvisor_api(request), request)


def get_session_from_db(session_id: str) -> TravelAgentSession:
    """Loads session state from SQLite or creates a new session."""
    conn = sqlite3.connect("zari_travel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM sessions WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        try:
            raw = json.loads(row[0])
            context_raw = raw.get("context", {})
            context = TravelAgentContext(**context_raw) if isinstance(context_raw, dict) else TravelAgentContext()
            return TravelAgentSession(session_id=raw.get("session_id", session_id), context=context)
        except Exception as e:
            print(f"[DB] Session restore warning for {session_id}: {repr(e)}", flush=True)
    return TravelAgentSession(session_id=session_id)


def save_session_to_db(session: TravelAgentSession) -> None:
    """Persists session state into SQLite."""
    data = dataclasses.asdict(session)
    conn = sqlite3.connect("zari_travel.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sessions (session_id, data) VALUES (?, ?)
        ON CONFLICT(session_id) DO UPDATE SET data=excluded.data, updated_at=CURRENT_TIMESTAMP
    """, (session.session_id, json.dumps(data)))
    conn.commit()
    conn.close()


@app.post("/api/agent/chat")
async def agent_chat(request: Request) -> dict[str, object]:
    """Conversational AI agent endpoint with state persistence and graceful fallback."""
    try:
        try:
            payload = await request.json()
        except Exception:
            payload = {}

        if not isinstance(payload, dict):
            payload = {}

        message = str(payload.get("message", "")).strip()
        session_id = str(payload.get("session_id") or "default")
        history = payload.get("history") if isinstance(payload.get("history"), list) else []
        lang = str(payload.get("lang") or "").lower().strip()
        if lang not in ("ru", "en"):
            lang = None

        # Load session from SQLite database
        session = get_session_from_db(session_id)
        sessions: dict[str, TravelAgentSession] = {session_id: session}

        result = await process_chat_message(
            session_id=session_id,
            message=message,
            history=history,
            sessions=sessions,
            lang=lang,
        )

        # Save mutated session back to DB
        updated_session = sessions.get(session_id, session)
        save_session_to_db(updated_session)

        return result

    except Exception as e:
        print(f"[Agent Error]: {repr(e)}", flush=True)
        traceback.print_exc()
        fallback_msg = (
            "Не удалось обработать запрос в данный момент. Пожалуйста, уточните направление, даты или ориентировочный бюджет."
            if (locals().get("lang") == "ru")
            else "Unable to process the request at this moment. Please clarify your destination, preferred dates, or total budget."
        )
        return {
            "reply": fallback_msg,
            "state": "INCOMPLETE",
            "status": "INCOMPLETE",
            "missing_fields": ["country", "date_start", "budget_kzt"],
            "results": [],
            "prompts": build_seasonal_prompts(is_russian=(locals().get("lang") == "ru")),
            "slots": {},
        }
