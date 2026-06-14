"""Работа с Supabase — пользователи, вызовы, чек-ины."""

from __future__ import annotations

import datetime as dt
from typing import Any

from supabase import create_client, Client

from config import SUPABASE_URL, SUPABASE_KEY, CHALLENGE_DAYS


_client: Client | None = None


def get_db() -> Client:
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


# ─── Пользователи ───────────────────────────────────────────────

def get_user(tg_id: int) -> dict | None:
    """Найти пользователя по Telegram ID."""
    resp = get_db().table("users").select("*").eq("tg_id", tg_id).maybe_single().execute()
    return resp.data


def create_user(
    tg_id: int,
    username: str | None,
    first_name: str | None,
) -> dict:
    """Создать нового пользователя."""
    data = {
        "tg_id": tg_id,
        "username": username or "",
        "first_name": first_name or "",
        "state": "new",
    }
    resp = get_db().table("users").insert(data).execute()
    return resp.data[0]


def update_user(tg_id: int, **fields: Any) -> dict | None:
    """Обновить поля пользователя."""
    resp = get_db().table("users").update(fields).eq("tg_id", tg_id).execute()
    return resp.data[0] if resp.data else None


# ─── Слабости ────────────────────────────────────────────────────

def set_weaknesses(tg_id: int, weakness_ids: list[str]) -> None:
    """Сохранить выбранные слабости пользователя."""
    # Удалить старые
    get_db().table("user_weaknesses").delete().eq("tg_id", tg_id).execute()
    # Вставить новые
    rows = [{"tg_id": tg_id, "weakness_id": w} for w in weakness_ids]
    if rows:
        get_db().table("user_weaknesses").insert(rows).execute()


def get_weaknesses(tg_id: int) -> list[str]:
    """Получить ID слабостей пользователя."""
    resp = get_db().table("user_weaknesses").select("weakness_id").eq("tg_id", tg_id).execute()
    return [r["weakness_id"] for r in resp.data]


# ─── Вызов (30 дней) ────────────────────────────────────────────

def start_challenge(tg_id: int) -> dict:
    """Создать 30-дневный вызов."""
    now = dt.datetime.now(dt.timezone.utc)
    end = now + dt.timedelta(days=CHALLENGE_DAYS)
    data = {
        "tg_id": tg_id,
        "started_at": now.isoformat(),
        "ends_at": end.isoformat(),
        "day": 1,
        "streak": 0,
        "total_checkins": 0,
        "total_fails": 0,
        "active": True,
    }
    resp = get_db().table("challenges").insert(data).execute()
    return resp.data[0]


def get_active_challenge(tg_id: int) -> dict | None:
    """Найти активный вызов пользователя."""
    resp = (
        get_db()
        .table("challenges")
        .select("*")
        .eq("tg_id", tg_id)
        .eq("active", True)
        .order("started_at", desc=True)
        .limit(1)
        .maybe_single()
        .execute()
    )
    return resp.data


def update_challenge(challenge_id: str, **fields: Any) -> dict | None:
    """Обновить вызов."""
    resp = get_db().table("challenges").update(fields).eq("id", challenge_id).execute()
    return resp.data[0] if resp.data else None


# ─── Чек-ины ─────────────────────────────────────────────────────

def add_checkin(
    tg_id: int,
    challenge_id: str,
    day: int,
    passed: bool,
    weaknesses_held: list[str] | None = None,
    note: str = "",
) -> dict:
    """Записать дневной чек-ин."""
    data = {
        "tg_id": tg_id,
        "challenge_id": challenge_id,
        "day": day,
        "passed": passed,
        "weaknesses_held": weaknesses_held or [],
        "note": note,
        "checked_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    resp = get_db().table("checkins").insert(data).execute()
    return resp.data[0]


def get_checkins(challenge_id: str) -> list[dict]:
    """Все чек-ины за вызов."""
    resp = (
        get_db()
        .table("checkins")
        .select("*")
        .eq("challenge_id", challenge_id)
        .order("day")
        .execute()
    )
    return resp.data


def has_checkin_today(tg_id: int, challenge_id: str) -> bool:
    """Был ли уже чек-ин сегодня?"""
    today = dt.date.today().isoformat()
    resp = (
        get_db()
        .table("checkins")
        .select("id")
        .eq("tg_id", tg_id)
        .eq("challenge_id", challenge_id)
        .gte("checked_at", today + "T00:00:00Z")
        .lte("checked_at", today + "T23:59:59Z")
        .limit(1)
        .execute()
    )
    return len(resp.data) > 0


# ─── Аватар ──────────────────────────────────────────────────────

def save_avatar_url(tg_id: int, url: str) -> None:
    """Сохранить URL пиксельного аватара."""
    update_user(tg_id, avatar_url=url)


def upload_photo_to_storage(tg_id: int, photo_bytes: bytes, filename: str) -> str:
    """Загрузить фото в Supabase Storage, вернуть публичный URL."""
    path = f"photos/{tg_id}/{filename}"
    get_db().storage.from_("assets").upload(
        path,
        photo_bytes,
        file_options={"content-type": "image/jpeg", "upsert": "true"},
    )
    return get_db().storage.from_("assets").get_public_url(path)
